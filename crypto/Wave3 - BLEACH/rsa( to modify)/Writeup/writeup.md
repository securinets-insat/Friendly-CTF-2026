---
title: "rsa (Common Modulus)"
ctf: "Securinets Friendly CTF"
date: 2026-09-18
category: crypto
difficulty: easy
points: 100
flag_format: "Securinets{...}"
author: "jed.jemili"
---

# rsa (Common Modulus)

## Summary

The same flag is encrypted twice under the **same modulus `n`** with two different public
exponents, `e1 = 3` and `e2 = 5`. Because `gcd(3, 5) = 1`, the classic **common modulus
attack** recovers the plaintext directly — no factoring of `n` needed.

## Challenge Files

`chall.py` boils down to:

```python
E1, E2 = 3, 5
m  = bytes_to_long(FLAG)
p, q = getPrime(512), getPrime(512)
n  = p * q
c1 = pow(m, E1, n)
c2 = pow(m, E2, n)
```

`chall_output.txt` gives us `n`, `e1`, `c1`, `e2`, `c2`. One message, one modulus, two exponents —
that's the whole bug.

## Solution

### Step 1: Bézout on the exponents

Since `e1` and `e2` are coprime, the extended Euclidean algorithm gives integers `a, b` with

```
a·e1 + b·e2 = 1
```

Raising each ciphertext to the matching coefficient and multiplying collapses to `m`:

```
c1^a · c2^b  ≡  m^(a·e1) · m^(b·e2)  ≡  m^(a·e1 + b·e2)  ≡  m^1  ≡  m   (mod n)
```

For `e1 = 3, e2 = 5` we get `a = 2, b = -1`, i.e. `m ≡ c1² · c2⁻¹ (mod n)`.
The negative exponent is fine — Python's `pow(c, -1, n)` computes the modular inverse for us
(the inverse exists because `gcd(c2, n) = 1`).

### Step 2: Full solve script

```python
#!/usr/bin/env python3
import re
from Crypto.Util.number import long_to_bytes

data = open("chall_output.txt").read()
get  = lambda k: int(re.search(rf"{k}\s*=\s*(\d+)", data).group(1))
n, e1, c1, e2, c2 = get("n"), get("e1"), get("c1"), get("e2"), get("c2")

def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = egcd(b, a % b)
    return g, y, x - (a // b) * y

g, a, b = egcd(e1, e2)
assert g == 1, "exponents must be coprime"

# pow() handles negative exponents mod n by inverting first
m = (pow(c1, a, n) * pow(c2, b, n)) % n
print(long_to_bytes(m).decode())
```

Output:

```
a = 2, b = -1
Recovered flag: Securinets{m4yur1_14b_p3rm1ss10n_gr4nt3d}
```

## Bonus: the challenge is doubly broken

The flag is 41 bytes → `m` is 327 bits, so `m³` is only **980 bits** while `n` is **1024 bits**.
That means `c1` was never actually reduced mod `n` — it's just the plain integer `m³`.
A single integer cube root also solves it:

```python
import gmpy2
from Crypto.Util.number import long_to_bytes
root, exact = gmpy2.iroot(c1, 3)
assert exact
print(long_to_bytes(int(root)).decode())   # Securinets{m4yur1_14b_p3rm1ss10n_gr4nt3d}
```

`c2 = m⁵` is 1632 bits, so *that* one genuinely wraps around `n`. If you're planning to reuse this
challenge, raising `e1` (or padding `m`) closes the cube-root shortcut and forces the intended
common-modulus solve.

## Flag

```
Securinets{m4yur1_14b_p3rm1ss10n_gr4nt3d}
```

## Lessons

- **Never encrypt the same plaintext under one modulus with two exponents.** Anyone holding both
  ciphertexts recovers the plaintext with a Bézout identity — the private key is irrelevant.
- **Always pad.** OAEP would kill both this attack and the low-exponent cube root, since the padded
  message is randomized and large enough to wrap the modulus.

## Tools

- Python 3 + `pycryptodome` (`Crypto.Util.number`)
- `gmpy2` (bonus cube-root path only)
