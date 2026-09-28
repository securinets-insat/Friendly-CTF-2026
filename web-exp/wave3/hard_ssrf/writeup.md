---
title: "ha"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: hard
author: "L-BOH"
---

# ha

## Summary

This challenge combines DNS rebinding with an HAProxy URL-decoding differential. The fetcher approves a public DNS answer but later fetches a private Docker address; a trailing malformed percent sign bypasses HAProxy's flag-path block.

## Vulnerable code

The fetcher validates DNS only once in [src/fetcher/app.js](src/fetcher/app.js), lines 17-24:

~~~javascript
const addresses = await dns.lookup(hostname, { all: true });
for (const addr of addresses) {
  const ip = ipaddr.parse(addr.address);
  if (ip.range() === 'loopback' || ip.range() === 'private' || ip.range() === 'linkLocal') {
    return false;
  }
}
~~~

It then makes a HEAD request, waits two seconds, and makes a separate GET at lines 39-62. The address checked at the start is not pinned to either connection. A rebinding hostname can therefore return a public address during the check and the internal address later.

HAProxy should block the flag path in [src/haproxy/haproxy.cfg](src/haproxy/haproxy.cfg), lines 22-24:

~~~haproxy
acl restricted_flag path_sub,url_dec -m sub -i /flag.txt
http-request deny if restricted_flag
~~~

On the supplied HAProxy 3.2.0, the legacy URL decoder mishandles a malformed final percent sign. The raw path still begins with /internal, so lines 16 and 26 route it to the internal backend; the decoder used by the flag check fails to recognize /flag.txt.

## Exploit

Request the fetcher with:

~~~text
http://0a64000a.93a80001.rbndr.us/internal/flag.txt%
~~~

The rebinding service alternates the public and private hexadecimal addresses. The private address is 10.100.0.10, the HAProxy address from [src/docker-compose.yaml](src/docker-compose.yaml), lines 30-35.

When the timing succeeds:

1. the DNS check sees the public answer;
2. Axios later connects to the internal address;
3. HAProxy sees a trusted source in the Docker subnet and routes /internal;
4. the malformed percent sign bypasses the decoded flag-path ACL;
5. the internal service returns /internal/flag.txt.

The included [solver.py](solver.py) uses this exact URL and retries until it wins the rebinding race:

~~~bash
python solver.py
~~~

Set BASE_URL on line 3 to the challenge host if it differs. Retries are expected, not a sign that the payload is wrong.

## Flag

~~~text
Securinets{d0cker_c0mpse_d3ta1ls_4r3_imp0rtant}
~~~
