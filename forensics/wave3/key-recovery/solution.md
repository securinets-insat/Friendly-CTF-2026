# #17 "Key Recovery" — Walkthrough (INTERNAL)

**Category:** Forensics · **Tier:** 🟡🟠 Medium-Hard
**Artifacts:** `traffic.pcapng` (30 KB, TLS 1.3) + `agent.core` (5.5 MB, ELF process core)
**Flag:** `Securinets{tls_k3ys_l1v3_1n_m3m0ry}`

The standout of the set: decrypt "undecryptable" TLS 1.3 by recovering the session keys from
a process memory dump. Modern, realistic IR, and rare in CTFs.

---

## What it teaches

**TLS is only as private as its endpoints' memory.** A capture with no keys looks hopeless —
but if you have a dump of a process that held the TLS secrets, you can rebuild an NSS keylog
and decrypt everything. This is exactly how analysts decrypt malware C2 when they have a
memory image.

| Skill | Why it matters outside the CTF |
|---|---|
| Recognising undecryptable TLS 1.3 in a pcap | Knowing when you need out-of-band key material |
| Carving `CLIENT_TRAFFIC_SECRET_0` etc. from a memory dump | The core technique for memory-assisted TLS decryption |
| Building an NSS keylog + Wireshark `tls.keylog_file` | The standard decryption workflow |
| Pairing keys to the right session via ClientHello random | Isolating one session when a dump holds several / when there are decoys |
| Reading an ELF process core (`strings`/`gdb`) | Everyday memory forensics |

---

## Intended path

### 1. See that the traffic is TLS 1.3 and opaque

```
tshark -r traffic.pcapng -Y 'tls.handshake.type==1' -T fields -e tls.handshake.random
```

Seven TLS sessions (a sync agent chatting to a CDN-looking host). All application data is
encrypted; there's nothing to read yet. Note there are **many** sessions — you'll need to
find the one that matters.

### 2. Realise the keys might be in the dump

`agent.core` is a memory dump of the process that made these connections. TLS libraries that
honour `SSLKEYLOGFILE` format their secrets as NSS keylog lines
(`CLIENT_TRAFFIC_SECRET_0 <client_random> <secret>`), and those strings can linger in the
heap. Carve them:

```
strings agent.core | grep -E 'TRAFFIC_SECRET|EXPORTER_SECRET' | sort -u > keylog.txt
```

(or `grep -aoE '(CLIENT|SERVER)_(HANDSHAKE_)?TRAFFIC_SECRET_0 [0-9a-f]{64} [0-9a-f]+' agent.core`)

You get the client/server application-traffic secrets (and exporter) for **one**
`client_random`.

### 3. Match the key to the right session

The `client_random` in the recovered keylog matches exactly one ClientHello in the pcap —
the real exfil session. The other six have no keys in the dump (see red herring).

### 4. Decrypt

```
tshark -r traffic.pcapng -o tls.keylog_file:keylog.txt -Y 'http.request.method=="POST"' \
  -T fields -e http.file_data | xxd -r -p
```

or in Wireshark: *Preferences → Protocols → TLS → (Pre)-Master-Secret log filename* →
`keylog.txt`, then Follow HTTP Stream.

```
AGILOGIX INTERNAL - VAULT EXPORT (CONFIDENTIAL)
...
Securinets{tls_k3ys_l1v3_1n_m3m0ry}
```

Only the `CLIENT_TRAFFIC_SECRET_0` / `SERVER_TRAFFIC_SECRET_0` pair is needed to decrypt the
application data (the POST body); the handshake secrets aren't required for the flag.

---

## The red herring

**Six of the seven sessions are undecryptable.** The dump holds keys for only the real exfil
session; the others (benign "noise" lookups to `cdn1/api/static/img/telemetry/assets.
softsync-cdn.net`, plus one decoy `POST`) have **no matching secrets**. A player who tries to
decrypt the wrong session — or assumes all sessions share keys — wastes time. The
discriminator is the `client_random`: match the keylog's random to the ClientHello, then
decrypt that stream. This mirrors real captures where a dump yields keys for one process/one
connection out of many.

