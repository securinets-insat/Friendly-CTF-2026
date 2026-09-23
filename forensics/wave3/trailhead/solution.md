# #25 "Trailhead" — Walkthrough (INTERNAL)

**Category:** Forensics · **Tier:** 🟡🟠 Medium-Hard
**Artifacts:** `entra_signins.json` (22 KB), `cloudtrail.json` (170 KB), `s3_access.log` (187 KB)
**Flag:** `Securinets{cl0udtr41l_t1m3l1n3_st1tch3d}`

Three logs, three timestamp conventions, one attacker threading through all of them:
- **Entra** sign-in logs — time as **epoch milliseconds** (`authTimeMs`)
- **CloudTrail** — time as **ISO 8601 UTC** (`eventTime`, `...Z`)
- **S3 access log** — time as **CLF** (`[14/Jun/2019:02:29:01 +0000]`)

Attacker IP: `45.83.220.14` (Amsterdam hosting). Compromised identity: `mkedri@agilogix.tn`.

---

## What it teaches

Cloud/identity forensics — the "host" is an account, not a machine — and the unglamorous
core skill of **correlating one actor across logs that agree on nothing, including how they
write the time.**

| Skill | Why it matters outside the CTF |
|---|---|
| Spotting **impossible-travel** in sign-in logs | The canonical account-takeover signal |
| Following a pivot through **CloudTrail** (`jq`) | Standard AWS incident response |
| Reading **S3 server access logs** | Proving what data actually left |
| Normalising **epoch-ms / ISO-8601 / CLF** to one basis | The real work in every multi-source timeline |
| Separating one actor from a noisy shared principal | Why "filter by user" isn't enough |

---

## Intended path

### 1. Entra — impossible travel

Group sign-ins by user; find the one account that logged in from two countries:

```
jq -r '.value | group_by(.userPrincipalName)[]
       | select((map(.location.countryOrRegion)|unique|length)>1)
       | .[] | "\(.authTimeMs)  \(.userPrincipalName)  \(.ipAddress)  \(.location.city)"' entra_signins.json
```

`mkedri@agilogix.tn` appears from **Tunis** and **Amsterdam**. The times are epoch-ms:

```
date -u -d @$((1560478447442/1000))   # 2019-06-14 02:14:07  Tunis   (legit)
date -u -d @$((1560479133110/1000))   # 2019-06-14 02:25:33  Amsterdam (attacker, +11 min)
```

Two continents, eleven minutes apart → account takeover. **Attacker IP: `45.83.220.14`.**

### 2. CloudTrail — the privilege pivot

Everything from the attacker IP:

```
jq -r '.Records[] | select(.sourceIPAddress=="45.83.220.14")
       | "\(.eventTime)  \(.eventName)  \(.requestParameters.userName // "-") -> \(.responseElements.accessKey.accessKeyId // "-")"' cloudtrail.json
```

```
2019-06-14T02:27:21Z  GetCallerIdentity  -                -
2019-06-14T02:27:58Z  CreateAccessKey    svc-backup       AKIA5JQATTACKER99Z
```

