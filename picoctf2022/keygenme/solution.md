# keygenme

We're dealing with a stripped ELF

``` console
$ file ./keygenme 
./keygenme: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=68e04014a041ff448b2e7ef1693c998042ec2644, for GNU/Linux 3.2.0, stripped
```

We'll follow as we did for [`bbbbloat`](../bbbbloat/solution.md) to find `main`

``` 
$ gdb -q ./keygenme 
Reading symbols from ./keygenme...
(No debugging symbols found in ./keygenme)
(gdb) info files
Symbols from "/home/mjh/src/writeups/picoctf2022/keygenme/keygenme".
Local exec file:
	`/home/mjh/src/writeups/picoctf2022/keygenme/keygenme', file type elf64-x86-64.
	Entry point: 0x1120
	0x0000000000000318 - 0x0000000000000334 is .interp
	0x0000000000000338 - 0x0000000000000358 is .note.gnu.property
	0x0000000000000358 - 0x000000000000037c is .note.gnu.build-id
	0x000000000000037c - 0x000000000000039c is .note.ABI-tag
	0x00000000000003a0 - 0x00000000000003c8 is .gnu.hash
	0x00000000000003c8 - 0x0000000000000518 is .dynsym
	0x0000000000000518 - 0x00000000000005f3 is .dynstr
	0x00000000000005f4 - 0x0000000000000610 is .gnu.version
	0x0000000000000610 - 0x0000000000000660 is .gnu.version_r
	0x0000000000000660 - 0x0000000000000738 is .rela.dyn
	0x0000000000000738 - 0x00000000000007e0 is .rela.plt
	0x0000000000001000 - 0x000000000000101b is .init
	0x0000000000001020 - 0x00000000000010a0 is .plt
	0x00000000000010a0 - 0x00000000000010b0 is .plt.got
	0x00000000000010b0 - 0x0000000000001120 is .plt.sec
	0x0000000000001120 - 0x0000000000001595 is .text
	0x0000000000001598 - 0x00000000000015a5 is .fini
	0x0000000000002000 - 0x000000000000204a is .rodata
	0x000000000000204c - 0x0000000000002098 is .eh_frame_hdr
	0x0000000000002098 - 0x00000000000021c0 is .eh_frame
	0x0000000000003d78 - 0x0000000000003d80 is .init_array
	0x0000000000003d80 - 0x0000000000003d88 is .fini_array
	0x0000000000003d88 - 0x0000000000003f88 is .dynamic
	0x0000000000003f88 - 0x0000000000004000 is .got
	0x0000000000004000 - 0x0000000000004010 is .data
	0x0000000000004010 - 0x0000000000004020 is .bss
(gdb) x/20i 0x1120
   0x1120:	endbr64 
   0x1124:	xor    ebp,ebp
   0x1126:	mov    r9,rdx
   0x1129:	pop    rsi
   0x112a:	mov    rdx,rsp
   0x112d:	and    rsp,0xfffffffffffffff0
   0x1131:	push   rax
   0x1132:	push   rsp
   0x1133:	lea    r8,[rip+0x456]        # 0x1590
   0x113a:	lea    rcx,[rip+0x3df]        # 0x1520
   0x1141:	lea    rdi,[rip+0x343]        # 0x148b
   0x1148:	call   QWORD PTR [rip+0x2e92]        # 0x3fe0
   0x114e:	hlt    
   0x114f:	nop
   0x1150:	lea    rdi,[rip+0x2eb9]        # 0x4010 <stdin>
   0x1157:	lea    rax,[rip+0x2eb2]        # 0x4010 <stdin>
   0x115e:	cmp    rax,rdi
   0x1161:	je     0x1178
   0x1163:	mov    rax,QWORD PTR [rip+0x2e7e]        # 0x3fe8
   0x116a:	test   rax,rax
