#!/usr/bin/env python3
"""
Deliberately-insecure Flask backend for Securinets CTF.
Designed for live MITM-proxy and certificate pinning exercises.

Endpoints, each teaching a specific mobile security bug:
1. /login — plain HTTP session_note is sniffable (party_line_was_never_encrypted)
2. /profile/<id> — IDOR vulnerability, no ownership check (f4c9a2e7-b81d-4f3a-9c6e-2b7d5a1f8e3c)
3. /audit — requires cert pinning to intercept (sealed_envelope_pin_bypassed)
4. /admin/report — HS256 signature IS verified; the secret is crackable (forged_papers_grant_admin)
5. /activate — #1 NomadVpn: server-verified credential check (sh1pp3d_1n_th3_0p3n)

/login, /profile and /audit also require an X-Sig HMAC header — see the
per-endpoint docstrings and docs/CHALLENGE-AUDIT-2026-09-11.md for the exact
construction and why it differs by endpoint.
"""

import sys
import os
import json
import hashlib
import hmac
import secrets
import sqlite3
import time
import argparse
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify

app = Flask(__name__)

DEBRIEFS_PATH = os.environ.get(
    "CTF_DEBRIEFS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "debriefs.json")
)

try:
    with open(DEBRIEFS_PATH, encoding="utf-8") as fh:
        DEBRIEFS = json.load(fh)
except (OSError, ValueError) as exc:
    print(f"[FATAL] cannot load debriefs from {DEBRIEFS_PATH}: {exc}", file=sys.stderr)
    raise

# Was "dev-secret-change-me" — not in rockyou.txt, which made the #12 redesign
# (crack the HS256 secret, forge an admin token) silently unsolvable. Verified
# present in rockyou.txt at line 3904; see docs/CHALLENGE-AUDIT-2026-09-11.md #12.
JWT_SECRET = "changeme"
JWT_ALGORITHM = "HS256"

# Shared HMAC key for the X-Sig request-signing scheme (#9/#10/#11). 32 bytes,
# committed default so the repo is self-contained; override in prod via env.
# The Android native `sign()` must use this exact key — see backend/README.md
# for the per-endpoint HMAC construction.
SIG_KEY = bytes.fromhex(os.environ.get(
    "CTF_SIG_KEY",
    "8500481f4455316520166c746e90718d7fe2f0c6832b055b0956a0896a218e75",
))

# Designer mode: env/argv only, never request-controlled. Disables X-Sig
# checking so the API stays testable with plain curl during development.
SIG_DISABLED = os.environ.get("CTF_SIG_DISABLED") == "1"

# Every 401 body below is deliberately identical *within one endpoint* — a
# signature failure must read exactly like a credentials/token failure, or
# the failure reason itself becomes an oracle (see docs/CHALLENGE-AUDIT
# #9's Task 1: "Missing or bad signature -> 401, byte-identical to every
# other 401 the endpoint can return").
LOGIN_401 = {"error": "Invalid credentials"}
AUTH_401 = {"error": "Unauthorized"}

# RT-02a: the app used to ship sha256(flag) for all 16 challenges and compare
# locally (ProgressStore.submitFlag) -- a free offline oracle for every guess
# against every challenge, including the ones still being hardened per
# docs/HARDENING-PLAN-2026-09-15.md. That hash registry is gone from the app;
# this table is the only place a submitted flag is checked against now. It
# exists so the in-app "captured" UI (debrief unlock, chained-challenge
# unlock) can confirm a real flag -- CTFd remains the actual scoreboard.
#
# Loaded at runtime from secrets/flags.json, same pattern as DEBRIEFS_PATH
# above -- never a literal in this file. tools/check_no_flag_leaks.py treats
# any tracked file outside secrets/ as a leak if it contains a real flag, and
# app.py is tracked, so the flags themselves cannot live here even though the
# lookup logic does.
CHALLENGE_FLAGS_PATH = os.environ.get(
    "CTF_FLAGS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "secrets", "flags.json")
)

