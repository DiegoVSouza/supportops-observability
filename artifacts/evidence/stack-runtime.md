# Local stack runtime availability

Date: 2026-10-15; command executed from the P03 repository.

| Command | Exit | Output | Status |
|---|---:|---|---|
| `docker info --format '{{.ServerVersion}}'` | 1 | `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.` | Live stack E2E INCOMPLETE; Docker CLI exists, local daemon does not run. |
| `docker compose -f stack/docker-compose.obs.yml config --quiet` | 0 | no output | Compose configuration parsed successfully; this is not a running-stack test. See `check-full.txt`. |
| `promtool check rules alerts/observability.yml` | 127 | `INCOMPLETE: promtool unavailable` | Alert rule syntax gate INCOMPLETE. See `check-full.txt`. |

No external deployment or paid LLM call was made.
