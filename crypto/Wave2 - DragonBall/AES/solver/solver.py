from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import md5
import json

with open("challenge.json") as f:
    data = json.load(f)

ciphertext = bytes.fromhex(data["ciphertext"])
iv = bytes.fromhex(data["iv"])

for pin in range(10000):

    password = f"{pin:04d}"

    # Same key derivation as the challenge
    key = md5(password.encode()).digest()

    cipher = AES.new(key, AES.MODE_CBC, iv)

    try:
        plaintext = unpad(
            cipher.decrypt(ciphertext),
            AES.block_size
        )

        # Check whether we found the flag
        if plaintext.startswith(b"Securinets{"):
            print("Password:", password)
            print("Key:", key.hex())
            print("Flag:", plaintext.decode())
            break

    except ValueError:
        # Wrong key → invalid PKCS#7 padding
        pass