try:
    with open(CHALLENGE_FLAGS_PATH, encoding="utf-8") as fh:
        _raw_flags = json.load(fh)
    CHALLENGE_FLAGS = {int(k): v["flag"] for k, v in _raw_flags.items() if k.isdigit()}
except (OSError, ValueError, KeyError) as exc:
    print(f"[FATAL] cannot load flags from {CHALLENGE_FLAGS_PATH}: {exc}", file=sys.stderr)
    raise

VERIFY_400 = {"error": "id and flag required"}

# Hardening plan step 1 (docs/HARDENING-PLAN-2026-09-15.md): a per-session
# value minted when a challenge screen starts, never present in the APK.
# Single Flask process, single dict -- matches the existing style
# (SEED_USERS, CHALLENGE_FLAGS are plain dicts too). A live event runs this
# as one process for a few hours; nothing here needs to survive a restart.
# Not gated on X-Sig -- see the plan's own ruling that X-Sig is already
# forged and adds nothing.
SESSIONS: dict[str, dict] = {}
SESSION_TTL_SECONDS = 6 * 60 * 60


def _new_session(**fields) -> str:
    session_id = secrets.token_hex(16)
    SESSIONS[session_id] = {"created_at": time.time(), **fields}
    return session_id


def _session(session_id: str) -> dict | None:
    entry = SESSIONS.get(session_id)
    if entry is None:
        return None
    if time.time() - entry["created_at"] > SESSION_TTL_SECONDS:
        del SESSIONS[session_id]
        return None
    return entry


def _hmac_hex(key: bytes, message: bytes) -> str:
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def _check_sig(expected_message: bytes) -> bool:
    """Compare X-Sig header against HMAC-SHA256(SIG_KEY, expected_message)."""
    if SIG_DISABLED:
        return True
    provided = request.headers.get("X-Sig", "")
    if not provided:
        return False
    expected = _hmac_hex(SIG_KEY, expected_message)
    return hmac.compare_digest(provided.strip().lower(), expected)

SEED_USERS = {
    1: {"username": "alice", "password": "alice123", "name": "Alice Johnson", "email": "alice@example.com", "internal_ref": "REF-2024-88201"},
    2: {"username": "bob", "password": "bob456", "name": "Bob Smith", "email": "bob@example.com", "internal_ref": "a3f9c210e7"},
    3: {"username": "charlie", "password": "charlie789", "name": "Charlie Brown", "email": "charlie@example.com", "internal_ref": "REF-2024-88202"},
    4: {"username": "diana", "password": "diana999", "name": "Diana Prince", "email": "diana@example.com", "internal_ref": CHALLENGE_FLAGS[10]},
    5: {"username": "eve", "password": "eve111", "name": "Eve Wilson", "email": "eve@example.com", "internal_ref": "REF-2024-88203"},
    6: {"username": "player", "password": "player123", "name": "Player Account", "email": "player@example.com", "internal_ref": "REF-2024-88204"},
    7: {"username": "frank", "password": "frank222", "name": "Frank Miller", "email": "frank@example.com", "internal_ref": "b7d4e2f1a9"},
    8: {"username": "grace", "password": "grace333", "name": "Grace Lee", "email": "grace@example.com", "internal_ref": "REF-2024-88205"},
    9: {"username": "henry", "password": "henry444", "name": "Henry Taylor", "email": "henry@example.com", "internal_ref": "c2e8f5b1d3"},
    10: {"username": "iris", "password": "iris555", "name": "Iris Clark", "email": "iris@example.com", "internal_ref": "REF-2024-88206"},
}

