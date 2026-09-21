#!/usr/bin/env python3

import socketserver
import secrets

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.number import getPrime, bytes_to_long


# ============================================================
# CONFIGURATION
# ============================================================

HOST = "0.0.0.0"
PORT = 31337

FLAG = b"Securinets{b4nk4i_br0k3_th3_h0gy0ku}"


# ============================================================
# STAGE 1 — SENKAIMON
# Caesar Cipher
# ============================================================

STAGE1 = "EVYRLF=GHUWHRBAV"
STAGE1_ANSWER = "XORKEY=ZANPAKUTO"


# ============================================================
# STAGE 2 — ZANPAKUTO
# Repeating XOR
# ============================================================

STAGE2 = "0c08091b0412680707130f071700061c"
STAGE2_ANSWER = "VIGKEY=SHINIGAMI"


# ============================================================
# STAGE 3 — SHIKAI
# Vigenere
# ============================================================

STAGE3 = "SLAXME=ZMVYLBFCQEK12345"

# This is the information revealed to the player.
# It gives them the AES key AND the target role for Stage 4.
STAGE3_ANSWER = "AESKEY=ZANGETSUKEY12345"


# ============================================================
# STAGE 4 — BANKAI
# AES-CBC Bit Flipping
# ============================================================

AES_KEY = b"ZANGETSUKEY12345"

# Both strings are exactly 16 bytes.
OLD_ROLE = b"role=shinigami  "
NEW_ROLE = b"role=quincy     "

assert len(AES_KEY) == 16
assert len(OLD_ROLE) == 16
assert len(NEW_ROLE) == 16

AES_PLAINTEXT = (
    b"AAAAAAAAAAAAAAAA"
    + OLD_ROLE
    + b"user=ichigo"
)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def send_line(conn, text):
    """Send a UTF-8 encoded line."""
    conn.sendall((text + "\n").encode())


def recv_line(conn):
    """Receive one line from the client."""

    data = b""

    while True:
        chunk = conn.recv(1)

        if not chunk:
            return None

        if chunk == b"\n":
            break

        if chunk != b"\r":
            data += chunk

        # Prevent excessively large input.
        if len(data) > 10000:
            return None

    return data.decode(errors="ignore").strip()


def wait_for_answer(conn, expected):
    """
    Wait for:
        answer <expected>
    """

    while True:

        line = recv_line(conn)

        if line is None:
            return False

        if line == f"answer {expected}":
            return True

        send_line(conn, "Wrong answer. Try again.")


# ============================================================
# STORY — BEFORE STAGE 1
# ============================================================

def story_stage1(conn):

    send_line(conn, "")
    send_line(conn, "=" * 60)
    send_line(conn, "                    SOUL SOCIETY")
    send_line(conn, "=" * 60)
    send_line(conn, "")

    send_line(
        conn,
        "The Senkaimon opens, but the path into Soul Society is sealed."
    )

    send_line(
        conn,
        "Ichigo forces his way through the gate, only to discover"
    )

    send_line(
        conn,
        "that the first barrier is protecting a hidden message."
    )

    send_line(conn, "")
    send_line(conn, "Break the seal.")
    send_line(conn, "")

    send_line(conn, "=" * 60)
    send_line(conn, "")


# ============================================================
# STAGE 1
# ============================================================

def stage1(conn):

    story_stage1(conn)

    send_line(conn, "[1] SENKAIMON")
    send_line(conn, "-" * 60)
    send_line(conn, "")
    send_line(conn, STAGE1)
    send_line(conn, "")
    send_line(conn, "Submit your answer using:")
    send_line(conn, "answer <plaintext>")
    send_line(conn, "")

    if not wait_for_answer(conn, STAGE1_ANSWER):
        return False

    send_line(conn, "")
    send_line(conn, "Correct.")
    send_line(conn, "The first barrier falls.")
    send_line(conn, "")

    return True


# ============================================================
# STORY — BEFORE STAGE 2
# ============================================================

