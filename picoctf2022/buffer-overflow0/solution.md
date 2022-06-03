# Buffer Overflow 0

There's a handler for `SIGSETV` that prints the flag and we `gets` on a `char
buf1[100]` which is then `strcpy`'d into a `buf2[16]` so giving an input \> 16
chars should trigger a segfault, yielding the flag.
