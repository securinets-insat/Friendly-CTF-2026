# Nitro

An Agilogix employee got a DM on Discord offering free Nitro. A day later his workstation
`DESKTOP-7K2X9QP` was pulled for review — his Discord account was hijacked and something on the
box had been beaconing out.

You're handed a **full triage collection** of the host (KAPE-style: registry hives, event logs,
Amcache, Prefetch, and the user profile). Nobody has told you what to look at. **Work out what
happened** — how he got hit, what he ran, and what it stole — and recover the two-part secret.

**File:** `DESKTOP-7K2X9QP_triage.zip` (a `C\...` triage tree)

The flag has two halves — one is in what he ran, the other cannot be read without the piece of
his account the attacker was after. Concatenate in order: `Securinets{<A>_<B>}`.
