---
title: "Vault"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: hard
author: "L-BOH"
---

# Vault

## Summary

The input filter permits shell command substitution. Shell variable expansion supplies the missing spaces, and a changing exit status becomes an oracle for each flag character.

## Root cause

The filter allows shell metacharacters and the application executes the resulting string:

~~~python
ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.{}$`^")
...
cmd = "ping -c 2 " + input
status = os.system(cmd)
~~~

Dollar signs and backticks are enough for command substitution even though ordinary spaces and semicolons are rejected. The shell expands IFS into spaces and evaluates the nested command before running ping.

## Vulnerability

The vault rejects ordinary shell separators, but it accepts dollar signs and backticks. This still permits a nested command. The response is either Exit code: 0 or Failure, allowing us to learn whether a shell command found a matching prefix.

## Exploit

Use this value as the host. The two ASCII 0x60 characters are literal shell backticks:

~~~text
8.8.8.8${IFS}`grep${IFS}^Securinets{NEXT_CHARACTER}${IFS}flag.txt`
~~~

The shell replaces ${IFS} with spaces and evaluates the text between the backticks. If grep finds a flag starting with the guessed prefix, its output becomes an extra ping argument and the page says Failure. A wrong guess leaves the normal ping command and produces Exit code: 0.

Start with Securinets and an opening brace, append the character that causes Failure, and repeat to the closing brace.

The included [exp.py](exp.py) automates this. Set the target on line 3, then run:

~~~bash
python exp.py
~~~

## Flag

~~~text
Securinets{no7_4_fan_of_c0mm4nd_subs7itut1on}
~~~
