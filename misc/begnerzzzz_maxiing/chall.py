#!/usr/bin/env python3

import base64
import hashlib
import hmac
import os
from pathlib import Path
import pwd
import re
import secrets
import subprocess
import sys

from detector import BadSource, Detector


ROOT = Path(__file__).resolve().parent


def become_ctf():
    if os.geteuid() != 0:
        return
    account = pwd.getpwnam("ctf")
    os.setgroups([])
    os.setgid(account.pw_gid)
    os.setuid(account.pw_uid)


def seal(nonce, receipt):
    key = secrets.token_bytes(32)
    stream = hashlib.sha256(nonce.encode() + key).digest()
    ciphertext = bytes(a ^ b for a, b in zip(receipt, stream))
    shards = []
    for index in range(4):
        body = bytes([index]) + key[index * 8:index * 8 + 8]
        tag = hashlib.sha256(nonce.encode() + body + b"MAX").digest()[:4]
        shards.append(base64.urlsafe_b64encode(body + tag).rstrip(b"="))
    return ciphertext, b",".join(shards)


def main():
    flag = (ROOT / "flag.txt").read_text().strip()
    nonce = secrets.token_hex(8)
    detector = Detector()

    print("BEGNERZZZZ MAXIING")
    print(f"session nonce: {nonce}")
    print(f"source limit: {detector.max_source} bytes")
    print("send Exploit.java as one base64 line")
    print("source> ", end="", flush=True)

    line = sys.stdin.buffer.readline(30_000)
    if not line.endswith(b"\n") or len(line) >= 30_000:
        print("bad upload")
        return
    try:
        source = base64.b64decode(line.strip(), validate=True)
        score, probability, verdict = detector.classify(nonce, source)
    except (ValueError, BadSource):
        print("bad source")
        return

    print(f"AI probability: {probability:.12f}")
    print(f"verdict: {verdict}")
    if verdict != "HUMAN":
        return

    receipt = secrets.token_bytes(24)
    expected = hashlib.sha256(nonce.encode() + receipt).hexdigest()
    ciphertext, shards = seal(nonce, receipt)
    payload = b"\n".join([
        nonce.encode(),
        base64.b64encode(ciphertext),
        shards,
        base64.b64encode(source),
    ]) + b"\n"

    command = [
        "java", "-Xms32m", "-Xmx192m", "-Djava.io.tmpdir=/tmp",
        "--add-exports=java.base/jdk.internal.reflect=ALL-UNNAMED",
        "--add-opens=java.base/java.lang=ALL-UNNAMED",
        "-cp", str(ROOT), "Main",
    ]
    try:
        child = subprocess.run(
            command, input=payload, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, timeout=20, cwd=ROOT,
            env={"PATH": os.environ.get("PATH", "/opt/java/openjdk/bin:/usr/bin")},
            preexec_fn=become_ctf,
        )
    except subprocess.TimeoutExpired:
        print("sandbox: timeout")
        return
    except Exception:
        print("sandbox: failed")
        return

    output = child.stdout.decode("ascii", "replace")[:4096]
    match = re.search(r"^RESULT:([0-9a-f]{64})$", output, re.MULTILINE)
    if not match or not hmac.compare_digest(match.group(1), expected):
        status = output.strip().splitlines()[-1] if output.strip() else "no proof"
        print(f"sandbox: {status[:120]}")
        return
    print(flag)


if __name__ == "__main__":
    main()
