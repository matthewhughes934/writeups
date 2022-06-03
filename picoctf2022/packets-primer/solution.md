# Packets Primer

Inspect the raw `.pcap` file with e.g. `xxd` we see that the flag is available
in plaintext, but with spaces separating the characters, so we can strip the
spaces and read it directly:

``` console
$ tr --delete ' ' < network-dump.flag.pcap \
    | grep --text --only-matching 'picoCTF{.*}'
```
