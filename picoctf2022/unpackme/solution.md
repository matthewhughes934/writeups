# unpackme

Following the hint, it looks like the file is [`upx`](https://upx.github.io)
compressed:

    $ upx -l unpackme-upx
                           Ultimate Packer for eXecutables
                              Copyright (C) 1996 - 2020
    UPX git-d7ba31+ Markus Oberhumer, Laszlo Molnar & John Reiser   Jan 23rd 2020
    
            File size         Ratio      Format      Name
       --------------------   ------   -----------   -----------
       1002408 ->    379116   37.82%   linux/amd64   unpackme-upx

Unpacking and checking shows we have a non-stripped binary:

    $ upx -d unpackme-upx
    $ file unpackme-upx
    unpackme-upx: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked, BuildID[sha1]=4a81791934c743e1b0efac8efc7ffeb5af610b22, for GNU/Linux 3.2.0, not stripped

So let's poke around `main` (annotating some lines with `#` comments):

    $ objdump --disassemble --disassembler-options=intel unpackme-upx \
        | sed --quiet '/^[a-f0-9]\+ <main>/,/^$/p'
    0000000000401e73 <main>:
      401e73:	f3 0f 1e fa          	endbr64
      401e77:	55                   	push   rbp
      401e78:	48 89 e5             	mov    rbp,rsp
      401e7b:	48 83 ec 50          	sub    rsp,0x50
      401e7f:	89 7d bc             	mov    DWORD PTR [rbp-0x44],edi # argc
      401e82:	48 89 75 b0          	mov    QWORD PTR [rbp-0x50],rsi #argv
      401e86:	64 48 8b 04 25 28 00 	mov    rax,QWORD PTR fs:0x28
      401e8d:	00 00
      401e8f:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
      401e93:	31 c0                	xor    eax,eax
      401e95:	48 b8 41 3a 34 40 72 	movabs rax,0x4c75257240343a41
      401e9c:	25 75 4c
      401e9f:	48 ba 46 41 6d 6b 30 	movabs rdx,0x30623e306b6d4146
      401ea6:	3e 62 30
      401ea9:	48 89 45 d0          	mov    QWORD PTR [rbp-0x30],rax
      401ead:	48 89 55 d8          	mov    QWORD PTR [rbp-0x28],rdx
      401eb1:	48 b8 37 66 48 30 64 	movabs rax,0x6865666430486637
      401eb8:	66 65 68
      401ebb:	48 89 45 e0          	mov    QWORD PTR [rbp-0x20],rax
      401ebf:	c7 45 e8 33 64 63 36 	mov    DWORD PTR [rbp-0x18],0x36636433
      401ec6:	66 c7 45 ec 4e 00    	mov    WORD PTR [rbp-0x14],0x4e
      401ecc:	48 8d 3d 31 11 0b 00 	lea    rdi,[rip+0xb1131]        # 4b3004 <_IO_stdin_used+0x4>
      401ed3:	b8 00 00 00 00       	mov    eax,0x0
      401ed8:	e8 13 ef 00 00       	call   410df0 <_IO_printf>
      401edd:	48 8d 45 c4          	lea    rax,[rbp-0x3c]
      401ee1:	48 89 c6             	mov    rsi,rax
      401ee4:	48 8d 3d 35 11 0b 00 	lea    rdi,[rip+0xb1135]        # 4b3020 <_IO_stdin_used+0x20>, "%d"
      401eeb:	b8 00 00 00 00       	mov    eax,0x0
      401ef0:	e8 8b f0 00 00       	call   410f80 <__isoc99_scanf>  # scanf(&x, "%d")
      401ef5:	8b 45 c4             	mov    eax,DWORD PTR [rbp-0x3c]
      401ef8:	3d cb 83 0b 00       	cmp    eax,0xb83cb              # x == 0xb83cb
      401efd:	75 43                	jne    401f42 <main+0xcf>
      401eff:	48 8d 45 d0          	lea    rax,[rbp-0x30]
      401f03:	48 89 c6             	mov    rsi,rax
      401f06:	bf 00 00 00 00       	mov    edi,0x0
      401f0b:	e8 a5 fe ff ff       	call   401db5 <rotate_encrypt>  # ret = rotate_encrypt(0, [rbp-0x30])
      401f10:	48 89 45 c8          	mov    QWORD PTR [rbp-0x38],rax
      401f14:	48 8b 15 b5 d7 0d 00 	mov    rdx,QWORD PTR [rip+0xdd7b5]        # 4df6d0 <stdout>
      401f1b:	48 8b 45 c8          	mov    rax,QWORD PTR [rbp-0x38]
      401f1f:	48 89 d6             	mov    rsi,rdx
      401f22:	48 89 c7             	mov    rdi,rax
      401f25:	e8 a6 ec 01 00       	call   420bd0 <_IO_fputs>       # fputs(&ret, stdout)
      401f2a:	bf 0a 00 00 00       	mov    edi,0xa
      401f2f:	e8 3c f1 01 00       	call   421070 <putchar>         # putchar('\n')
      401f34:	48 8b 45 c8          	mov    rax,QWORD PTR [rbp-0x38]
      401f38:	48 89 c7             	mov    rdi,rax
      401f3b:	e8 80 cf 02 00       	call   42eec0 <__free>
      401f40:	eb 0c                	jmp    401f4e <main+0xdb>
      401f42:	48 8d 3d da 10 0b 00 	lea    rdi,[rip+0xb10da]        # 4b3023 <_IO_stdin_used+0x23>
      401f49:	e8 42 ef 01 00       	call   420e90 <_IO_puts>
      401f4e:	b8 00 00 00 00       	mov    eax,0x0
      401f53:	48 8b 4d f8          	mov    rcx,QWORD PTR [rbp-0x8]
      401f57:	64 48 33 0c 25 28 00 	xor    rcx,QWORD PTR fs:0x28
      401f5e:	00 00
      401f60:	74 05                	je     401f67 <main+0xf4>
      401f62:	e8 89 ae 05 00       	call   45cdf0 <__stack_chk_fail>
      401f67:	c9                   	leave
      401f68:	c3                   	ret
      401f69:	0f 1f 80 00 00 00 00 	nop    DWORD PTR [rax+0x0]

The `moveabs` calls near the start look like they might be constructing a
string, let's see how that might look (reversing because we're little
endian):

