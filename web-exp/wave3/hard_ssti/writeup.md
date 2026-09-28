---
title: "tik tak"
ctf: "Friendly CTF 2026"
date: 2026-09-28
category: web
difficulty: hard
author: "L-BOH"
---

# tik tak

## Summary

An uploaded file is deleted 60 seconds later. By requesting it as deletion happens, the error handler inserts the original filename into a Jinja template and renders it. A filename containing Jinja code then reads the flag environment variable.

## Vulnerable code

The upload path schedules removal at [src/app.py](src/app.py), line 161:

~~~python
schedule_deletion(file_id, session["id"], stored_name, delay_seconds=60)
~~~

The download endpoint deliberately waits at line 189, then catches a missing-file exception. Lines 193-196 are the SSTI sink:

~~~python
except FileNotFoundError as e:
    e.filename = original_name
    template = "<h1>error has been caught: {}</h1>".format(str(e))
    return render_template_string(template), 500
~~~

The original filename is user controlled. Assigning it to e.filename makes it part of the exception message, line 195 places that message in template source, and line 196 evaluates it as Jinja.

## Exploit

1. Register and log in.
2. Upload a file whose filename is the following value. The final .txt keeps the upload extension check happy:

~~~jinja
{{ cycler.__init__.__globals__.os.popen('printenv').read() }}.txt
~~~

3. Obtain the file ID from the profile page.
4. At about 59.5 seconds after the upload, send GET /files/FILE_ID. The endpoint sleeps for 0.5 seconds, while the deletion timer reaches 60 seconds. Retry if the race misses.
5. The request reaches open after the file has been removed. The 500 page evaluates the filename payload and prints FLAG from the environment.

The supplied [exploit.py](exploit.py) handles login, upload, file-ID lookup, and timing. Its key parts are:

- line 42 supplies the filename payload;
- lines 47-51 schedule the GET for 59.5 seconds after upload;
- lines 24-30 make the request in a background timer.

Change the command in line 42 from id to printenv to display the flag, then run it. This is a race condition: timing can vary, so repeating the final request is expected.

## Flag

~~~text
Securinets{1nter3sting_ssti_1n_3rror_7emplate}
~~~