The attacker (in `mkedri`'s SSO session) minted a **new access key for a *different* IAM
user, `svc-backup`** — a long-lived backdoor onto the backup service account.

### 3. S3 — the exfiltration

Now the twist: `svc-backup` is also the **legitimate automation principal** that does
hundreds of routine backup reads all day, so *filtering S3 by principal is useless* — every
line says `user/svc-backup`. Pivot on the **attacker IP** instead:

```
grep " 45.83.220.14 " s3_access.log
```

```
[14/Jun/2019:02:28:49 +0000] ... REST.GET.BUCKET  -                     (enumerate)
[14/Jun/2019:02:29:01 +0000] ... REST.GET.OBJECT  exports/U2VjdXJpbmV0c3t...==
```

A bucket listing, then a single object GET — moments after the key was created. Decode the
object key:

```
echo 'U2VjdXJpbmV0c3tjbDB1ZHRyNDFsX3QxbTNsMW4zX3N0MXRjaDNkfQ==' | base64 -d
Securinets{cl0udtr41l_t1m3l1n3_st1tch3d}
```

### 4. Stitch the timeline (the deliverable)

Converting all three formats to one basis proves causality:

```
02:25:33Z  Entra sign-in from NL          (epoch-ms 1560479133110)
02:27:58Z  CloudTrail CreateAccessKey     (ISO 8601)
02:29:01Z  S3 GET exports/…               (CLF)
```

---

## The red herrings

1. **`svc-backup` noise.** ~300 CloudTrail `AssumeRole` events and ~400 S3 GETs from the
   internal automation host (`10.0.42.7`) fill the same day. A player who filters by the
   `svc-backup` principal drowns. The discriminator is the **attacker IP** (or the time
   window), never the principal.
2. **Decoy base64 object keys.** Five legit objects have base64 names too
   (`nightly-index-Q2`, `retention-policy-v4`, …). A player who greps every base64-looking
   key and decodes them gets six candidates and must still reason about which is the exfil —
   only one decodes to a flag, but they had to work for it rather than grep-skipping.
3. **`mkedri`'s normal Tunis logins** all day — the account is a real, active user, so its
   presence in the logs isn't itself suspicious. Only the *Amsterdam* session is.

---

## Alternative paths that legitimately work

- **Time-first:** find the anomalous window from Entra, convert all three logs to epoch, and
  slice the ~02:25–02:30 window. Lands on the same S3 GET. (This is the path the "three
  timestamp formats" trick is built to make you earn.)
- **Key-first:** from CloudTrail take `AKIA5JQATTACKER99Z`; note S3 logs identify the
  requester by ARN not access-key-id, so this alone won't filter S3 — you still need IP or
  time. Good lesson in what each log does and doesn't record.
- **Grep-and-decode** every base64 object key (see red herring 2) — works, but noisier.

---

## Hint ladder

1. **"One account signed in from two places it could not physically be in. Who, and from
   what IP?"**
2. **"Follow that IP into CloudTrail. What did the attacker create — and notice it's for a
   *different* user than the one who logged in."**
3. **"That backup user also runs legit automation, so don't filter S3 by the user — filter
   by the attacker's IP. The object it read has a base64 name. Decode it."**

---

## Failure modes

| Symptom | Cause / fix |
|---|---|
| Player filters S3 by `svc-backup`, gives up in the noise | Intended. Hint 3 — pivot on IP/time, not principal. |
| Player tries to filter S3 by `AKIA5JQATTACKER99Z` | S3 logs record the ARN, not the access-key-id. Use IP or time. |
| Timeline looks out of order | They string-sorted mixed formats. Convert epoch-ms, ISO-Z, and CLF to one basis first. |
| Player submits a decoy-decoded string | Red herring 2. Only one base64 key decodes to `Securinets{…}`. |
| Entra times look wrong | `authTimeMs` is **milliseconds**; divide by 1000 before `date -d @`. |

---

## Build provenance

- Generator: `scratchpad/build25.py` (seed 1409, deterministic). Build tree `build/ch25/`;
  **only** the three logs + README + SHA256SUMS ship.
- Fully synthetic — **no real AWS account, tenant, or identity was touched.** All ARNs,
  account id (`209384756012`), IPs, and users are fabricated.
- Flag is base64 in the exfil S3 object key; `Securinets{` never appears in plaintext in any
  log (verified on the shipped files).
- Attacker IP `45.83.220.14` deliberately threads all three logs (Entra 1 / CloudTrail 2 /
  S3 2) so cross-log correlation is possible from any starting point.
- Realism touches: Entra epoch-ms export (as a SIEM would emit), CloudTrail ISO-8601,
  S3 CLF; `svc-backup` doubles as legit automation and the backdoor target; the account id
  and region (`eu-west-1`) are internally consistent.

**Difficulty dial:** to harden, drop the attacker IP from the S3 log (leave only the shared
`svc-backup` ARN) so the exfil can be isolated **only** by the time window — forcing full
three-format normalisation with no IP shortcut. Kept the IP thread here so the challenge has
a clean primary path at Medium-Hard.