def require_auth(f):
    """Decorator: require a JWT bearer token whose HS256 signature verifies
    against JWT_SECRET. This DOES verify the signature — only /admin/report
    (#12) reads a token's claims without verifying it, and that is the point
    of that challenge, not a project-wide bypass."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify(AUTH_401), 401

        token = auth_header.split(" ", 1)[1]

        try:
            jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.InvalidTokenError:
            return jsonify(AUTH_401), 401

        return f(*args, **kwargs)

    return decorated

@app.route("/health", methods=["GET"])
def health():
    """Health check, no auth required."""
    return jsonify({"status": "ok"}), 200

@app.route("/debrief", methods=["POST"])
def debrief():
    """Hand back one challenge's writeup, on proof the player captured it.

    Proof is the flag itself, checked by hash. This is not an authorisation
    boundary protecting anything secret — the player necessarily already has
    the flag — it just stops the writeups being readable by anyone who has the
    APK, which was the whole problem.

    Deliberately NOT wired into flag capture: the app's own "captured" state
    is driven by /verify, not by this endpoint. A dead network at the event
    must cost players their debriefs, never their progress.
    """
    body = request.get_json(silent=True) or {}
    cid = body.get("id")
    flag = body.get("flag")

    if not isinstance(cid, (int, str)) or not isinstance(flag, str) or not flag:
        return jsonify({"error": "id and flag required"}), 400

    entry = DEBRIEFS.get(str(cid))
    if entry is None:
        return jsonify({"error": "unknown challenge"}), 404

    submitted = hashlib.sha256(flag.strip().encode("utf-8")).hexdigest()
    if not hmac.compare_digest(submitted, entry["sha256"]):
        return jsonify({"error": "flag does not match"}), 403

    return jsonify({"id": int(cid), "debrief": entry["debrief"]}), 200

@app.route("/login", methods=["POST"])
def login():
    """
    POST /login
    Body: {"username": str, "password": str}
    Header: X-Sig: HMAC-SHA256(SIG_KEY, <raw request body bytes>), lowercase hex.
    No token exists yet at this point, so the raw body is what gets signed.

    Returns JWT with session_note containing the first flag (sniffable over plain HTTP).
    """
    if not _check_sig(request.get_data()):
        return jsonify(LOGIN_401), 401

    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user_id = None
    for uid, user in SEED_USERS.items():
        if user["username"] == username and user["password"] == password:
            user_id = uid
            break

    if user_id is None:
        return jsonify(LOGIN_401), 401

    payload = {
        "sub": str(user_id),
        "username": username,
        "role": "user",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return jsonify({
        "token": token,
        "session_note": CHALLENGE_FLAGS[9]
    }), 200

@app.route("/profile/<int:user_id>", methods=["GET"])
def profile(user_id):
    """
    GET /profile/<id>
    Requires: Authorization header with Bearer token
    Header: X-Sig: HMAC-SHA256(SIG_KEY, <bearer token string>), lowercase hex.
    The path is deliberately NOT covered by the signature, so <id> can be
    rewritten in flight without invalidating a captured signature — see
    docs/CHALLENGE-AUDIT-2026-09-11.md, "The trap in the obvious design".

    INTENTIONALLY VULNERABLE: Does NOT verify that the token's 'sub' matches <id>.
    This is IDOR (Broken Object Level Authorization / BOLA).
    A player logs in as themselves (id=6), gets a token, then requests /profile/4
    and can read another user's data (including the flag in internal_ref).
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify(AUTH_401), 401

    token = auth_header.split(" ", 1)[1]

    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return jsonify(AUTH_401), 401

    if not _check_sig(token.encode("utf-8")):
        return jsonify(AUTH_401), 401

    if user_id not in SEED_USERS:
        return jsonify({"error": "User not found"}), 404

    user = SEED_USERS[user_id]
    return jsonify({
        "id": user_id,
        "name": user["name"],
        "email": user["email"],
        "internal_ref": user["internal_ref"]
    }), 200

@app.route("/audit", methods=["GET"])
@require_auth
def audit():
    """
    GET /audit
    Requires: Authorization header with Bearer token
    Header: X-Sig: HMAC-SHA256(SIG_KEY, <bearer token string> + "/audit"),
    lowercase hex. Unlike /profile, the path IS bound into the signature here
    — otherwise a sig lifted from an intercepted /profile call would replay
    against /audit for free, skipping certificate pinning entirely. See
    docs/CHALLENGE-AUDIT-2026-09-11.md #11, "Load-bearing detail".

    Returns a flag in the 'note' field. The client-side Android app is expected
    to have certificate pinning configured; intercepting/bypassing that pinning
    is the exercise (sealed_envelope_pin_bypassed).

    The server itself has no special logic here — it just requires a valid token
    and returns the flag. The vulnerability is entirely on the client side
    (certificate pinning that a player learns to bypass).
    """
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ", 1)[1]
    if not _check_sig(token.encode("utf-8") + b"/audit"):
        return jsonify(AUTH_401), 401

    return jsonify({
        "report": "Q3 access log — 14 anomalies flagged",
        "note": CHALLENGE_FLAGS[11]
    }), 200

