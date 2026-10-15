# Incident: agent loop

1. Follow the `AgentLoopDetected` alert to the incident window.
2. In the trace, inspect consecutive `tool.*` spans and compare tool name plus normalized arguments; check state attributes if provided by the runner.
3. Confirm whether the detector reason is `repeated_tool_arguments`, `state_cycle`, or `step_limit` before terminating the run.
4. Preserve trace IDs and loop history; change the caller's termination policy only after confirming the repeated path.

The committed fixture is synthetic. A real exported trace and screenshot are PENDING.
