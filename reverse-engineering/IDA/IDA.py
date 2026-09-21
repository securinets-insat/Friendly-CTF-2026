flag = b"Securinets{X0r3d_1N_IDA_little_revers3rs}"
key = 0x42

encrypted = bytes(b ^ key for b in flag)

print(", ".join(f"0x{x:02x}" for x in encrypted))