def story_stage2(conn):

    send_line(conn, "")
    send_line(conn, "=" * 60)
    send_line(conn, "                  THE INNER WORLD")
    send_line(conn, "=" * 60)
    send_line(conn, "")

    send_line(
        conn,
        "The gate was only the beginning."
    )

    send_line(
        conn,
        "Deep inside, Ichigo is confronted by the power within himself."
    )

    send_line(
        conn,
        "His Zanpakuto refuses to reveal its secret easily."
    )

    send_line(conn, "")

    send_line(
        conn,
        "The message is scattered behind another layer."
    )

    send_line(conn, "")
    send_line(conn, "Master the pattern.")
    send_line(conn, "")

    send_line(conn, "=" * 60)
    send_line(conn, "")


# ============================================================
# STAGE 2
# ============================================================

def stage2(conn):

    story_stage2(conn)

    send_line(conn, "[2] ZANPAKUTO")
    send_line(conn, "-" * 60)
    send_line(conn, "")
    send_line(conn, STAGE2)
    send_line(conn, "")
    send_line(conn, "Submit your answer using:")
    send_line(conn, "answer <plaintext>")
    send_line(conn, "")

    if not wait_for_answer(conn, STAGE2_ANSWER):
        return False

    send_line(conn, "")
    send_line(conn, "Correct.")
    send_line(conn, "The second barrier falls.")
    send_line(conn, "")

    return True


# ============================================================
# STORY — BEFORE STAGE 3
# ============================================================

def story_stage3(conn):

    send_line(conn, "")
    send_line(conn, "=" * 60)
    send_line(conn, "                       SHIKAI")
    send_line(conn, "=" * 60)
    send_line(conn, "")

    send_line(
        conn,
        "Zangetsu finally speaks."
    )

    send_line(
        conn,
        "To reach the next barrier, Ichigo must understand"
    )

    send_line(
        conn,
        "the language of his Zanpakuto."
    )

    send_line(conn, "")

    send_line(
        conn,
        "The message appears simple."
    )

    send_line(
        conn,
        "But every letter hides behind another."
    )

    send_line(conn, "")
    send_line(conn, "Decode the message.")
    send_line(conn, "")

    send_line(conn, "=" * 60)
    send_line(conn, "")


# ============================================================
# STAGE 3
# ============================================================

def stage3(conn):

    story_stage3(conn)

    send_line(conn, "[3] SHIKAI")
    send_line(conn, "-" * 60)
    send_line(conn, "")
    send_line(conn, STAGE3)
    send_line(conn, "")
    send_line(conn, "Submit your answer using:")
    send_line(conn, "answer <plaintext>")
    send_line(conn, "")

    if not wait_for_answer(conn, STAGE3_ANSWER):
        return False

    send_line(conn, "")
    send_line(conn, "Correct.")
    send_line(conn, "")
    send_line(conn, "Zangetsu has revealed the next path.")
    send_line(conn, "")
    send_line(conn, "The third barrier falls.")
    send_line(conn, "")

    return True


# ============================================================
# STORY — BEFORE STAGE 4
# ============================================================

def story_stage4(conn):

    send_line(conn, "")
    send_line(conn, "=" * 60)
    send_line(conn, "                       BANKAI")
    send_line(conn, "=" * 60)
    send_line(conn, "")

    send_line(
        conn,
        "The pressure becomes overwhelming."
    )

    send_line(
        conn,
        "Ichigo releases Bankai."
    )

    send_line(conn, "")

    send_line(
        conn,
        "Speed alone will not break this barrier."
    )

    send_line(
        conn,
        "The enemy's encrypted session contains a role field."
    )

    send_line(
        conn,
        "The role must be changed to QUINCY."
    )

    send_line(conn, "")

    send_line(
        conn,
        "Alter the encrypted session without knowing its plaintext."
    )

    send_line(conn, "")

    send_line(conn, "=" * 60)
    send_line(conn, "")


# ============================================================
# GENERATE BANKAI SESSION
# ============================================================

def generate_bankai_session():

    cipher = AES.new(
        AES_KEY,
        AES.MODE_CBC
    )

    ciphertext = cipher.encrypt(
        pad(
            AES_PLAINTEXT,
            AES.block_size
        )
    )

    return cipher.iv, ciphertext


# ============================================================
# CHECK BANKAI
# ============================================================

