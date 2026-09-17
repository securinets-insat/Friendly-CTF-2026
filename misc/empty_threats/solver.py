#!/usr/bin/env python3

text = open("message.txt", encoding="utf-8").read()
hidden = "".join(char for char in text if char in "\u200b\u200c\u2060")

flag = bytes(
    int(part.replace("\u200b", "0").replace("\u200c", "1"), 2)
    for part in hidden.split("\u2060")
)

print(flag.decode())
