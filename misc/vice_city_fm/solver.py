#!/usr/bin/env python3

import re


text = open("playlist.m3u", encoding="utf-8").read()
flag = bytes(map(int, re.findall(r"#EXTINF:(\d+),", text)))
print(flag.decode())