def check_bankai(iv, ciphertext):

    try:

        cipher = AES.new(
            AES_KEY,
            AES.MODE_CBC,
            iv
        )

        plaintext = unpad(
            cipher.decrypt(ciphertext),
            AES.block_size
        )

        # The player must transform:
        #
        # role=shinigami
        #
        # into:
        #
        # role=quincy
        #
        if b"role=quincy" in plaintext:
            return True

    except Exception:
        pass

    return False


# ============================================================
# STAGE 4
# ============================================================

def stage4(conn):

    story_stage4(conn)

    iv, ciphertext = generate_bankai_session()

    send_line(conn, "[4] BANKAI")
    send_line(conn, "-" * 60)
    send_line(conn, "")
    send_line(
        conn,
        "The session contains an encrypted role field."
    )
    send_line(conn, "")
    send_line(
        conn,
        "Modify the encrypted session."
    )
    send_line(conn, "")
    send_line(conn, "IV:")
    send_line(conn, iv.hex())
    send_line(conn, "")
    send_line(conn, "Ciphertext:")
    send_line(conn, ciphertext.hex())
    send_line(conn, "")
    send_line(conn, "Submit:")
    send_line(conn, "oracle <IV + ciphertext>")
    send_line(conn, "")

    while True:

        line = recv_line(conn)

        if line is None:
            return False

        if not line.startswith("oracle "):

            send_line(
                conn,
                "Invalid format. Use: oracle <IV + ciphertext>"
            )

            continue

        hex_data = line[7:].strip()

        try:

            raw = bytes.fromhex(hex_data)

        except ValueError:

            send_line(
                conn,
                "Invalid hexadecimal data."
            )

            continue

        if len(raw) < 32:

            send_line(
                conn,
                "Ciphertext too short."
            )

            continue

        submitted_iv = raw[:16]
        submitted_ciphertext = raw[16:]

        if len(submitted_ciphertext) % 16 != 0:

            send_line(
                conn,
                "Ciphertext must be block aligned."
            )

            continue

        if check_bankai(
            submitted_iv,
            submitted_ciphertext
        ):

            send_line(conn, "")
            send_line(conn, "BANKAI BROKEN.")
            send_line(conn, "")
            send_line(conn, "The fourth barrier falls.")
            send_line(conn, "")

            return True

        send_line(
            conn,
            "The role is still wrong."
        )

        send_line(conn, "")


# ============================================================
# STORY — BEFORE STAGE 5
# ============================================================

def story_stage5(conn):

    send_line(conn, "")
    send_line(conn, "=" * 60)
    send_line(conn, "                      HOGYOKU")
    send_line(conn, "=" * 60)
    send_line(conn, "")

    send_line(
        conn,
        "Aizen stands before you."
    )

    send_line(
        conn,
        "The Hogyoku has been awakened, and the final barrier"
    )

    send_line(
        conn,
        "is protected by something far more dangerous"
    )

    send_line(
        conn,
        "than a Zanpakuto."
    )

    send_line(conn, "")

    send_line(
        conn,
        "The numbers look impossible."
    )

    send_line(
        conn,
        "But Aizen has made one mistake."
    )

    send_line(conn, "")

    send_line(
        conn,
        "He trusted a weak foundation."
    )

    send_line(conn, "")
    send_line(conn, "Break the final barrier.")
    send_line(conn, "")

    send_line(conn, "=" * 60)
    send_line(conn, "")


# ============================================================
# RSA CHALLENGE
# ============================================================

def generate_rsa_challenge():

    e = 3
    m = bytes_to_long(FLAG)

    while True:

        p = getPrime(512)
        q = getPrime(512)

        if p == q:
            continue

        n = p * q

        phi = (p - 1) * (q - 1)

        # RSA requires gcd(e, phi(n)) = 1.
        if phi % e == 0:
            continue

        # Vulnerability:
        #
        #       m^3 < n
        #
        # Therefore:
        #
        #       c = m^3 mod n
        #         = m^3
        #
        if m ** 3 < n:
            break

    c = pow(m, e, n)

    assert m ** 3 < n
    assert c == m ** 3

    return e, n, c


# ============================================================
# STAGE 5
# ============================================================