---

## Alternative paths that legitimately work

- Wireshark GUI end-to-end (set keylog file, Follow HTTP Stream on the decrypted session).
- `gdb agent.core` + `find`/`strings` to locate the secrets, same result.
- Volatility on the core (overkill, but valid) to enumerate strings/heap.
- Carving with a broader regex and letting Wireshark ignore the non-matching lines.

No guessing — the keys are literally present in the dump in a documented format.

---

## Hint ladder

1. **"The pcap is TLS 1.3 with no keys — on its own, undecryptable. But you were also given a
   memory dump of the process that made the connections. What does a TLS library leave in
   memory when key logging is on?"**
2. **"Carve `CLIENT_TRAFFIC_SECRET_0` / `SERVER_TRAFFIC_SECRET_0` lines from `agent.core`,
   put them in a file, and point Wireshark's TLS keylog setting at it. There are many
   sessions — only one has keys."**
3. **"`strings agent.core | grep TRAFFIC_SECRET > keylog.txt`, then
   `tshark -r traffic.pcapng -o tls.keylog_file:keylog.txt` and Follow the HTTP stream whose
   ClientHello random matches the keylog."**

---

## Failure modes

| Symptom | Cause / fix |
|---|---|
| "Nothing decrypts" | Carved lines malformed (extra bytes) — each line must be `LABEL <64hex> <hex>`. Re-grep. |
| Player decrypts a session but it's empty/benign | They matched a noise session. Use the keylog's `client_random` to pick the right stream. |
| `strings` finds no secrets | Some `strings` builds miss them across page boundaries; use `grep -a` on the raw core. |
| Player greps the core for the flag directly | Returns nothing — the plaintext was never in the dumped process (see build note). Good: forces the intended path. |
| Odd-length hex in `xxd -r -p` | `http.file_data` field selection picked up an empty row; filter `grep -v '^$'`. |

---

## Build provenance

- Built live on the lab VMs: attacker nginx (`10.10.10.10:443`, TLS 1.3, self-signed
  `updates.softsync-cdn.net`); victim ran an uploader that POSTed the vault file, plus benign
  noise sessions and one decoy.
- **Key design point — no plaintext in the dump.** The *uploader* process (which held the
  file bytes) sends the data then **exits**, freeing the plaintext. A separate *holder*
  process receives only the keylog text over a pipe and is the one `gcore`'d. Result verified:
  `agent.core` contains the TLS secrets but `grep 'Securinets{'` on it returns **0** — the
  strings-shortcut is closed and the intended path is mandatory.
- Noise: 6 benign TLS 1.3 sessions (varied SNIs) + 1 decoy `POST`, interleaved before/after
  the real exfil so it isn't positionally obvious (7 sessions total).
- Verified on the **shipped** files: keylog carves cleanly, real session decrypts to the flag,
  6 other sessions undecryptable, flag absent as plaintext in both pcapng and core.
- **Build gotchas (author notes):**
  1. *Stale `/tmp`* — leftover `tcpdump`/holder processes from prior runs left a stale pcap
     that didn't match the fresh dump (keys ↔ capture mismatch → nothing decrypts). The
     generator now `pkill`s and `rm`s at the start.
  2. *Attacker DoS* — an aggressive noise burst (rapid TLS connections) hung the 768 MB
     attacker's network stack (conntrack/fd exhaustion). Noise was gentled (fewer sessions,
     0.4–0.8 s gaps) and made fault-tolerant (a dropped noise session can't abort the build;
     the real exfil retries).

**Difficulty dial:** to harden, ship a full RAM image instead of a targeted core (players
must first find the process), or include keys for a *second* session that decrypts to a
decoy file — so the player must reason about which decrypted stream is the real exfil.
