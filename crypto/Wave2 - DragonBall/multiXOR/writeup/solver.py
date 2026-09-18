from secrets import token_bytes

flag = b"Securinets{k4m3h4m3h4_b34m_d3str0ys_th3_k3y}"

# Repeating XOR key
key = b"Genkidama"

messages = [
    b"People of Earth!! Please, give me your energy!!",
    b"See you later, Majin Buu.",
    flag,
]

def repeating_xor(data, key):
    return bytes(
        b ^ key[i % len(key)]
        for i, b in enumerate(data)
    )

for i, message in enumerate(messages, 1):
    ciphertext = repeating_xor(message, key)
    print(f"ciphertext{i} = {ciphertext.hex()}")