(gdb) x/20i 0x148b
   0x148b:	endbr64 
   0x148f:	push   rbp
   0x1490:	mov    rbp,rsp
   0x1493:	sub    rsp,0x40
   0x1497:	mov    DWORD PTR [rbp-0x34],edi
   0x149a:	mov    QWORD PTR [rbp-0x40],rsi
   0x149e:	mov    rax,QWORD PTR fs:0x28
   0x14a7:	mov    QWORD PTR [rbp-0x8],rax
   0x14ab:	xor    eax,eax
   0x14ad:	lea    rdi,[rip+0xb55]        # 0x2009
   0x14b4:	mov    eax,0x0
   0x14b9:	call   0x10b0 <printf@plt>
   0x14be:	mov    rdx,QWORD PTR [rip+0x2b4b]        # 0x4010 <stdin>
   0x14c5:	lea    rax,[rbp-0x30]
   0x14c9:	mov    esi,0x25
   0x14ce:	mov    rdi,rax
   0x14d1:	call   0x10d0 <fgets@plt>
   0x14d6:	lea    rax,[rbp-0x30]
   0x14da:	mov    rdi,rax
   0x14dd:	call   0x1209
```

Again, we check the first arg to what we suspect to be `__libc_start_main` (from
the `lea` at `0x1141`) and it looks like we've found main. Let's step through
`main` block by block.

``` 
$ objdump --disassemble --disassembler-options=intel ./keygenme \
    | sed --quiet '/^\s\+148b:/,/ret$/p'
    148b:	f3 0f 1e fa          	endbr64
    148f:	55                   	push   rbp
    1490:	48 89 e5             	mov    rbp,rsp
    1493:	48 83 ec 40          	sub    rsp,0x40
    1497:	89 7d cc             	mov    DWORD PTR [rbp-0x34],edi
    149a:	48 89 75 c0          	mov    QWORD PTR [rbp-0x40],rsi
    149e:	64 48 8b 04 25 28 00 	mov    rax,QWORD PTR fs:0x28
    14a5:	00 00 
    14a7:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
    14ab:	31 c0                	xor    eax,eax
    14ad:	48 8d 3d 55 0b 00 00 	lea    rdi,[rip+0xb55]
    14b4:	b8 00 00 00 00       	mov    eax,0x0
    14b9:	e8 f2 fb ff ff       	call   10b0 <printf@plt>                # printf("Enter your license key: ")
    14be:	48 8b 15 4b 2b 00 00 	mov    rdx,QWORD PTR [rip+0x2b4b]       # stdin
    14c5:	48 8d 45 d0          	lea    rax,[rbp-0x30]                   # char *license;
    14c9:	be 25 00 00 00       	mov    esi,0x25
    14ce:	48 89 c7             	mov    rdi,rax
    14d1:	e8 fa fb ff ff       	call   10d0 <fgets@plt>                 # fgets(license, 0x25, stdin)
    14d6:	48 8d 45 d0          	lea    rax,[rbp-0x30]
    14da:	48 89 c7             	mov    rdi,rax
    14dd:	e8 27 fd ff ff       	call   1209 <__stack_chk_fail@plt+0xf9> # int result = validate_license(license)
    14e2:	84 c0                	test   al,al                            # if(result == 0)
    14e4:	74 0e                	je     14f4 <__stack_chk_fail@plt+0x3e4>
    14e6:	48 8d 3d 35 0b 00 00 	lea    rdi,[rip+0xb35]
    14ed:	e8 ce fb ff ff       	call   10c0 <puts@plt>                  # puts("That key is valid.")
    14f2:	eb 0c                	jmp    1500 <__stack_chk_fail@plt+0x3f0>
    14f4:	48 8d 3d 3a 0b 00 00 	lea    rdi,[rip+0xb3a]                  # else
    14fb:	e8 c0 fb ff ff       	call   10c0 <puts@plt>                  # puts("That key is invalid.")
    1500:	b8 00 00 00 00       	mov    eax,0x0
    1505:	48 8b 4d f8          	mov    rcx,QWORD PTR [rbp-0x8]
    1509:	64 48 33 0c 25 28 00 	xor    rcx,QWORD PTR fs:0x28
    1510:	00 00 
    1512:	74 05                	je     1519
    1514:	e8 f7 fb ff ff       	call   1110
    1519:	c9                   	leave
    151a:	c3                   	ret
```

So something like:

``` C
#include <stdio>

#define LICENSE_LENGTH 0x24

int validate_license(const char *);

