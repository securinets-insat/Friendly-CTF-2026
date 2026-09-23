# Ghost in the GPU

An ML inference job crashed on a GPU box and left a raw **VRAM capture**. The accelerator was
scrubbed before anyone could image it properly — but this memory dump survived.

`file` says `data`. `binwalk`, `foremost`, `photorec` — every carver — find nothing worth having.
There is no container here. Figure out what the GPU was actually holding, and read it.

**File:** `vram_dump.bin` (32 MB)
