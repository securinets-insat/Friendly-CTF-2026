---
title: "Cookies"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: easy
author: "L-BOH"
---

# Cookies

## Summary

The application stores the admin decision in a Base64 cookie. Base64 is reversible encoding, so changing the decoded value from False to True grants admin access.

## Root cause

The application creates and trusts the cookie like this:

~~~python
is_admin = False
encoded = base64.b64encode(str(is_admin).encode()).decode()
resp.set_cookie('is_admin', encoded)
...
is_admin = base64.b64decode(is_admin_cookie).decode() == 'True'
~~~

Base64 is encoding, not a signature. The browser can change the value, and the server makes an authorization decision from the changed value instead of looking up the role server-side.

## Vulnerability

Log in with any account and inspect the cookies. The is_admin value decodes from Base64 to False. The application accepts a replacement value instead of keeping the role only on the server.

## Exploit

1. Register and log in normally to obtain a valid session.
2. Replace the is_admin cookie with:

~~~text
VHJ1ZQ==
~~~

This is Base64 for True:

~~~text
echo -n True | base64
~~~

3. Open /profile. The valid session proves we are logged in and the changed cookie makes the application show the admin response.

## Flag

~~~text
Securinets{v3ry_e4sy_c00k13_m4n1pul4t10n}
~~~
