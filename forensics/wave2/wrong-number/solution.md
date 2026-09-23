# #12 "Wrong Number" — Walkthrough (INTERNAL)

**Category:** Forensics · **Tier:** 🟢🟡 Easy–Medium · **Artifact:** `dns.pcap` (16 KB, 148 packets)
**Flag:** `Securinets{dns_qu3r13s_l34k_by73s}`

---

## What it teaches

**DNS as a covert exfiltration channel.** No file transfer, no HTTP — data leaves the
network encoded in the *names being looked up*. The player learns to recognise the pattern
(many lookups of long, high-entropy subdomains under one domain), extract the labels, and
decode them.

| Skill | Why it matters outside the CTF |
|---|---|
| Reading DNS from a pcap (`tshark`/Wireshark) | First move on any capture with no obvious payload |
| Spotting exfil-shaped queries among noise | The core detection skill for DNS tunneling |
| Decoding hex-in-subdomains | The most common DNS-exfil encoding |
| Handling retransmissions (dedupe) | Real captures repeat packets; naive concat corrupts |

This is the **easy** member of the exfil family; #19 "Silent Exfil" is the hard sibling
(out-of-order sequence + a rebuilt PNG + crypto).

---

## Intended path

### 1. Look at the DNS

```
tshark -r dns.pcap -Y 'dns.flags.response==0' -T fields -e dns.qry.name
```

74 queries. Most are ordinary (`pool.ntp.org`, `deb.debian.org`, `cdn.jsdelivr.net`, …) —
but a cluster stands out: long hex-looking labels under one domain, each appearing **twice**:

```
5365637572696e657473.sync.datasync-cdn.net
5365637572696e657473.sync.datasync-cdn.net
7b646e735f7175337231.sync.datasync-cdn.net
7b646e735f7175337231.sync.datasync-cdn.net
33735f6c33346b5f6279.sync.datasync-cdn.net
...
```

### 2. Isolate the exfil and dedupe

Filter to the one suspicious domain, strip the label, drop the duplicate retransmissions
(keep first occurrence, preserve order):

```
tshark -r dns.pcap -Y 'dns.flags.response==0 && dns.qry.name contains "sync.datasync-cdn.net"' \
  -T fields -e dns.qry.name \
  | sed 's/\.sync\..*//' | awk '!seen[$0]++'
```

### 3. Concatenate and decode

The labels are hex. Join in capture order, un-hex:

```
... | tr -d '\n' | xxd -r -p
```

```
Securinets{dns_qu3r13s_l34k_by73s}
```

---

## The wrinkles (both fair)

1. **Retransmissions.** Every exfil label appears twice, adjacent. Concatenating without
   dedupe doubles every chunk → garbage. Any of `awk '!seen'`, `uniq` (they're adjacent), or
   `sort -u` (labels are unique) fixes it. This is the one real "gotcha."
2. **Noise.** 66 of the 74 queries are benign lookups to real domains. A naive
   `grep -o '[0-9a-f]*'` across everything pulls in junk; the player must notice the exfil
   all sits under a single, unusual domain and filter to it. Not a troll — the signal is
   clearly distinguishable (one domain, uniform label length, high entropy, paired queries).

---

## Alternative paths that legitimately work

- Wireshark GUI: `Statistics > DNS`, or sort the packet list by query name — the exfil
  cluster is visually obvious.
- `tshark ... | grep datasync-cdn | grep -oE '^[0-9a-f]+' | sort -u | tr -d '\n' | xxd -r -p`.
- Reading the labels by eye (only 4 unique chunks) and decoding in CyberChef (From Hex).

No guessing — the domain and encoding are self-evident from the capture.

---

## Hint ladder

1. **"There's no file transfer in this capture. Look at *what* is being looked up, not the
   responses."**
2. **"One domain gets a lot of long, hex-looking subdomains — and each query appears more
   than once. Collect the unique labels in order."**
3. **"Concatenate the hex labels under `sync.datasync-cdn.net` (dedupe the repeats) and run
   From Hex."**

---

## Failure modes

| Symptom | Cause / fix |
|---|---|
| Decoded output is doubled/garbled | Didn't dedupe the retransmissions. |
| Player pulls hex from noise domains too | Filter to the single exfil domain first. |
| "There's nothing here" | They looked at responses/payloads, not query names. Hint 1. |
| Odd-length hex error in `xxd -r -p` | A duplicate slipped in, making the concatenation odd-length. Dedupe. |

---

## Build provenance

- Built live on the lab VMs (attacker `10.10.10.10` dnsmasq authoritative for
  `datasync-cdn.net` + `log-queries`; victim `10.10.10.20` generated the queries), captured
  with `tcpdump` on the victim's ctfnet NIC. Only `dns.pcap` ships, so an in-guest capture
  tool leaves no problematic artifact (no disk/memory image of this host is shipped).
- Generator: `lab/scripts/gen-ch12.sh` — flag → hex → 20-char labels → `dig` each twice,
  with 25 lead-in + interleaved + 25 trailing benign lookups.
- Verified on the shipped pcap: 74 queries (8 exfil / 66 noise), intended solve decodes to
  the flag, `Securinets{` never appears as plaintext (hex-encoded only).
- **Build gotcha (author note):** a stale `/tmp/dns.pcap` from an earlier run masked
  regenerations — always `rm -f` the output and `pkill tcpdump` before re-capturing.

**Difficulty dial:** to make it harder, drop the shared parent domain (spread exfil across
several look-alike domains), or lengthen the flag so more chunks must be ordered correctly.
That progression is essentially #19.
