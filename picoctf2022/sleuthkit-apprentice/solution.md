# Sleuthkit Apprentice

Extracting the flag an inspecting:

```console
$ mmls disk.flag.img 
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0000206847   0000204800   Linux (0x83)
003:  000:001   0000206848   0000360447   0000153600   Linux Swap / Solaris x86 (0x82)
004:  000:002   0000360448   0000614399   0000253952   Linux (0x83)
```

Inspecting one of these:

```console
$ fls -F -r -o 0000360448 disk.flag.img  | grep flag
r/r * 2082(realloc):	root/my_folder/flag.txt
r/r 2371:	root/my_folder/flag.uni.txt
```

Then we can recover the file:

```console
$ fcat -o 0000360448 /root/my_folder/flag.uni.txt disk.flag.img
```