def stage5(conn):

    story_stage5(conn)

    e, n, c = generate_rsa_challenge()

    send_line(conn, "[5] HOGYOKU")
    send_line(conn, "-" * 60)
    send_line(conn, "")
    send_line(conn, f"e = {e}")
    send_line(conn, "")
    send_line(conn, f"n = {n}")
    send_line(conn, "")
    send_line(conn, f"c = {c}")
    send_line(conn, "")
    send_line(conn, "Submit your answer using:")
    send_line(conn, "answer <flag>")
    send_line(conn, "")

    while True:

        line = recv_line(conn)

        if line is None:
            return False

        if not line.startswith("answer "):

            send_line(
                conn,
                "Use: answer <flag>"
            )

            continue

        submitted = line[7:].strip()

        if submitted.encode() == FLAG:

            send_line(conn, "")
            send_line(conn, "Correct.")
            send_line(conn, "")
            send_line(conn, "The final barrier falls.")
            send_line(conn, "")

            return True

        send_line(
            conn,
            "Incorrect flag. Try again."
        )


# ============================================================
# VICTORY
# ============================================================

def victory(conn):

    send_line(conn, "")
    send_line(conn, "=" * 60)
    send_line(conn, "                         VICTORY")
    send_line(conn, "=" * 60)
    send_line(conn, "")

    send_line(
        conn,
        "The Hogyoku shatters."
    )

    send_line(conn, "")

    send_line(
        conn,
        "The five barriers have fallen."
    )

    send_line(conn, "")

    send_line(
        conn,
        "You have defeated every layer protecting"
    )

    send_line(
        conn,
        "the Central 46 archive."
    )

    send_line(conn, "")

    send_line(
        conn,
        "                     BANKAI COMPLETE."
    )

    send_line(conn, "")
    send_line(conn, "FLAG:")
    send_line(conn, FLAG.decode())
    send_line(conn, "")

    send_line(conn, "=" * 60)
    send_line(conn, "")


# ============================================================
# CLIENT HANDLER
# ============================================================

def handle_client(conn, addr):

    print(f"[+] Connection from {addr}")

    try:

        # ----------------------------------------------------
        # INTRO
        # ----------------------------------------------------

        send_line(conn, "=" * 60)
        send_line(conn, "              SOUL SOCIETY — FIVE BARRIERS")
        send_line(conn, "=" * 60)
        send_line(conn, "")

        send_line(
            conn,
            "You have entered Soul Society."
        )

        send_line(
            conn,
            "Five barriers stand between you and the archive."
        )

        send_line(conn, "")

        send_line(
            conn,
            "Break them one by one."
        )

        send_line(conn, "")

        send_line(
            conn,
            "Bankai won't help you."
        )

        send_line(
            conn,
            "Your brain might."
        )

        send_line(conn, "")
        send_line(conn, "=" * 60)
        send_line(conn, "")

        # ----------------------------------------------------
        # STAGE 1
        # ----------------------------------------------------

        if not stage1(conn):
            return

        # ----------------------------------------------------
        # STAGE 2
        # ----------------------------------------------------

        if not stage2(conn):
            return

        # ----------------------------------------------------
        # STAGE 3
        # ----------------------------------------------------

        if not stage3(conn):
            return

        # ----------------------------------------------------
        # STAGE 4
        # ----------------------------------------------------

        if not stage4(conn):
            return

        # ----------------------------------------------------
        # STAGE 5
        # ----------------------------------------------------

        if not stage5(conn):
            return

        # ----------------------------------------------------
        # VICTORY
        # ----------------------------------------------------

        victory(conn)

    except Exception as e:

        print(
            f"[!] Error with {addr}: {e}"
        )

    finally:

        conn.close()

        print(
            f"[-] Connection closed: {addr}"
        )


# ============================================================
# THREADED TCP SERVER
# ============================================================

class ThreadedTCPServer(
    socketserver.ThreadingMixIn,
    socketserver.TCPServer
):

    allow_reuse_address = True
    daemon_threads = True


class ClientHandler(
    socketserver.BaseRequestHandler
):

    def handle(self):

        handle_client(
            self.request,
            self.client_address
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("          SECURINETS — BANKAI CTF SERVER")
    print("=" * 60)
    print()
    print(f"[*] Listening on {HOST}:{PORT}")
    print("[*] Waiting for players...")
    print()

    with ThreadedTCPServer(
        (HOST, PORT),
        ClientHandler
    ) as server:

        server.serve_forever()


if __name__ == "__main__":
    main()