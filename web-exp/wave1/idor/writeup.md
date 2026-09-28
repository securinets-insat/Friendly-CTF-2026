---
title: "1dor"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: easy
author: "L-BOH"
---

# 1dor

## Summary

Changing the numeric note ID exposes notes belonging to other users. The administrator flag is split among many notes, so enumerate IDs and ignore decoys.

## Root cause

The note-detail query is:

~~~python
c.execute('SELECT note FROM notes WHERE id=?', (note_id,))
~~~

It checks only a note ID. The query is missing an owner condition such as user_id equals the currently logged-in user's ID, so any authenticated user can request another user's note.

## Vulnerability

After logging in as the regular user, the application shows only that user's notes. However, changing the number in a note-detail URL returns another user's note instead of denying access. This is an insecure direct object reference (IDOR).

## Exploit

Log in with the supplied account:

~~~text
username: user
password: userpass
~~~

Request increasing note IDs. Keep the character from every response except the decoy text not here, and stop after the collected string ends with the closing brace.

The included [exp.py](exp.py) automates this:

~~~bash
python exp.py
~~~

Set BASE_URL on line 4 to the deployed challenge URL. The script keeps the login session, requests each numeric ID, parses the note content, skips decoys, and builds the flag.

## Flag

~~~text
Securinets{1d0r_1s_4n_1mp0rt4nt_v3ct0r_0f_w3b_3xpl01t4t10n}
~~~
