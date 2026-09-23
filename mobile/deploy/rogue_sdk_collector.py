"""
Rogue analytics SDK collector — #14 "The Passenger"

A fake third-party analytics service that collects device identifiers and
other telemetry, unbeknown to the app's developers. Runs on a different host:port
than the main backend, so it reads as a distinct third-party service in a proxy capture.

Run alongside app.py on a different port:
    python rogue_sdk_collector.py --port 9090

REDESIGNED 2026-09-11 (docs/CHALLENGE-AUDIT-2026-09-11.md #14): the flag used
to be a 5-byte XOR literal in PassengerActivity.kt — findable with jadx, no
device, no proxy, no collector. It has been deleted client-side. The flag now
only exists in this response body, so the player must actually capture live
traffic to a host that is not the app's own backend and read what comes back,
not just what the SDK sends.

The response is shaped like a real telemetry ack (status + a fake ingest id)
so it does not read as "the flag delivery endpoint" to a player skimming a
proxy log; the flag sits in a field named like ordinary ack metadata.
"""

import json
import os
import sys
import argparse
import secrets
from flask import Flask, request, jsonify

# tools/check_no_flag_leaks.py fails any tracked file outside secrets/ that
# contains a real flag literal -- loaded at runtime instead, same pattern as
# CHALLENGE_FLAGS in app.py.
_FLAGS_PATH = os.environ.get(
    "CTF_FLAGS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "secrets", "flags.json")
)
try:
    with open(_FLAGS_PATH, encoding="utf-8") as _fh:
        FLAG_14 = json.load(_fh)["14"]["flag"]
except (OSError, ValueError, KeyError) as _exc:
    print(f"[FATAL] cannot load flag #14 from {_FLAGS_PATH}: {_exc}", file=sys.stderr)
    raise

app = Flask(__name__)

REQUIRED_FIELDS = ("device_id", "install_id", "event")


@app.route("/collect", methods=["POST"])
def collect():
    """
    Accept telemetry payload from the SDK. A well-formed payload (the shape
    MetricFlowKit actually sends: device_id, install_id, event) gets an
    ack that carries the flag in "sync_token" — a field name that reads as
    ordinary telemetry plumbing, not as a flag. A malformed or empty POST
    gets a plain ack with no sync_token, so probing the endpoint with an
    empty body teaches nothing.
    """
    payload = request.get_json(silent=True) or {}
    print(f"Received telemetry: {json.dumps(payload, indent=2)[:500]}")

    well_formed = all(isinstance(payload.get(field), str) and payload.get(field) for field in REQUIRED_FIELDS)

    ack = {
        "status": "ack",
        "ingest_id": secrets.token_hex(8),
    }
    if well_formed:
        ack["sync_token"] = FLAG_14

    return jsonify(ack), 200

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rogue SDK Collector")
    parser.add_argument("--port", type=int, default=9090, help="Port to listen on")
    args = parser.parse_args()

    print(f"Starting rogue SDK collector on 0.0.0.0:{args.port}")
    print("This collector is intentionally unsecured and designed for educational purposes.")
    app.run(host="0.0.0.0", port=args.port, debug=False, use_reloader=False)
