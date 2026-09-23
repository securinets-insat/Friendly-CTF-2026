# #43 "Hello Packet" — Walkthrough (INTERNAL)

**Category:** Network · **Tier:** 🟢 Easy · **Artifact(s):** `capture.pcap`
**Flag:** `Securinets{cl34rt3xt_http_l34ks_1t}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Opening and filtering a PCAP | And that cleartext HTTP exposes URLs and parameters. |

---

## Intended path

### 1. Open in Wireshark
Filter `http`. Four packets: SYN, SYN-ACK, the GET, the 200 OK.

### 2. Read the GET
The request line is `GET /search?q=Securinets{...}&lang=en` — the flag is in the query string.

### 3. Or just strings it
`strings capture.pcap | grep Securinets` also works — it's cleartext.

---

## Hint ladder

1. **Open it in Wireshark and filter for `http`.**
2. **Look at the GET request line and its query parameters.**
3. **`strings capture.pcap | grep Securinets` if you don't want to open Wireshark.**

---

## Build provenance
Hand-built libpcap (Ethernet/IPv4/TCP, correct IP checksums) with a 4-packet HTTP session; flag in the GET query string. Cleartext by design.
