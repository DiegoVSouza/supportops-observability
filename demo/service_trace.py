"""Real loopback HTTP -> SQS/P04 worker -> installed P01 -> PostgreSQL demo."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import time
from urllib.request import Request, urlopen
from uuid import uuid4

import boto3
import psycopg
from opentelemetry import propagate, trace
from prometheus_client import generate_latest
from supportops_agents import get_runner
from supportops_agents.contracts import Ticket
from supportops_agents.fakes import FakeLLMClient
from supportops_async.store.postgres import PostgresTaskStore
from supportops_async.queue.memory import SqsBroker
from supportops_async.queue.contracts import BrokerMessage
from supportops_async.worker import Worker
from supportops_obs import (setup_telemetry,flush_telemetry,LLMResponse,record_llm_call,
                           record_agent_execution,metrics_registry,traced_tool,traced_operation,
                           LoopDetector,StepRecord)


def run():
    setup_telemetry("p03-service-incidents",otlp_endpoint=os.getenv("P03_OTLP_ENDPOINT","http://127.0.0.1:24317"))
    dsn=os.getenv("P03_POSTGRES_DSN","postgresql://supportops:supportops@127.0.0.1:37432/supportops")
    store=PostgresTaskStore(dsn)
    client=boto3.client("sqs",endpoint_url=os.getenv("P03_LOCALSTACK_ENDPOINT","http://127.0.0.1:34566"),region_name="us-east-1",aws_access_key_id="test",aws_secret_access_key="test")
    suffix=uuid4().hex
    main=client.create_queue(QueueName="p03-incidents-"+suffix)["QueueUrl"]
    dead=client.create_queue(QueueName="p03-incidents-dlq-"+suffix)["QueueUrl"]
    broker=SqsBroker(client,main,dead)
    tracer=trace.get_tracer("p03.service")
    traces=[]

    class API(BaseHTTPRequestHandler):
        def do_POST(self):
            incident=json.loads(self.rfile.read(int(self.headers["Content-Length"])))['incident']
            with tracer.start_as_current_span("api.request") as root:
                root.set_attribute("supportops.synthetic",True)
                root.set_attribute("supportops.incident",incident)
                with tracer.start_as_current_span("queue.publish"):
                    carrier={}
                    propagate.inject(carrier)
                    task,_=store.create({"steps":["triage"],"incident":incident,"carrier":carrier},uuid4().hex)
                    broker.publish(BrokerMessage(task.task_id))
                response=json.dumps({"task_id":task.task_id,"trace_id":format(root.get_span_context().trace_id,"032x")}).encode()
            self.send_response(202);self.end_headers();self.wfile.write(response)
        def log_message(self,*args): pass

    @traced_operation("database","incident.lookup")
    def lookup():
        with psycopg.connect(dsn) as conn: return conn.execute("SELECT 1").fetchone()[0]

    @traced_tool("incident.lookup")
    def tool(incident):
        if incident=="slow_tool": time.sleep(.2)
        return lookup()

    class Client:
        def __init__(self,incident): self.incident=incident;self.fake=FakeLLMClient()
        def complete(self,agent,payload):
            with tracer.start_as_current_span("llm.fake"):
                if agent=="kb_researcher": tool(self.incident)
                record_llm_call(LLMResponse("fake","incident-fixture",10,5,8.75 if self.incident=="cost_spike" else 0,6 if self.incident=="slow_tool" else .01))
                return self.fake.complete(agent,payload)

    def runner(payload,step):
        with tracer.start_as_current_span("worker.run",context=propagate.extract(payload["carrier"])):
            with tracer.start_as_current_span("agent.triage"):
                result=get_runner("core").run(Ticket(id=uuid4().hex,subject="Invoice",description="Billing question",customer_id="synthetic"),llm=Client(payload["incident"]))
                if payload["incident"]=="agent_loop":
                    detector=LoopDetector(repeat_threshold=3)
                    for _ in range(4): signal=detector.observe(StepRecord(tool="search",arguments={"fixture":True},state="same"))
                    assert signal.detected
                record_agent_execution(steps=len(result.trace),success=True,task_type="triage")
                return {"stop_reason":result.stop_reason,"synthetic":True}

    server=ThreadingHTTPServer(("127.0.0.1",0),API)
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        for incident in ("slow_tool","agent_loop","cost_spike"):
            req=Request(f"http://127.0.0.1:{server.server_port}/tasks",json.dumps({"incident":incident}).encode(),headers={"Content-Type":"application/json"})
            with urlopen(req,timeout=10) as response: submitted=json.load(response)
            assert Worker(store,broker,runner=runner).run_once()
            assert store.get(submitted["task_id"]).status.value=="done"
            traces.append({"incident":incident,**submitted})
        assert flush_telemetry()
        return {"synthetic":True,"p01":"0.1.1","p04":"0.1.3","traces":traces,
                "metrics":generate_latest(metrics_registry()).decode()}
    finally:
        server.shutdown();server.server_close();thread.join(timeout=2)
        client.delete_queue(QueueUrl=main);client.delete_queue(QueueUrl=dead)


if __name__=="__main__":
    from pathlib import Path
    output=run()
    Path("artifacts/evidence/phase-009-service-traces.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"traces":output["traces"],"synthetic":True}))