@app.route("/admin/report", methods=["GET"])
def admin_report():
    """
    GET /admin/report
    Requires: Authorization header with Bearer token. No X-Sig — signing this
    endpoint adds failure surface for no benefit; the lesson is forgery of a
    valid admin token, not interception (docs/CHALLENGE-AUDIT-2026-09-11.md #12).

    REDESIGNED 2026-09-11: the signature IS verified now, and role is read
    from a token that has passed verification. The intended path is: take
    your own role:"user" token, crack JWT_SECRET offline (it is a plausible
    dev leftover that is genuinely in rockyou.txt), mint a fresh HS256 token
    with role:"admin", present it here. This teaches JWT secret cracking
    (forged_papers_grant_admin), not signature-bypass — the old
    verify_signature=False version made forgery free and taught nothing.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.split(" ", 1)[1]

    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token format"}), 401

    role = decoded.get("role")

    if role == "admin":
        return jsonify({
            "report": "Full user export — 47 records",
            "flag": CHALLENGE_FLAGS[12]
        }), 200
    else:
        return jsonify({"error": "admin role required"}), 403

# #1 "Left in the Open" — NomadVpn. Username ships hardcoded and in plain
# sight in the APK (the M1 lesson: it is a hardcoded credential, not a secret
# worth hiding). Only an MD5 *hash* of the password ships client-side; the
# player cracks it (CrackStation / rockyou) to recover the plaintext, which
# this endpoint then verifies server-side.
ACTIVATE_ACCOUNT = "nomad.admin"
ACTIVATE_PASSWORD = "trustno1"  # MD5 5fcfd41e547a12215b173ff47fdd3739, confirmed in rockyou.txt
ACTIVATE_401 = {"status": "denied"}


@app.route("/activate", methods=["POST"])
def activate():
    """
    POST /activate
    Body: {"account": str, "key": str}
    No X-Sig — replay via curl is accepted and expected (see #1's ruling);
    the actual risk this endpoint guards against is a bare POST with no
    credentials returning the flag, since the URL ships in the APK strings
    and every player finds it in the first minute.

    Success 200: {"status": "active", "notice": "<flag>"}
    Failure 401: {"status": "denied"} — identical for a wrong password and an
    unknown account, so the username is never enumerable from the response.

    Never logs the submitted password or the response body — #3 is the
    logcat challenge, and leaking here would hand out a cross-challenge
    shortcut.
    """
    data = request.get_json(silent=True) or {}
    account = data.get("account")
    key = data.get("key")

    if not isinstance(account, str) or not isinstance(key, str) or not account or not key:
        return jsonify(ACTIVATE_401), 401

    valid = hmac.compare_digest(account, ACTIVATE_ACCOUNT) and hmac.compare_digest(key, ACTIVATE_PASSWORD)
    if not valid:
        return jsonify(ACTIVATE_401), 401

    return jsonify({
        "status": "active",
        "notice": CHALLENGE_FLAGS[1]
    }), 200


@app.route("/verify", methods=["POST"])
def verify():
    """
    POST /verify
    Body: {"id": int, "flag": str}

    RT-02a: this replaces the app's old local sha256(flag) compare
    (ProgressStore.submitFlag) so a guess can no longer be checked
    entirely offline against a hash shipped in the APK. This is the
    in-app "captured" confirmation only — it drives the debrief unlock
    and chained-challenge gating, not the event scoreboard. CTFd stays
    the actual scoring authority; this endpoint never awards points.

    Success 200: {"valid": true|false}
    Failure 400: {"error": "id and flag required"} — missing/malformed body.
    Unknown id: {"valid": false} — same shape as a wrong flag, not a 404,
    so the response never confirms which ids exist server-side.
    """
    data = request.get_json(silent=True) or {}
    challenge_id = data.get("id")
    submitted = data.get("flag")

    if not isinstance(challenge_id, int) or not isinstance(submitted, str) or not submitted:
        return jsonify(VERIFY_400), 400

    expected = CHALLENGE_FLAGS.get(challenge_id, "")
    valid = bool(expected) and hmac.compare_digest(submitted.strip(), expected)

    return jsonify({"valid": valid}), 200


# #5 "Front Door Trick" — the SQL injection login bypass. The app's local
# LoginGate seeds a real sqlite `users` table (guest/guest1234, admin/<random
# 24-byte hex>) and runs the exact vulnerable query below against it, so a
# player who defeats it locally really did find a working injection payload.
# What used to happen next was a local decrypt of a slot in SecureStore --
# recoverable offline with no injection at all. Now: the server seeds an
# identical table under its own session id, the app calls here with the
# literal input that produced ADMIN locally, and the server re-runs the same
# query for real. Unforgeable without an actual payload, because the server
# reproduces the injection itself rather than trusting the client's verdict.
def _frontdoor_query(username: str, password: str) -> str:
    return "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"


@app.route("/frontdoor/start", methods=["POST"])
def frontdoor_start():
    """
    POST /frontdoor/start
    No body required.

    Mints a session id and a random 24-byte-hex admin password, the same
    shape LoginGate.adminPassword() used to generate locally with
    SecureRandom. The app seeds its local `users` table with this exact
    value instead of generating its own, so the local table and the
    server's replica agree.

    Designer mode (CTF_SIG_DISABLED=1): returns a fixed password instead of
    a random one, so a tester gets the same reproducible state on every
    call instead of a different admin password per session -- standing
    constraint, see CLAUDE.md. Deliberately reuses CTF_SIG_DISABLED rather
    than a new flag; this backend only ever has the one designer switch.

    Success 200: {"session_id": str, "admin_password": str}
    """
    admin_password = (
        "11" * 24 if SIG_DISABLED else secrets.token_bytes(24).hex()
    )
    session_id = _new_session(admin_password=admin_password)
    return jsonify({"session_id": session_id, "admin_password": admin_password}), 200


@app.route("/frontdoor/verify", methods=["POST"])
def frontdoor_verify():
    """
    POST /frontdoor/verify
    Body: {"session_id": str, "username": str, "password": str}

    Re-runs the same vulnerable query against an in-memory sqlite table seeded with
    this session's admin password, exactly as the app does locally. Returns
    the flag only if an admin row comes back AND the submitted password is
    not literally the real one -- so knowing or guessing the random password
    outright does not count, only a working injection does.

    Success 200: {"valid": true, "flag": "<flag>"} or {"valid": false}
    Failure 400: {"error": "session_id, username and password required"}
    Unknown/expired session: {"valid": false} -- same shape as a failed
    attempt, not a 404, so the response never confirms a session id's status.
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    username = data.get("username")
    password = data.get("password")

    if not all(isinstance(v, str) and v for v in (session_id, username, password)):
        return jsonify({"error": "session_id, username and password required"}), 400

    entry = _session(session_id)
    if entry is None:
        return jsonify({"valid": False}), 200

    admin_password = entry["admin_password"]

    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE users (username TEXT, password TEXT, role TEXT)")
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES ('guest', 'guest1234', 'user')"
        )
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES ('admin', ?, 'admin')",
            (admin_password,),
        )

        query = _frontdoor_query(username, password)
        try:
            rows = conn.execute(query).fetchall()
        except sqlite3.Error:
            return jsonify({"valid": False}), 200
    finally:
        conn.close()

    admin_reached = any(row[2] == "admin" for row in rows)
    real_password_used = hmac.compare_digest(password, admin_password)

    valid = admin_reached and not real_password_used
    if not valid:
        return jsonify({"valid": False}), 200

    return jsonify({"valid": True, "flag": CHALLENGE_FLAGS[5]}), 200


