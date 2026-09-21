#!/usr/bin/env python3

from Crypto.Util.number import getPrime, bytes_to_long

FLAG = b"Securinets{f4k3_fl4g_f0r_l0c4l_t3st1ng}"

E1 = 3
E2 = 5  


def generate_challenge():
    m = bytes_to_long(FLAG)

    while True:
        p = getPrime(512)
        q = getPrime(512)
        if p == q:
            continue
        n = p * q
        if m < n:
            c1 = pow(m, E1, n)
            c2 = pow(m, E2, n)
            return n, c1, c2


def main():
    n, c1, c2 = generate_challenge()

    output = (
        f"n = {n}\n"
        f"e1 = {E1}\n"
        f"c1 = {c1}\n"
        f"e2 = {E2}\n"
        f"c2 = {c2}\n"
    )

    print(output)

    with open("chall_output.txt", "w") as f:
        f.write(output)


if __name__ == "__main__":
    main()
