# Roboto Sans

Inspecting `robots.txt` we find:

```console
$ curl http://saturn.picoctf.net:64710/robots.txt
User-agent *
Disallow: /cgi-bin/
Think you have seen your flag or want to keep looking.

ZmxhZzEudHh0;anMvbXlmaW
anMvbXlmaWxlLnR4dA==
svssshjweuiwl;oiho.bsvdaslejg
Disallow: /wp-admin
```

From the base64 encoded string we can find an interesting path.