# #3 "Loose Lips" and #4 "The Evidence Locker" — both used to log/cache a
# value pulled from SecureStore, a local decrypt with no server involved, so
# `strings`-equivalent tooling against the .so recovered it without ever
# running the app. Both endpoints below hand back a real value that only
# exists once the app asks for it live; BackupManager.run() logs the /note
# response instead of decrypting a blob, and LocalStore writes the
# /session_token response into the one real settings row instead of the rest
# of the (still-local, still-decoy) row set. No session needed -- these are
# fixed values, not per-instance secrets -- so hitting either directly with
# curl gets the value too. Accepted residual per the hardening plan: the
# cost has moved from "recoverable from the APK alone" to "must reach our
# server," which is what these two were ever meant to require.
@app.route("/backup/note", methods=["POST"])
def backup_note():
    """
    POST /backup/note
    No body required.

    Success 200: {"note": "backup: archive signed, token = <flag>"}
    """
    return jsonify({"note": f"backup: archive signed, token = {CHALLENGE_FLAGS[3]}"}), 200


@app.route("/backup/session_token", methods=["POST"])
def backup_session_token():
    """
    POST /backup/session_token
    No body required.

    Success 200: {"value": "<flag>"}
    """
    return jsonify({"value": CHALLENGE_FLAGS[4]}), 200


