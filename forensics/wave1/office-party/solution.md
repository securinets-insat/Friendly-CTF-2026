# #47 "Office Party" — Walkthrough (INTERNAL)

**Category:** Document forensics · **Tier:** 🟢 Easy · **Artifact(s):** `report.docx`
**Flag:** `Securinets{d0cx_1s_4_z1p_0f_xml}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| OOXML is a ZIP of XML | And documents carry author/creator metadata people forget about. |

---

## Intended path

### 1. Unzip the docx
`unzip report.docx -d report/`

### 2. Read the core properties
`cat report/docProps/core.xml` — the `<dc:creator>` field holds the flag (viewers show it as the Author). File -> Properties works too.

### 3. Read the flag
The creator/author value is the flag.

## Why grep/eyeball doesn't shortcut it
The document *body* (`word/document.xml`) is a red herring — the flag is in metadata.

---

## Hint ladder

1. **The visible text is useless. What else does a Word file store?**
2. **A .docx is a ZIP. Unzip it and look at docProps/core.xml.**
3. **The `<dc:creator>` (Author) field is the flag.**

---

## Build provenance
Minimal valid OOXML package ([Content_Types].xml, _rels/.rels, word/document.xml, docProps/core.xml). Flag in `dc:creator`; body text is a decoy.
