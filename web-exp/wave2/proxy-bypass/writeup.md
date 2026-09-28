---
title: "Old is not always gold"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: medium
author: "L-BOH"
---

# Old is not always gold

## Summary

An old Nginx proxy and its backend disagree about a malformed request path. A raw byte bypasses the proxy's protection for /admin while the backend still handles the request as /admin.

## Root cause

The proxy protects only an exact path, then forwards every other path:

~~~nginx
location = /admin {
    deny all;
}
location / {
    proxy_pass http://app:5000;
}
~~~

The backend separately exposes the admin response:

~~~python
@app.get('/admin')
def admin():
    return jsonify({"flag": FLAG})
~~~

This relies on Nginx and Flask parsing every malformed path in the same way. The raw 0xA0 byte makes the proxy miss the exact match while the backend accepts the normalized path.

## Vulnerability

A normal request to /admin is denied. The challenge uses a parser differential: the proxy checks the path one way, while the application server normalizes the same bytes another way. The backend's administrative endpoint is reached when the two parsers disagree.

## Exploit

Append the literal byte 0xA0 to the path /admin. Do not URL-encode it as percent-A0.

The included [solver.py](solver.py) creates the exact raw request:

~~~python
path = b"/admin" + bytes([0xA0])
~~~

Set the host and port on lines 3-4, then run:

~~~bash
python solver.py
~~~
its possible also with burpsuite which is much easier by adding that byte to the raw bytes of the request
here is a research about this technique : https://blog.bugport.net/exploiting-http-parsers-inconsistencies

Nginx does not treat the resulting path as its exact protected location, so it proxies the request. The backend accepts the normalized path and returns the flag.

## Flag

~~~text
Securinets{3xplo1ting_0ld_ht7p_p4rser_inc0nsist3ncy}
~~~
