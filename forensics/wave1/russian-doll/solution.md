# #37 "Russian Doll" — Walkthrough (INTERNAL)

**Category:** Archives · **Tier:** 🟢 Easy · **Artifact(s):** `doll.zip`
**Flag:** `Securinets{unz1p_4ll_th3_w4y_d0wn}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| Nested archives | Recursively unpacking layered containers, a routine step when carving droppers and packed samples. |

---

## Intended path

### 1. Unzip, repeat
Each zip contains one file: the next zip. Unzip seven times.
```
f=doll.zip
while file "$f" | grep -q Zip; do unzip -o "$f"; f=$(ls -t doll_*.zip flag.txt 2>/dev/null | head -1); done
```

### 2. Or let binwalk do it
`binwalk -Me doll.zip` extracts all layers at once.

### 3. Read the bottom
The innermost file is `flag.txt` with the flag.

---

## Hint ladder

1. **What's inside the zip? Another zip.**
2. **Keep unzipping — there are 7 layers.**
3. **`binwalk -Me doll.zip` recurses automatically; read the final `flag.txt`.**

---

## Build provenance
`flag.txt` re-zipped 7 times, each layer named `doll_N.zip`. Pure nested zip (no appended data) so it does not collide with #2 Say Cheese.