int main () {
    char given_license[LICENSE_LENGTH + 1];

    printf("Enter your license key: ");
    fgets(given_license, LICENSE_LENGTH + 1, stdin);

    if (verify_license(given_license) == 0) {
        puts("That key is valid");
    } else {
        puts("That key is invalid");
    }

    return 0;
}
```

I've just made some guesses about the function names. Let's look at the function
that appears to validate the license we pass in:

``` 
$ objdump --disassemble --disassembler-options=intel ./keygenme \
    | sed --quiet '/^\s\+1209:/,/ret$/p'
    1209:	f3 0f 1e fa          	endbr64
    120d:	55                   	push   rbp
    120e:	48 89 e5             	mov    rbp,rsp
    1211:	48 81 ec e0 00 00 00 	sub    rsp,0xe0
    1218:	48 89 bd 28 ff ff ff 	mov    QWORD PTR [rbp-0xd8],rdi         # const char *license -> rbp-0xd8
    121f:	64 48 8b 04 25 28 00 	mov    rax,QWORD PTR fs:0x28
    1226:	00 00 
    1228:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
    122c:	31 c0                	xor    eax,eax
    122e:	48 b8 70 69 63 6f 43 	movabs rax,0x7b4654436f636970
    1235:	54 46 7b 
    1238:	48 ba 62 72 31 6e 67 	movabs rdx,0x30795f676e317262
    123f:	5f 79 30 
    1242:	48 89 85 70 ff ff ff 	mov    QWORD PTR [rbp-0x90],rax
    1249:	48 89 95 78 ff ff ff 	mov    QWORD PTR [rbp-0x88],rdx
    1250:	48 b8 75 72 5f 30 77 	movabs rax,0x6b5f6e77305f7275
    1257:	6e 5f 6b 
    125a:	48 89 45 80          	mov    QWORD PTR [rbp-0x80],rax
    125e:	c7 45 88 33 79 5f 00 	mov    DWORD PTR [rbp-0x78],0x5f7933
    1265:	66 c7 85 4e ff ff ff 	mov    WORD PTR [rbp-0xb2],0x7d
    126c:	7d 00 
    126e:	48 8d 85 70 ff ff ff 	lea    rax,[rbp-0x90]
    1275:	48 89 c7             	mov    rdi,rax
    1278:	e8 63 fe ff ff       	call   10e0 <strlen@plt>                # size_t len = strlen("picoCTF{br1ng_y0ur_0wn_k3y_")
    127d:	48 89 c1             	mov    rcx,rax
    1280:	48 8d 95 50 ff ff ff 	lea    rdx,[rbp-0xb0]                   # unsigned char *dest = &rbp-0xb0
    1287:	48 8d 85 70 ff ff ff 	lea    rax,[rbp-0x90]
    128e:	48 89 ce             	mov    rsi,rcx
    1291:	48 89 c7             	mov    rdi,rax
    1294:	e8 57 fe ff ff       	call   10f0 <MD5@plt>                   # MD5("picoCTF{br1ng_y0ur_0wn_k3y_", len, dest);
    1299:	48 8d 85 4e ff ff ff 	lea    rax,[rbp-0xb2]
    12a0:	48 89 c7             	mov    rdi,rax
    12a3:	e8 38 fe ff ff       	call   10e0 <strlen@plt>                # size_t other_len = strlen("}")
    12a8:	48 89 c1             	mov    rcx,rax
    12ab:	48 8d 95 60 ff ff ff 	lea    rdx,[rbp-0xa0]                   # unsifned char *other_dest = &rbp-0xa0
    12b2:	48 8d 85 4e ff ff ff 	lea    rax,[rbp-0xb2]
    12b9:	48 89 ce             	mov    rsi,rcx
    12bc:	48 89 c7             	mov    rdi,rax
    12bf:	e8 2c fe ff ff       	call   10f0 <MD5@plt>                   # MD5("}", other_len, other_dest)
    12c4:	c7 85 38 ff ff ff 00 	mov    DWORD PTR [rbp-0xc8],0x0         # int j = 0
    12cb:	00 00 00 
    12ce:	c7 85 3c ff ff ff 00 	mov    DWORD PTR [rbp-0xc4],0x0         # in i = 0
    12d5:	00 00 00 
    12d8:	eb 47                	jmp    1321 <__stack_chk_fail@plt+0x211>
    12da:	8b 85 3c ff ff ff    	mov    eax,DWORD PTR [rbp-0xc4]         # (for i, j; i <= 0xf; i++, j += 2)
    12e0:	48 98                	cdqe
    12e2:	0f b6 84 05 50 ff ff 	movzx  eax,BYTE PTR [rbp+rax*1-0xb0]    # dest + i
    12e9:	ff 
    12ea:	0f b6 c0             	movzx  eax,al
    12ed:	48 8d 4d 90          	lea    rcx,[rbp-0x70]                   # char *s = &rbp-0x70
    12f1:	8b 95 38 ff ff ff    	mov    edx,DWORD PTR [rbp-0xc8]
    12f7:	48 63 d2             	movsxd rdx,edx
    12fa:	48 01 d1             	add    rcx,rdx                          # s + j
    12fd:	89 c2                	mov    edx,eax
    12ff:	48 8d 35 fe 0c 00 00 	lea    rsi,[rip+0xcfe]                  # "%02x"
    1306:	48 89 cf             	mov    rdi,rcx
    1309:	b8 00 00 00 00       	mov    eax,0x0
    130e:	e8 ed fd ff ff       	call   1100 <sprintf@plt>               # sprintf(s + j, "%02x", dest + i)
    1313:	83 85 3c ff ff ff 01 	add    DWORD PTR [rbp-0xc4],0x1         # i++
    131a:	83 85 38 ff ff ff 02 	add    DWORD PTR [rbp-0xc8],0x2         # j += 2
    1321:	83 bd 3c ff ff ff 0f 	cmp    DWORD PTR [rbp-0xc4],0xf
    1328:	7e b0                	jle    12da <__stack_chk_fail@plt+0x1ca>
    132a:	c7 85 38 ff ff ff 00 	mov    DWORD PTR [rbp-0xc8],0x0         # j = 0
    1331:	00 00 00 
    1334:	c7 85 40 ff ff ff 00 	mov    DWORD PTR [rbp-0xc0],0x0         # i = 0
    133b:	00 00 00 
    133e:	eb 47                	jmp    1387 <__stack_chk_fail@plt+0x277>
    1340:	8b 85 40 ff ff ff    	mov    eax,DWORD PTR [rbp-0xc0]         # for(i, j; i <= 0xf; i++, j+=2)
    1346:	48 98                	cdqe
    1348:	0f b6 84 05 60 ff ff 	movzx  eax,BYTE PTR [rbp+rax*1-0xa0]    # other_dest + i
    134f:	ff 
    1350:	0f b6 c0             	movzx  eax,al
    1353:	48 8d 4d b0          	lea    rcx,[rbp-0x50]                   # char *s = &rbp-0x50
    1357:	8b 95 38 ff ff ff    	mov    edx,DWORD PTR [rbp-0xc8]
    135d:	48 63 d2             	movsxd rdx,edx
    1360:	48 01 d1             	add    rcx,rdx
    1363:	89 c2                	mov    edx,eax
    1365:	48 8d 35 98 0c 00 00 	lea    rsi,[rip+0xc98]                  # "%02x"
    136c:	48 89 cf             	mov    rdi,rcx
    136f:	b8 00 00 00 00       	mov    eax,0x0
    1374:	e8 87 fd ff ff       	call   1100 <sprintf@plt>               # sprintf(s + j, "%02x", other_dest + i)
    1379:	83 85 40 ff ff ff 01 	add    DWORD PTR [rbp-0xc0],0x1         # i++
    1380:	83 85 38 ff ff ff 02 	add    DWORD PTR [rbp-0xc8],0x2         # j+=2
    1387:	83 bd 40 ff ff ff 0f 	cmp    DWORD PTR [rbp-0xc0],0xf
    138e:	7e b0                	jle    1340 <__stack_chk_fail@plt+0x230>
    1390:	c7 85 44 ff ff ff 00 	mov    DWORD PTR [rbp-0xbc],0x0         # i = 0
    1397:	00 00 00 
    139a:	eb 23                	jmp    13bf <__stack_chk_fail@plt+0x2af>
    139c:	8b 85 44 ff ff ff    	mov    eax,DWORD PTR [rbp-0xbc]         # for(i; i <= 0x1a; i++)
    13a2:	48 98                	cdqe
    13a4:	0f b6 94 05 70 ff ff 	movzx  edx,BYTE PTR [rbp+rax*1-0x90]    # char *s = "picoCTF{br1ng_y0ur_0wn_k3y_"
    13ab:	ff 
    13ac:	8b 85 44 ff ff ff    	mov    eax,DWORD PTR [rbp-0xbc]
    13b2:	48 98                	cdqe
    13b4:	88 54 05 d0          	mov    BYTE PTR [rbp+rax*1-0x30],dl     # x[i] = s[i]
    13b8:	83 85 44 ff ff ff 01 	add    DWORD PTR [rbp-0xbc],0x1         # i++
    13bf:	83 bd 44 ff ff ff 1a 	cmp    DWORD PTR [rbp-0xbc],0x1a        # at end of loop: "picoCTF{br1ng_y0ur_0wn_k3y_" now in $rbp-0x30
    13c6:	7e d4                	jle    139c <__stack_chk_fail@plt+0x28c>
    13c8:	0f b6 45 a2          	movzx  eax,BYTE PTR [rbp-0x5e]          # the hex of the MD5 sums are bwetween rbp-0x70 and rbp-0x30
    13cc:	88 45 eb             	mov    BYTE PTR [rbp-0x15],al           # so this chunk is taking various bytes from that and appending
    13cf:	0f b6 45 aa          	movzx  eax,BYTE PTR [rbp-0x56]          # to the license
    13d3:	88 45 ec             	mov    BYTE PTR [rbp-0x14],al
    13d6:	0f b6 45 a9          	movzx  eax,BYTE PTR [rbp-0x57]
    13da:	88 45 ed             	mov    BYTE PTR [rbp-0x13],al
    13dd:	0f b6 45 90          	movzx  eax,BYTE PTR [rbp-0x70]
    13e1:	88 45 ee             	mov    BYTE PTR [rbp-0x12],al
    13e4:	0f b6 45 aa          	movzx  eax,BYTE PTR [rbp-0x56]
    13e8:	88 45 ef             	mov    BYTE PTR [rbp-0x11],al
    13eb:	0f b6 45 a2          	movzx  eax,BYTE PTR [rbp-0x5e]
    13ef:	88 45 f0             	mov    BYTE PTR [rbp-0x10],al
    13f2:	0f b6 45 9c          	movzx  eax,BYTE PTR [rbp-0x64]
    13f6:	88 45 f1             	mov    BYTE PTR [rbp-0xf],al
    13f9:	0f b6 45 aa          	movzx  eax,BYTE PTR [rbp-0x56]
    13fd:	88 45 f2             	mov    BYTE PTR [rbp-0xe],al
    1400:	0f b6 85 4e ff ff ff 	movzx  eax,BYTE PTR [rbp-0xb2]
    1407:	88 45 f3             	mov    BYTE PTR [rbp-0xd],al
    140a:	48 8b 85 28 ff ff ff 	mov    rax,QWORD PTR [rbp-0xd8]
    1411:	48 89 c7             	mov    rdi,rax
    1414:	e8 c7 fc ff ff       	call   10e0 <strlen@plt>            # size_t len = strlen(license)
    1419:	48 83 f8 24          	cmp    rax,0x24                     # if (len == 0x24)
    141d:	74 07                	je     1426 <__stack_chk_fail@plt+0x316>
    141f:	b8 00 00 00 00       	mov    eax,0x0
    1424:	eb 4f                	jmp    1475 <__stack_chk_fail@plt+0x365>
    1426:	c7 85 48 ff ff ff 00 	mov    DWORD PTR [rbp-0xb8],0x0     # i = 0
    142d:	00 00 00 
    1430:	eb 35                	jmp    1467 <__stack_chk_fail@plt+0x357>
    1432:	8b 85 48 ff ff ff    	mov    eax,DWORD PTR [rbp-0xb8]     # for (i; i <= 0x23; i++)
    1438:	48 63 d0             	movsxd rdx,eax
    143b:	48 8b 85 28 ff ff ff 	mov    rax,QWORD PTR [rbp-0xd8]
    1442:	48 01 d0             	add    rax,rdx
    1445:	0f b6 10             	movzx  edx,BYTE PTR [rax]
    1448:	8b 85 48 ff ff ff    	mov    eax,DWORD PTR [rbp-0xb8]
    144e:	48 98                	cdqe
    1450:	0f b6 44 05 d0       	movzx  eax,BYTE PTR [rbp+rax*1-0x30]
    1455:	38 c2                	cmp    dl,al                        # if (license[i] == true_license[i])
    1457:	74 07                	je     1460 <__stack_chk_fail@plt+0x350>
    1459:	b8 00 00 00 00       	mov    eax,0x0                      # return 0
    145e:	eb 15                	jmp    1475 <__stack_chk_fail@plt+0x365>
    1460:	83 85 48 ff ff ff 01 	add    DWORD PTR [rbp-0xb8],0x1
    1467:	83 bd 48 ff ff ff 23 	cmp    DWORD PTR [rbp-0xb8],0x23
    146e:	7e c2                	jle    1432 <__stack_chk_fail@plt+0x322>
    1470:	b8 01 00 00 00       	mov    eax,0x1                      # else return 1
    1475:	48 8b 75 f8          	mov    rsi,QWORD PTR [rbp-0x8]
    1479:	64 48 33 34 25 28 00 	xor    rsi,QWORD PTR fs:0x28
    1480:	00 00 
    1482:	74 05                	je     1489 <__stack_chk_fail@plt+0x379>
    1484:	e8 87 fc ff ff       	call   1110 <__stack_chk_fail@plt>
    1489:	c9                   	leave
    148a:	c3                   	ret
