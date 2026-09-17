# Follow Me

The service accepts one tar member named `report.txt`. It checks the member's
name and size, extracts it, then reads the resulting path.

The missing check is the member type and link target. A symbolic link named
`report.txt` that points to `/flag.txt` passes validation, and `read_text()`
follows it.

Run locally:

```bash
docker compose up --build
python3 solver.py 127.0.0.1 9044
```
