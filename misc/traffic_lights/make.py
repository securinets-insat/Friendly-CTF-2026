#!/usr/bin/env python3

from pathlib import Path


FLAG = b"Securinets{r3d_gr33n_l1ghts_sp3ll_th3_l34k}"
colors = {"0": "🔴", "1": "🟢"}
signals = [
    " ".join(colors[bit] for bit in f"{byte:08b}") + " 🟡"
    for byte in FLAG
]

Path(__file__).with_name("traffic.txt").write_text(
    "\n".join(signals) + "\n", encoding="utf-8"
)
