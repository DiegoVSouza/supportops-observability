# P03 Phase 002 Verification Plan

## Unit and contract

- Test that initialization remains stable after setup calls and that flush/shutdown exports pending data deterministically.
- Test privacy defaults, correlation IDs, task-type success, retries, errors, and cost metrics with bounded-cardinality labels.
- Test alert name/expression semantics and representative alert series.
- Test that the full gate returns nonzero and reports `INCOMPLETE` if a required gate (including promtool validation) did not run.

## Package integration

- Generate and inspect a deterministic trace through API, queue, worker, agent, LLM boundary, tool, and database using fake/replay mode. Verify shared trace/correlation identity and absence of sensitive content by default.
- Run `python -m pytest -q` and `python scripts/check_full.py`; save command, exit code, and output.

## Configuration and service integration

- Run `promtool check rules alerts/observability.yml` when installed; exercise alert fixtures with the available rule tester.
- Validate Compose configuration and run the stack, provisioned dashboard, and incident scenarios when Docker services are available. Static YAML parsing is not E2E evidence.
- If a required validator/stack did not execute, classify it INCOMPLETE and verify full gate exit is nonzero.

## E2E and agent evaluation

- Fake demo and integrated local stack trace are separate gates. Synthetic incident data is explicitly labeled synthetic.
- There is no agent evaluation requirement unless a real P01 runner/model path is added; model-quality and production metrics remain `PENDING` absent eligible runs.

## Evidence review

Store all command outputs and exit codes under `artifacts/evidence/`. Report PASS only for executed gates with output; report unavailable service gates as INCOMPLETE and absent production/replay metrics as PENDING.
