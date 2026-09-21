#!/usr/bin/env python3

colors = {"🔴": "0", "🟢": "1"}
groups = open("traffic.txt", encoding="utf-8").read().split("🟡")
flag = bytes(
    int("".join(colors[color] for color in group.split()), 2)
    for group in groups if group.strip()
)
print(flag.decode())
