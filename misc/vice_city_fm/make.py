#!/usr/bin/env python3

from pathlib import Path


FLAG = b"Securinets{th3_pl4yl1st_w4s_th3_l34k}"
lines = ["#EXTM3U"]
for index, byte in enumerate(FLAG):
    lines += [f"#EXTINF:{byte},Vice City Track {index:02}", f"audio/{index:02}.mp3"]

Path(__file__).with_name("playlist.m3u").write_text(
    "\n".join(lines) + "\n", encoding="utf-8"
)
