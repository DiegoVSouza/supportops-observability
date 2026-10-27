"""Execute local service requirements; dependency absence is never a green gate."""

import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import Request,urlopen
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]
def fetch(url,auth=None):
    headers={}
    if auth: headers['Authorization']='Basic '+base64.b64encode(auth.encode()).decode()
    try:
        with urlopen(Request(url,headers=headers),timeout=5) as response: return json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f'HTTP {exc.code} from {url}') from exc

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
