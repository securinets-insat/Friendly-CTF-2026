# #19 "Silent Exfil" — Walkthrough (INTERNAL)

**Category:** Forensics · **Tier:** 🟡🟠 Medium-Hard · **Artifact:** `exfil.pcapng` (58 KB)
**Flag:** `Securinets{0rd3r_th3n_st3g0_th3n_x0r}`

The hard sibling of #12. Three chained stages, each feeding the next:
1. **DNS exfil, out of order** — sort by seq, reassemble base32 → a PNG
2. **Stego** — LSB-hidden ciphertext in the PNG
3. **Crypto** — XOR key published in a DNS TXT record

---

## What it teaches

DNS tunneling with real-world friction (reordering) plus a stego+crypto tail. Teaches that
reassembly order matters, that carved blobs can carry more (stego), and that keys are often
hiding in the same capture (the TXT record).

| Skill | Why it matters |
|---|---|
| DNS-exfil reassembly with a **sequence field** | Real tunnels reorder; capture order ≠ data order |
| base32 decoding to a file | Common DNS-safe encoding |
| LSB extraction (`zsteg`) | Recovering a payload from a carved image |
| Finding a key in a **TXT record** | Keys frequently ship alongside the data |
| Chaining stages | Each output is the next input |

---

## Intended path

### Stage 1 — reassemble the DNS exfil (in order)
Filter the exfil queries (many `NNN.<BASE32>.sync.datasync-cdn.net` under one domain, amid
benign DNS/HTTP/ARP noise). **They're out of order** — each label starts with a 3-digit
sequence number.
```
tshark -r exfil.pcapng -Y 'dns.flags.response==0 && dns.qry.name contains "sync.datasync-cdn.net"' \
  -T fields -e dns.qry.name | sort -u | grep -E '^[0-9]{3}\.' \
  | sort -n -t. -k1 | sed -E 's/^[0-9]+\.([A-Z2-7]+)\..*/\1/' | tr -d '\n' > b32.txt
python3 -c "import base64;s=open('b32.txt').read().strip();s+='='*((8-len(s)%8)%8);open('out.png','wb').write(base64.b32decode(s))"
file out.png     # -> PNG image data, 64 x 16
```

> **The trick:** reassembling in *capture order* (not sorted by the seq prefix) yields bytes
> that are **not** a valid PNG — so a naive "concatenate everything" fails. Sorting by the
> leading number is mandatory.

### Stage 2 — LSB-extract the ciphertext
```
zsteg -E b1,rgb,lsb,xy out.png > lsb.bin
```
The payload is `[2-byte length][ciphertext]` — read the length, take that many bytes.

### Stage 3 — the key is in a TXT record
```
tshark -r exfil.pcapng -Y dns.txt -T fields -e dns.txt      # -> tr41lw1nd
```
XOR the ciphertext with the key (repeating):
```
Securinets{0rd3r_th3n_st3g0_th3n_x0r}
```

---

## The red herrings / friction

- **Out-of-order chunks** — the central trick; capture order produces a corrupt, non-PNG blob.
- **Benign DNS/HTTP noise** — pool.ntp.org, jsdelivr, etc., plus ARP/ICMP background, so the
  exfil must be isolated by its distinctive `sync.datasync-cdn.net` parent + `NNN.` prefix.

---

## Alternative paths

- Do it all in Python/CyberChef (extract names → sort → base32 → PNG → LSB → XOR).
- `stegsolve` for the LSB plane instead of `zsteg`.
- Any base32 tolerance for padding (strip/re-add `=`).

No guessing — sequence numbers give the order, the TXT record gives the key.

---

## Hint ladder

1. **"No file transfer in the capture — the data is in the DNS *names*. Collect the queries
   under the one odd domain. Look at how each label starts."**
2. **"Each label has a 3-digit sequence prefix, and they're shuffled. Sort by it, strip the
   prefix, concatenate, and base32-decode — you'll get a file."**
3. **"It's a PNG with an LSB payload (`zsteg -E b1,rgb,lsb,xy`). The XOR key is in a DNS TXT
   record in the same capture."**

---

## Failure modes

| Symptom | Cause / fix |
|---|---|
| Decoded blob isn't a PNG | Reassembled in capture order — sort by the `NNN.` prefix first. |
| base32 decode errors | Missing padding — pad the concatenation to a multiple of 8 with `=`. |
| LSB extract gives garbage | Wrong channel/order — use `b1,rgb,lsb,xy`; the payload is length-prefixed. |
| XOR output is garbage | Wrong key — it's the TXT record value (`dns.txt`), not a guess. |

---

## Build provenance

- Built on the lab VMs: attacker dnsmasq answers `*.sync.datasync-cdn.net` (A) and publishes
  the XOR key as `txt-record=key.sync.datasync-cdn.net,"tr41lw1nd"`. Victim generated the
  payload and exfiltrated it.
- Payload chain (victim `python3`): flag XOR `tr41lw1nd` → ciphertext → LSB-embedded (length-
  prefixed, `b1,rgb,lsb,xy`) into a 64×16 PNG → base32 (padding stripped for DNS) → 40-char
  chunks → `NNN.`-seq-prefixed → **shuffled** → `dig`'d out of order, with benign DNS noise.
- Whole-interface capture + ambient ARP/ICMP/DNS/HTTP for realism.
- Verified on the shipped pcap: sorted reassembly → valid PNG; capture-order reassembly →
  non-PNG (trick holds); `zsteg` → 37-byte ciphertext; TXT key XOR → flag; flag not plaintext
  anywhere.
- **Build gotcha (author note):** the first carrier PNG (220×90) produced 2249 chunks / an
  884 KB pcap — absurd. Shrunk the carrier to 64×16 (~109 chunks, 58 KB) since only ~39 bytes
  of LSB payload are needed.

**Difficulty dial:** interleave a *second* out-of-order stream (a decoy that reassembles to a
junk PNG), or gzip the PNG before base32 so the file type isn't obvious until decompressed.