``` python
>>> parts = ("4c75257240343a41", "30623e306b6d4146", "6865666430486637", "36636433", "4e")
>>> asbytes = map(bytes.fromhex, parts)
>>> "".join(p[::-1].decode() for p in asbytes)
'A:4@r%uLFAmk0>b07fH0dfeh3dc6N'
```

Which looks like some garbage, but there is a call to `rotate_encrypt` so maybe
this is our encrypted key. So the interesting parts of `main` look something
like:

``` c
#include <stdio.h>
#include <stdlib.h>

char *rotate_encrypt(int, const char *);

int main(int argc, const char *argv[]) {
    int x;
    const char *flag = "A:4@r%uLFAmk0>b07fH0dfeh3dc6N";

    puts("What's my favorite number?");
    scanf("%d", &x);

    if (x == 0xb83cb) {
        char *result = rotate_encrypt(0, flag);
        fputs(result, stdout);
        putchar('\n');
        free(result);
    }
    return 0;
}
```

Looking now at `rotate_encrypt`:

    $ objdump --disassemble --disassembler-options=intel unpackme-upx \
        | sed --quiet '/^[a-f0-9]\+ <rotate_encrypt>/,/^$/p'
    0000000000401db5 <rotate_encrypt>:
      401db5:	f3 0f 1e fa          	endbr64
      401db9:	55                   	push   rbp
      401dba:	48 89 e5             	mov    rbp,rsp
      401dbd:	48 83 ec 30          	sub    rsp,0x30
      401dc1:	48 89 7d d8          	mov    QWORD PTR [rbp-0x28],rdi # first arg
      401dc5:	48 89 75 d0          	mov    QWORD PTR [rbp-0x30],rsi # second arg
      401dc9:	48 8b 45 d0          	mov    rax,QWORD PTR [rbp-0x30]
      401dcd:	48 89 c7             	mov    rdi,rax
      401dd0:	e8 0b f7 02 00       	call   4314e0 <__strdup>        # result = strdup(second_arg)
      401dd5:	48 89 45 f0          	mov    QWORD PTR [rbp-0x10],rax
      401dd9:	48 8b 45 f0          	mov    rax,QWORD PTR [rbp-0x10]
      401ddd:	48 89 c7             	mov    rdi,rax
      401de0:	e8 ab f3 ff ff       	call   401190 <.plt+0x170>      # strlen(result)
      401de5:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax  # *[rbp-0x8] = strlen(...)
      401de9:	48 c7 45 e8 00 00 00 	mov    QWORD PTR [rbp-0x18],0x0 # *[rbp-0x18] = i (loop variable)
      401df0:	00
      401df1:	eb 70                	jmp    401e63 <rotate_encrypt+0xae> # jmp :FOR
      401df3:	48 8b 55 f0          	mov    rdx,QWORD PTR [rbp-0x10]
      401df7:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
      401dfb:	48 01 d0             	add    rax,rdx
      401dfe:	0f b6 00             	movzx  eax,BYTE PTR [rax]
      401e01:	3c 20                	cmp    al,0x20                      # if (result[i] == 0x20)
      401e03:	7e 58                	jle    401e5d <rotate_encrypt+0xa8> # continue
      401e05:	48 8b 55 f0          	mov    rdx,QWORD PTR [rbp-0x10]
      401e09:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
      401e0d:	48 01 d0             	add    rax,rdx
      401e10:	0f b6 00             	movzx  eax,BYTE PTR [rax]
      401e13:	3c 7f                	cmp    al,0x7f                      # if (result[i] == 0x7f)
      401e15:	74 46                	je     401e5d <rotate_encrypt+0xa8> # continnue
      401e17:	48 8b 55 f0          	mov    rdx,QWORD PTR [rbp-0x10]
      401e1b:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
      401e1f:	48 01 d0             	add    rax,rdx
      401e22:	0f b6 00             	movzx  eax,BYTE PTR [rax]
      401e25:	0f be c0             	movsx  eax,al
      401e28:	83 c0 2f             	add    eax,0x2f                     # unsigned char c = result[i] + 0x2f
      401e2b:	89 45 e4             	mov    DWORD PTR [rbp-0x1c],eax
      401e2e:	83 7d e4 7e          	cmp    DWORD PTR [rbp-0x1c],0x7e
      401e32:	7e 17                	jle    401e4b <rotate_encrypt+0x96> # if (c <= 0x7e) jmp: LTE
      401e34:	8b 45 e4             	mov    eax,DWORD PTR [rbp-0x1c]
      401e37:	8d 48 a2             	lea    ecx,[rax-0x5e]
      401e3a:	48 8b 55 f0          	mov    rdx,QWORD PTR [rbp-0x10]
      401e3e:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
      401e42:	48 01 d0             	add    rax,rdx
      401e45:	89 ca                	mov    edx,ecx
      401e47:	88 10                	mov    BYTE PTR [rax],dl            # result[i] = c - 0x5e
      401e49:	eb 13                	jmp    401e5e <rotate_encrypt+0xa9>
      401e4b:	48 8b 55 f0          	mov    rdx,QWORD PTR [rbp-0x10]     # : LTE
      401e4f:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18]
      401e53:	48 01 d0             	add    rax,rdx
      401e56:	8b 55 e4             	mov    edx,DWORD PTR [rbp-0x1c]
      401e59:	88 10                	mov    BYTE PTR [rax],dl            # result[i] = c
      401e5b:	eb 01                	jmp    401e5e <rotate_encrypt+0xa9>
      401e5d:	90                   	nop
      401e5e:	48 83 45 e8 01       	add    QWORD PTR [rbp-0x18],0x1
      401e63:	48 8b 45 e8          	mov    rax,QWORD PTR [rbp-0x18] # for (int i = 0; i < strlen(second_arg); i++): FOR
      401e67:	48 3b 45 f8          	cmp    rax,QWORD PTR [rbp-0x8]
      401e6b:	72 86                	jb     401df3 <rotate_encrypt+0x3e>
      401e6d:	48 8b 45 f0          	mov    rax,QWORD PTR [rbp-0x10]
      401e71:	c9                   	leave
      401e72:	c3                   	ret

So the function looks something like:

``` c
#include <stdlib.h>
#include <string.h>

char *rotate_encrypt(int x, const char *src) {
    char *result = strdup(src);

    for (size_t i = 0; i < strlen(result); i++) {
        if (result[i] <= 0x20 || result[i] == 0x7f) {
            continue;
        }

        unsigned char c = result[i] + 0x2f;
        if (c >= 0x7e) {
            result[i] = c - 0x5e;
        } else {
            result[i] = c;
        }
    }
    return result;
}
```

Combining the two, it appears feeding the `scanf` call the decimal equivalent of
`0xb83cb` should cause the program to decrypt and print the flag.