```

We can see the string at the very start of the function being built up,
reconstructing the data from the `movabs` instructions there:

``` python

>>> parts = ("7b4654436f636970", "30795f676e317262", "6b5f6e77305f7275", "5f7933")
>>> asbytes = map(bytes.fromhex, parts)
>>> "".join(p[::-1].decode() for p in asbytes)
'picoCTF{br1ng_y0ur_0wn_k3y_'
```

Then converting this function to C we get something like:

``` C
#include <stdio.h>
#include <string.h>
#include <openssl/md5.h>

#define LICENSE_LENGTH 0x24

int verify_license(const char *given_license)
{
    unsigned char true_license[LICENSE_LENGTH];
    unsigned char first_sum[MD5_DIGEST_LENGTH];
    unsigned char second_sum[MD5_DIGEST_LENGTH];
    unsigned char sum_hexes[4 * MD5_DIGEST_LENGTH];
    unsigned char *first_sum_hex = sum_hexes;
    unsigned char *second_sum_hex = sum_hexes + 2 * MD5_DIGEST_LENGTH;
    const char *first_part = "picoCTF{br1ng_y0ur_0wn_k3y_";
    const char *second_part = "}";

    MD5(first_part, strlen(first_part), first_sum);
    MD5(second_part, strlen(second_part), second_sum);

    for (int i = 0, j = 0; i <= MD5_DIGEST_LENGTH; i++, j += 2) {
        sprintf(first_sum_hex + j, "%02x", first_sum[i]);
    }
    for (int i = 0, j = 0; i <= MD5_DIGEST_LENGTH; i++, j += 2) {
        sprintf(second_sum_hex + j, "%02x", second_sum[i]);
    }
    for (int i = 0; i < strlen(first_part); i++) {
        true_license[i] = first_part[i];
    }
    char *license_tail = true_license + strlen(first_part);
    license_tail[0] = sum_hexes[0x12];
    license_tail[1] = sum_hexes[0x1a];
    license_tail[2] = sum_hexes[0x19];
    license_tail[3] = sum_hexes[0];
    license_tail[4] = sum_hexes[0x1a];
    license_tail[5] = sum_hexes[0x12];
    license_tail[6] = sum_hexes[0xc];
    license_tail[7] = sum_hexes[0x1a];
    license_tail[8] = second_part[0];

    if (strlen(given_license) != strlen(true_license)) {
        return 1;
    }

    for (int i = 0; i < LICENSE_LENGTH; i++) {
        if (given_license[i] != true_license[i]) {
            return 1;
        }
    }
    return 0;
}
```

Which can be used to extract the valid license. Or you could just step through
the program with a long-enough license to the end of that function and read the
value from memory at `$rbp-0x30`