# #6 "Unlisted Entrance" and #8 "Face Value" -- the capability-token pattern.
# The flag no longer lives in a SecureStore slot that ships in the APK; the
# running app mints a per-session capability from the server and only a real
# redemption hands the flag back. What the app still does locally (XSS into
# the JS bridge for #6, the unbound biometric callback for #8) decides *when*
# a redemption is possible, but the token itself cannot exist offline: it
# did not exist until a live session minted it. Tokens are single-use and
# tied to the challenge they were minted for, so one redemption per session
# and no replay for a different challenge.
CAPABILITY_CHALLENGES = {6, 8}
CAPABILITY_DESIGNER_TOKEN = "designer_capability_token"


def _capability_error(message: str, status: int):
    return jsonify({"error": message}), status


@app.route("/capability/mint", methods=["POST"])
def capability_mint():
    """
    POST /capability/mint
    Body: {"challenge": int}

    Mints a single-use capability token for one challenge. The token is
    stored in the session store with its challenge and spend state; the
    flag is never part of this response.

    Success 200: {"token": "<64-hex>"}
    Failure 400: {"error": "challenge required"} -- missing/unknown id.
    """
    data = request.get_json(silent=True) or {}
    challenge = data.get("challenge")

    if challenge not in CAPABILITY_CHALLENGES:
        return _capability_error("challenge required", 400)

    token = _new_session(
        kind="capability",
        challenge=challenge,
        spent=False,
    )

    return jsonify({"token": token}), 200


@app.route("/capability/redeem", methods=["POST"])
def capability_redeem():
    """
    POST /capability/redeem
    Body: {"token": str}

    Spends a minted capability. Single-use: a spent or unknown token is
    rejected with the same shape so the response never distinguishes
    "already used" from "never existed".

    Success 200: {"flag": "<flag>"}
    Failure 400: {"error": "token required"} -- malformed body.
    Failure 403: {"error": "invalid token"} -- unknown, expired, or spent.
    """
    data = request.get_json(silent=True) or {}
    token = data.get("token")

    if not isinstance(token, str) or not token:
        return _capability_error("token required", 400)

    entry = _session(token)
    if (
        entry is None
        or entry.get("kind") != "capability"
        or entry.get("spent")
    ):
        return _capability_error("invalid token", 403)

    challenge = entry.get("challenge")
    flag = CHALLENGE_FLAGS.get(challenge, "")
    if not flag:
        return _capability_error("invalid token", 403)

    entry["spent"] = True

    return jsonify({"flag": flag}), 200


