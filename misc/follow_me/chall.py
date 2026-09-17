#!/usr/bin/env python3

import base64
import io
from pathlib import Path
import sys
import tarfile
import tempfile


MAX_INPUT = 100_000

print("FOLLOW ME")
print("Send a base64 tar archive containing report.txt.")
print("archive> ", end="", flush=True)

try:
    line = sys.stdin.buffer.readline(MAX_INPUT + 2).strip()
    if len(line) > MAX_INPUT:
        raise ValueError

    data = base64.b64decode(line, validate=True)
    if len(data) > 65_536:
        raise ValueError

    with tempfile.TemporaryDirectory() as folder:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            members = archive.getmembers()
            if len(members) != 1 or members[0].name != "report.txt":
                raise ValueError
            if members[0].size > 4096:
                raise ValueError
            archive.extractall(folder, filter="fully_trusted")

        report = (Path(folder) / "report.txt").read_text(errors="replace")
except Exception:
    print("Invalid archive.")
    raise SystemExit

print("Report:")
print(report)
