#!/usr/bin/env python3
"""
Konpaku Ledger - local solver (common modulus RSA attack)

Reads n, e1, c1, e2, c2 from chall_output.txt (same directory,
or pass a path as argv[1]) and recovers the flag.

Attack: same message m encrypted under the same n with two
coprime exponents e1, e2. Since gcd(e1, e2) = 1, Bezout gives
integers a, b with a*e1 + b*e2 = 1, so:

    c1^a * c2^b = m^(a*e1 + b*e2) = m^1 = m (mod n)

No factoring of n required.
"""

import re
import sys

from Crypto.Util.number import long_to_bytes


def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "chall_output.txt"

    with open(path) as f:
        data = f.read()

    n = int(re.search(r"n\s*=\s*(\d+)", data).group(1))
    e1 = int(re.search(r"e1\s*=\s*(\d+)", data).group(1))
    c1 = int(re.search(r"c1\s*=\s*(\d+)", data).group(1))
    e2 = int(re.search(r"e2\s*=\s*(\d+)", data).group(1))
    c2 = int(re.search(r"c2\s*=\s*(\d+)", data).group(1))

    g, a, b = egcd(e1, e2)
    assert g == 1, "e1 and e2 must be coprime for this attack to work"

    # pow() in Python natively handles negative exponents under a
    # modulus (it computes the modular inverse first).
    m = (pow(c1, a, n) * pow(c2, b, n)) % n

    flag = long_to_bytes(m)

    print(f"a = {a}, b = {b}")
    print(f"Recovered flag: {flag.decode()}")


if __name__ == "__main__":
    main()
