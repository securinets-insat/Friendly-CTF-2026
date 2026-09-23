# #41 "Zip Code" — Walkthrough (INTERNAL)

**Category:** Mobile · **Tier:** 🟢 Easy · **Artifact(s):** `app-release.apk`
**Flag:** `Securinets{4pk_1s_just_4_z1p_f1l3}`

---

## What it teaches

| Skill | Why it matters |
|---|---|
| An APK is a ZIP | So are JAR/WAR/DOCX/XLSX. `unzip` opens them all. |

---

## Intended path

### 1. Unzip the APK
`unzip app-release.apk -d app/` — you get `AndroidManifest.xml`, `classes.dex`, `res/`, ...

### 2. Read the string resources
`cat app/res/values/strings.xml` — among `app_name` and `welcome` sits a `license_key` string.

### 3. Read the flag
The `license_key` value is the flag.

---

## Hint ladder

1. **You don't need Android tooling. What kind of file is an .apk really?**
2. **It's a ZIP. Unzip it.**
3. **Look in `res/values/strings.xml` for `license_key`.**

---

## Build provenance
Minimal but structurally real APK (manifest, dummy classes.dex, resources.arsc, META-INF). Flag placed as a `<string name="license_key">` resource among decoys.
