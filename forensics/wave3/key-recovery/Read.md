# Key Recovery

A sync agent on a workstation uploaded a confidential export to an outside host over TLS 1.3.
We captured the traffic, but it's encrypted end to end. Before the process was killed we
grabbed a dump of it.

Recover what was uploaded.

Files:
- `traffic.pcapng` — the captured network traffic (TLS 1.3)
- `agent.core`     — a process memory dump of the sync agent
