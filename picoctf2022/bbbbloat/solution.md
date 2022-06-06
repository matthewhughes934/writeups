# bbbbloat

We're dealing with a stripped binary:

``` console
$ file ./bbbbloat 
./bbbbloat: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=affb0d5630122ba0717a50d579952a83278e727c, for GNU/Linux 3.2.0, stripped
```

[Here's](https://www.youtube.com/watch?v=N1US3c6CpSw) a good video on how to
find the entry point in such case. Let's give it a shot:

``` 
$ gdb -q ./bbbbloat 
Reading symbols from ./bbbbloat...
(No debugging symbols found in ./bbbbloat)
(gdb) info files
Symbols from "/home/mjh/src/writeups/picoctf2022/bbbbloat/bbbbloat".
Local exec file:
	`/home/mjh/src/writeups/picoctf2022/bbbbloat/bbbbloat', file type elf64-x86-64.
	Entry point: 0x1160
	0x0000000000000318 - 0x0000000000000334 is .interp
	0x0000000000000338 - 0x0000000000000358 is .note.gnu.property
	0x0000000000000358 - 0x000000000000037c is .note.gnu.build-id
	0x000000000000037c - 0x000000000000039c is .note.ABI-tag
	0x00000000000003a0 - 0x00000000000003c8 is .gnu.hash
	0x00000000000003c8 - 0x0000000000000548 is .dynsym
	0x0000000000000548 - 0x0000000000000628 is .dynstr
	0x0000000000000628 - 0x0000000000000648 is .gnu.version
	0x0000000000000648 - 0x0000000000000688 is .gnu.version_r
	0x0000000000000688 - 0x0000000000000760 is .rela.dyn
	0x0000000000000760 - 0x0000000000000838 is .rela.plt
	0x0000000000001000 - 0x000000000000101b is .init
	0x0000000000001020 - 0x00000000000010c0 is .plt
	0x00000000000010c0 - 0x00000000000010d0 is .plt.got
	0x00000000000010d0 - 0x0000000000001160 is .plt.sec
	0x0000000000001160 - 0x0000000000001625 is .text
	0x0000000000001628 - 0x0000000000001635 is .fini
	0x0000000000002000 - 0x0000000000002039 is .rodata
	0x000000000000203c - 0x0000000000002088 is .eh_frame_hdr
	0x0000000000002088 - 0x00000000000021b0 is .eh_frame
	0x0000000000003d78 - 0x0000000000003d80 is .init_array
	0x0000000000003d80 - 0x0000000000003d88 is .fini_array
	0x0000000000003d88 - 0x0000000000003f78 is .dynamic
	0x0000000000003f78 - 0x0000000000004000 is .got
	0x0000000000004000 - 0x0000000000004010 is .data
	0x0000000000004010 - 0x0000000000004020 is .bss
```

We see there's an entrypoint at `0x1160`, inspecting:

``` 
(gdb) x/20i 0x1160
   0x1160:	endbr64 
   0x1164:	xor    ebp,ebp
   0x1166:	mov    r9,rdx
   0x1169:	pop    rsi
   0x116a:	mov    rdx,rsp
   0x116d:	and    rsp,0xfffffffffffffff0
   0x1171:	push   rax
   0x1172:	push   rsp
   0x1173:	lea    r8,[rip+0x4a6]        # 0x1620
   0x117a:	lea    rcx,[rip+0x42f]        # 0x15b0
   0x1181:	lea    rdi,[rip+0x17f]        # 0x1307
   0x1188:	call   QWORD PTR [rip+0x2e52]        # 0x3fe0
   0x118e:	hlt    
   0x118f:	nop
   0x1190:	lea    rdi,[rip+0x2e79]        # 0x4010 <stdout>
   0x1197:	lea    rax,[rip+0x2e72]        # 0x4010 <stdout>
   0x119e:	cmp    rax,rdi
   0x11a1:	je     0x11b8
   0x11a3:	mov    rax,QWORD PTR [rip+0x2e2e]        # 0x3fd8
   0x11aa:	test   rax,rax
```

The `call` instruction at `0x1188` seems like a good candidate to a call to
`__libc_start_main`. Let's make an educated guess an assume that's the case.
Given that, we expected `main` to be at `0x1307`, and again inspecting:

``` 
(gdb) x/20i 0x1307
   0x1307:	endbr64 
   0x130b:	push   rbp
   0x130c:	mov    rbp,rsp
   0x130f:	sub    rsp,0x50
   0x1313:	mov    DWORD PTR [rbp-0x44],edi
   0x1316:	mov    QWORD PTR [rbp-0x50],rsi
   0x131a:	mov    rax,QWORD PTR fs:0x28
   0x1323:	mov    QWORD PTR [rbp-0x8],rax
   0x1327:	xor    eax,eax
   0x1329:	movabs rax,0x4c75257240343a41
   0x1333:	movabs rdx,0x3062396630664634
   0x133d:	mov    QWORD PTR [rbp-0x30],rax
   0x1341:	mov    QWORD PTR [rbp-0x28],rdx
   0x1345:	movabs rax,0x63633066635f3d33
   0x134f:	movabs rdx,0x4e5f6532636637
   0x1359:	mov    QWORD PTR [rbp-0x20],rax
   0x135d:	mov    QWORD PTR [rbp-0x18],rdx
   0x1361:	mov    DWORD PTR [rbp-0x3c],0x3078
   0x1368:	add    DWORD PTR [rbp-0x3c],0x13c29e
   0x136f:	sub    DWORD PTR [rbp-0x3c],0x30a8
```

Which at least looks like a function call. Let's start the program so we have
some more details once libraries are loaded and poke around a bit:

``` 
(gdb) b __libc_start_main
Function "__libc_start_main" not defined.
Make breakpoint pending on future shared library load? (y or [n]) y
Breakpoint 1 (__libc_start_main) pending.
(gdb) run
Breakpoint 1, 0x00007ffff7dba2c0 in __libc_start_main () from /usr/lib/libc.so.6
(gdb) bt
# From above, the first arg to __libc_start_main was loaded into $rdi
(gdb) b *$rdi
Breakpoint 2 at 0x555555555307
(gdb) c
Continuing.

Breakpoint 2, 0x0000555555555307 in ?? ()
```

Now we have some symbols from the standard library we can look around try and
find some useful bits (as the name suggests, we expect quite a bit of bloat
before finding these interesting bits). After poking around we see something
interesting:

``` 
(gdb) x/10i $rip+200
   0x5555555553cf:	or     al,0x0
   0x5555555553d1:	add    BYTE PTR [rax+0x0],bh
   0x5555555553d7:	call   0x555555555120 <printf@plt>
   0x5555555553dc:	mov    DWORD PTR [rbp-0x3c],0x3078
   0x5555555553e3:	add    DWORD PTR [rbp-0x3c],0x13c29e
   0x5555555553ea:	sub    DWORD PTR [rbp-0x3c],0x30a8
   0x5555555553f1:	shl    DWORD PTR [rbp-0x3c],1
   0x5555555553f4:	mov    eax,DWORD PTR [rbp-0x3c]
   0x5555555553f7:	movsxd rdx,eax
   0x5555555553fa:	imul   rdx,rdx,0x55555556
```

And later:

``` 
(gdb) x/10i $rip+320
   0x555555555447:	lea    eax,[rbp-0x40]
   0x55555555544a:	mov    rsi,rax
   0x55555555544d:	lea    rdi,[rip+0xbcc]        # 0x555555556020
   0x555555555454:	mov    eax,0x0
   0x555555555459:	call   0x555555555140 <__isoc99_scanf@plt>
   0x55555555545e:	mov    DWORD PTR [rbp-0x3c],0x3078
   0x555555555465:	add    DWORD PTR [rbp-0x3c],0x13c29e
   0x55555555546c:	sub    DWORD PTR [rbp-0x3c],0x30a8
   0x555555555473:	shl    DWORD PTR [rbp-0x3c],1
   0x555555555476:	mov    eax,DWORD PTR [rbp-0x3c]
```

Inspecting around this `scanf` call:

``` 
(gdb) x/35i $rip+320
   0x555555555447:	lea    eax,[rbp-0x40]
   0x55555555544a:	mov    rsi,rax
   0x55555555544d:	lea    rdi,[rip+0xbcc]        # 0x555555556020
   0x555555555454:	mov    eax,0x0
   0x555555555459:	call   0x555555555140 <__isoc99_scanf@plt>
   0x55555555545e:	mov    DWORD PTR [rbp-0x3c],0x3078
   0x555555555465:	add    DWORD PTR [rbp-0x3c],0x13c29e
   0x55555555546c:	sub    DWORD PTR [rbp-0x3c],0x30a8
   0x555555555473:	shl    DWORD PTR [rbp-0x3c],1
   0x555555555476:	mov    eax,DWORD PTR [rbp-0x3c]
   0x555555555479:	movsxd rdx,eax
   0x55555555547c:	imul   rdx,rdx,0x55555556
   0x555555555483:	shr    rdx,0x20
   0x555555555487:	sar    eax,0x1f
   0x55555555548a:	mov    esi,edx
   0x55555555548c:	sub    esi,eax
   0x55555555548e:	mov    eax,esi
   0x555555555490:	mov    DWORD PTR [rbp-0x3c],eax
   0x555555555493:	mov    DWORD PTR [rbp-0x3c],0x3078
   0x55555555549a:	add    DWORD PTR [rbp-0x3c],0x13c29e
   0x5555555554a1:	sub    DWORD PTR [rbp-0x3c],0x30a8
   0x5555555554a8:	shl    DWORD PTR [rbp-0x3c],1
   0x5555555554ab:	mov    eax,DWORD PTR [rbp-0x3c]
   0x5555555554ae:	movsxd rdx,eax
   0x5555555554b1:	imul   rdx,rdx,0x55555556
   0x5555555554b8:	shr    rdx,0x20
   0x5555555554bc:	sar    eax,0x1f
   0x5555555554bf:	mov    edi,edx
   0x5555555554c1:	sub    edi,eax
   0x5555555554c3:	mov    eax,edi
   0x5555555554c5:	mov    DWORD PTR [rbp-0x3c],eax
   0x5555555554c8:	mov    eax,DWORD PTR [rbp-0x40]
   0x5555555554cb:	cmp    eax,0x86187
   0x5555555554d0:	jne    0x555555555583
   0x5555555554d6:	mov    DWORD PTR [rbp-0x3c],0x3078
```

In particular the instruction `0x5555555554cb: cmp eax,0x86187`. Breaking things
down, we have our call

``` 
   0x555555555447:	lea    eax,[rbp-0x40]
   0x55555555544a:	mov    rsi,rax
   0x55555555544d:	lea    rdi,[rip+0xbcc]        # 0x555555556020
   0x555555555454:	mov    eax,0x0
   0x555555555459:	call   0x555555555140 <__isoc99_scanf@plt>
```

Which is something like `scanf("%d", &my_int)` so we expect the scanned in
number to be read into the address at `$rbp-0x40`. Then our comparison:

``` 
   0x5555555554c8:	mov    eax,DWORD PTR [rbp-0x40]
   0x5555555554cb:	cmp    eax,0x86187
   0x5555555554d0:	jne    0x555555555583
```

So we compare what's in the address pointed at by `$rbp-0x40` with `0x86187`.
But despite there being plenty of instructions between the `scanf` call and this
comparison, none of them touch `$rbp-0x40` so it looks like we're just comparing
directly on the value we read it. Running with this guess we try:

``` 
$ python -c 'print(0x86187)' | ./bbbbloat
```

And get the flag directly.
