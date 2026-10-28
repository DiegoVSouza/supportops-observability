"""Execute local service requirements; dependency absence is never a green gate."""

import base64
from http.client import RemoteDisconnected
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import Request,urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]

READ_RETRY_ATTEMPTS=5
READ_RETRY_DELAYS=(0.25,0.5,1.0,2.0)


def _read_endpoint_class(url):
    path=urlsplit(url).path
    if path=="/api/services": return "jaeger.services"
    if path.startswith("/api/traces/"): return "jaeger.trace"
    if path.startswith("/api/search"): return "grafana.search"
    if path=="/api/v1/alerts": return "prometheus.alerts"
    return "observability.other"


def _is_transient_read_error(exc):
    transport_errors=(RemoteDisconnected,ConnectionError,TimeoutError,socket.timeout)
    if isinstance(exc,transport_errors):
        return True
    return isinstance(exc,URLError) and isinstance(exc.reason,transport_errors)


def fetch(url,auth=None):
    headers={}
    if auth: headers['Authorization']='Basic '+base64.b64encode(auth.encode()).decode()
    request=Request(url,headers=headers)
    endpoint=_read_endpoint_class(url)
    for attempt in range(READ_RETRY_ATTEMPTS):
        try:
            with urlopen(request,timeout=5) as response: return json.load(response)
        except HTTPError as exc:
            raise RuntimeError(f'HTTP {exc.code} from {endpoint}') from exc
        except (RemoteDisconnected,ConnectionError,TimeoutError,socket.timeout,URLError) as exc:
            if not _is_transient_read_error(exc) or attempt+1>=READ_RETRY_ATTEMPTS:
                raise RuntimeError(
                    f'{type(exc).__name__} from {endpoint} after {attempt+1} attempts'
                ) from exc
            time.sleep(READ_RETRY_DELAYS[attempt])

def main():
    try:
        evidence_root=(ROOT/'artifacts'/'evidence').resolve()
        evidence_dir=(ROOT/os.getenv('P03_SERVICE_EVIDENCE_DIR','artifacts/evidence')).resolve()
        if not evidence_dir.is_relative_to(evidence_root):
            raise ValueError('P03_SERVICE_EVIDENCE_DIR must be inside artifacts/evidence')
        evidence_dir.mkdir(parents=True,exist_ok=True)
        project=os.getenv('P03_COMPOSE_PROJECT','p03-remediation')
        compose=['docker','compose','-p',project,'-f','stack/docker-compose.obs.yml','-f','artifacts/evidence/phase-008-compose.override.yml','-f','stack/docker-compose.integration.yml']
        result=subprocess.run(compose+['up','-d','--wait'],cwd=ROOT,capture_output=True,text=True)
        print('Command: '+' '.join(compose+['up','-d','--wait'])+'\nExit code: '+str(result.returncode))
        print(result.stdout+result.stderr)
        if result.returncode: return 2
        jaeger=os.getenv('P03_JAEGER_URL','http://127.0.0.1:24686')
        fetch(jaeger+'/api/services')
        run=subprocess.run([sys.executable,'demo/service_trace.py'],cwd=ROOT,capture_output=True,text=True)
        print('Command: '+sys.executable+' demo/service_trace.py\nExit code: '+str(run.returncode))
        print(run.stdout+run.stderr)
        if run.returncode: return 1
        traces=json.loads((evidence_dir/'phase-009-service-traces.json').read_text())
        exported=[]
        for item in traces['traces']:
            deadline=time.monotonic()+30
            while True:
                try:
                    found=fetch(jaeger+'/api/traces/'+item['trace_id'])['data']
                except HTTPError as exc:
                    if exc.code != 404: raise
                    found=[]
                if found: break
                if time.monotonic()>deadline: raise RuntimeError('exported incident trace missing')
                time.sleep(.5)
            names={s['operationName'] for s in found[0]['spans']}
            required={'api.request','queue.publish','worker.run','agent.triage','llm.fake','tool.incident.lookup','database.incident.lookup'}
            if not required<=names: raise RuntimeError('trace lacks required service stages: '+str(required-names))
            exported.extend(found)
        (evidence_dir/'phase-009-jaeger-export.json').write_text(json.dumps(exported,indent=2)+'\n')
        dashboard=fetch('http://127.0.0.1:23000/api/search?query=SupportOps',os.getenv('P03_GRAFANA_AUTH','admin:admin'))
        assert any(row['type']=='dash-db' for row in dashboard)
        deadline=time.monotonic()+int(os.getenv('P03_ALERT_TIMEOUT_S','600'))
        while True:
            alerts=fetch('http://127.0.0.1:29090/api/v1/alerts')
            fired={a['labels']['alertname'] for a in alerts['data']['alerts'] if a['state']=='firing'}
            if {'AgentLoopDetected','LLMCostAnomaly','AgentErrorRateHigh','LLMp95LatencyHigh'}<=fired: break
            if time.monotonic()>deadline: raise RuntimeError('required synthetic alerts did not fire')
            time.sleep(5)
        (evidence_dir/'phase-009-live-alerts.json').write_text(json.dumps(alerts,indent=2)+'\n')
        print('service-integration: PASS; real HTTP/SQS/P04/P01/PostgreSQL trace; three synthetic incidents; dashboard; four live synthetic alerts')
        return 0
    except Exception as exc:
        print('service-integration: INCOMPLETE; '+type(exc).__name__+': '+str(exc))
        return 2

if __name__=='__main__': raise SystemExit(main())
