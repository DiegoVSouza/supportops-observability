from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Lock

lock = Lock()
count = 0

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global count
        if self.path != "/metrics":
            self.send_error(404)
            return
        with lock:
            count += 1
            n = count
        body = "\n".join([
            "# TYPE supportops_agent_loop_signals_total counter",
            f'supportops_agent_loop_signals_total{{task_type="triage",synthetic="true"}} {n}',
            "# TYPE supportops_llm_cost_usd_total counter",
            f'supportops_llm_cost_usd_total{{synthetic="true"}} {n}',
            "# TYPE supportops_llm_calls_total counter",
            f'supportops_llm_calls_total{{outcome="error",synthetic="true"}} {n}',
            f'supportops_llm_calls_total{{outcome="success",synthetic="true"}} 0',
            "# TYPE supportops_llm_latency_seconds_bucket counter",
            f'supportops_llm_latency_seconds_bucket{{le="5",synthetic="true"}} 0',
            f'supportops_llm_latency_seconds_bucket{{le="10",synthetic="true"}} {n}',
            f'supportops_llm_latency_seconds_bucket{{le="+Inf",synthetic="true"}} {n}',
            "# TYPE supportops_llm_latency_seconds_count counter",
            f'supportops_llm_latency_seconds_count{{synthetic="true"}} {n}',
            "# TYPE supportops_llm_latency_seconds_sum counter",
            f'supportops_llm_latency_seconds_sum{{synthetic="true"}} {n * 6}',
            "",
        ]).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, fmt, *args):
        pass

print("synthetic metrics exporter listening on 0.0.0.0:8000; all series carry synthetic=true", flush=True)
HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
