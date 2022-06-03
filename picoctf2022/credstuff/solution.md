# Credstuff

We want to grab the line number for the relevant username and get the
corresponding password, which we can do with:

```console
$ grep --line-number cultiris usernames.txt \
        | cut --delimiter ':' --fields 1 \
        | xargs --replace={} sed --silent '{}p' passwords.txt
cvpbPGS{P7e1S_54I35_71Z3}
```

Which looks in the correct format, and a glance is ROT13 encoded, so decoding:

```sh
$ grep --line-number cultiris usernames.txt \
         | cut --delimiter ':' --fields 1 \
         | xargs --replace={} sed --silent '{}p' passwords.txt  \
         | tr 'A-Za-z' 'N-ZA-Zn-za-m'
```