# #16 "No Caller" -- the live-process-state nonce. `sirr_unseal` in
# libvaultcrypto.so is exported by name and stays that way; finding it with
# `nm` and calling it directly is the intended solve, not the shortcut. What
# changed is that the archived note used to decrypt with a nonce hardcoded
# to 0 -- fully offline, since the package name is public and 0 never
# varies. Same package name, same ciphertext, but now the caller must ask
# this endpoint for the nonce before `sirr_unseal` will produce anything
# but garbage. Fixed value, not per-session: the note is one global
# ciphertext, so every caller needs the same nonce to open it.
VAULT_LIVE_NONCE = 0x7C3D9A21


@app.route("/vault/nonce", methods=["GET"])
def vault_nonce():
    """
    GET /vault/nonce

    Success 200: {"nonce": "7c3d9a21"}
    """
    return jsonify({"nonce": f"{VAULT_LIVE_NONCE:08x}"}), 200


# #17 "Second Hand" -- the five target times used to be five string literals
# in the dex, identical in every install, which meant they never rerolled:
# one write-up and every later player could skip reading `currentTarget`
# entirely. They are seeded here per round instead, so a value lifted from
# someone else's session buys nothing, and the completion check is ours, not
# the app's -- the client sends what it recorded and the server decides.
CLOCK_TARGET_COUNT = 5
CLOCK_DESIGNER_TARGETS = ["02:17", "07:43", "11:58", "16:05", "22:36"]


@app.route("/clock/start", methods=["POST"])
def clock_start():
    """
    POST /clock/start
    No body required.

    Mints a session and the five targets for this round.

    Designer mode (CTF_SIG_DISABLED=1): the same five every call, so a
    tester gets reproducible state -- standing constraint, see CLAUDE.md.

    Success 200: {"session": str, "targets": [str x5]}
    """
    if SIG_DISABLED:
        targets = list(CLOCK_DESIGNER_TARGETS)
    else:
        targets = []
        while len(targets) < CLOCK_TARGET_COUNT:
            candidate = f"{secrets.randbelow(24):02d}:{secrets.randbelow(60):02d}"
            if candidate not in targets:
                targets.append(candidate)

    session_id = _new_session(kind="clock", targets=targets)
    return jsonify({"session": session_id, "targets": targets}), 200


@app.route("/clock/finish", methods=["POST"])
def clock_finish():
    """
    POST /clock/finish
    Body: {"session": str, "recorded": [str x5]}

    All five recorded values must match this session's own targets, in slot
    order. Anything else gets the same refusal, so the response never says
    which slot was wrong.

    Success 200: {"flag": "<flag>"}
    Failure 400: {"error": "session and recorded required"}
    Failure 403: {"error": "incomplete shift"}
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("session")
    recorded = data.get("recorded")

    if not isinstance(session_id, str) or not isinstance(recorded, list):
        return jsonify({"error": "session and recorded required"}), 400

    entry = _session(session_id)
    if entry is None or entry.get("kind") != "clock":
        return jsonify({"error": "incomplete shift"}), 403

    if recorded != entry.get("targets"):
        return jsonify({"error": "incomplete shift"}), 403

    return jsonify({"flag": CHALLENGE_FLAGS[17]}), 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Securinets CTF Backend")
    parser.add_argument("--http", action="store_true", help="Run in HTTP mode (default)")
    parser.add_argument("--https", action="store_true", help="Run in HTTPS mode with cert/key")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default 8000 for HTTP, 8443 for HTTPS)")

    args = parser.parse_args()

    use_https = args.https
    port = args.port

    if use_https:
        cert_path = "certs/cert.pem"
        key_path = "certs/key.pem"

        try:
            app.run(host="0.0.0.0", port=port, ssl_context=(cert_path, key_path), debug=False)
        except FileNotFoundError as e:
            print(f"Error: SSL certificates not found. {e}")
            print("Generate them with: openssl req -x509 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem -days 3650 -nodes -subj '/CN=localhost'")
            sys.exit(1)
    else:
        app.run(host="0.0.0.0", port=port, debug=False)
