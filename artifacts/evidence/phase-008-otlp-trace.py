from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider(resource=Resource.create({"service.name": "p03-phase-008-synthetic"}))
exporter = OTLPSpanExporter(endpoint="http://127.0.0.1:24317", insecure=True)
provider.add_span_processor(SimpleSpanProcessor(exporter))
tracer = provider.get_tracer("p03.phase008")
with tracer.start_as_current_span("api.request", attributes={"supportops.synthetic": True}) as root:
    trace_id = format(root.get_span_context().trace_id, "032x")
    with tracer.start_as_current_span("queue.publish", attributes={"supportops.synthetic": True}):
        with tracer.start_as_current_span("worker.run", attributes={"supportops.synthetic": True}):
            with tracer.start_as_current_span("agent.triage", attributes={"supportops.synthetic": True}):
                with tracer.start_as_current_span("llm.fake", attributes={"supportops.synthetic": True, "llm.mode": "fake"}):
                    with tracer.start_as_current_span("tool.lookup", attributes={"supportops.synthetic": True}):
                        with tracer.start_as_current_span("database.lookup", attributes={"supportops.synthetic": True}):
                            pass
print(f"synthetic OTLP trace exported; service=p03-phase-008-synthetic trace_id={trace_id} spans=7")
print("attributes include supportops.synthetic=true; no ticket/customer content was emitted")
print("export_result=flush")
provider.force_flush()
provider.shutdown()
