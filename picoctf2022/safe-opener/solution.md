# Safe Opener

There's a base 64 encoded string in the source of the Java file, extract and
decode it for the flag

``` console
$ grep \
    --ignore-case 'String encodedkey = "[A-Z0-9]\+"' \
    SafeOpener.java  \
    | awk --field-separator '"' '{print $2}' | base64 --decode
```
