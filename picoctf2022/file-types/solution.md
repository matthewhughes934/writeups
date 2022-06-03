# File Types

The original file is a `shar` file, on Arch we can grab `sharutils` to work with
this. This places an `ar` archive at `file`

```
$ sh Flag.pdf
```

Then working down the chain (making much use of `file -`) to determine the file
type each time:

```console
$ ar p flag \
        | cpio -i --to-stdout 2>/dev/null \
        | bunzip2 - \
        | gunzip - \
        | lzip --stdout --decompress - \
        | lz4 -d - \
        | unlzma - \
        | lzop -d - \
        | lzip --stdout --decompress - \
        | xzcat - \
        | tr --delete '\n' \
        | fold --width 2 \
        | xxd -r -p
```
