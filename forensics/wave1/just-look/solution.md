# #34 "Just Look" — Walkthrough (INTERNAL)

**Category:** Misc / Intro · **Tier:** 🟢 Easy · **Artifact(s):** `agent.dump`
**Flag:** `Securinets{str1ngs_f1nd_th3_s3cr3t}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Always check for readable text first | Before mounting, carving, or scripting anything, `strings` is the cheapest win in forensics. |

---

## Intended path

### 1. Identify
`file agent.dump` -> ELF 64-bit. `cat` spews binary noise, so don't.

### 2. Pull the strings
`strings agent.dump | grep Securinets`. The flag is a plain ASCII string sitting among heartbeat/debug messages.

### 3. Ignore the decoy
There is a `FAKE Securinets{n0t_th1s_0n3_h4h4}` decoy — the real flag is the one that reads like a sentence about the lesson.

---

## Hint ladder

1. **Don't open it in an editor. What is the very first tool you reach for on an unknown binary?**
2. **`strings` lists printable runs. Pipe it into `grep`.**
3. **`strings agent.dump | grep Securinets` — pick the real one, not the FAKE.**

---

## Build provenance
Synthetic ELF-headed blob: valid x86-64 ELF header, ~400 random records interleaved with decoy ASCII strings, the flag inserted once in the middle third. One `FAKE` decoy flag.
