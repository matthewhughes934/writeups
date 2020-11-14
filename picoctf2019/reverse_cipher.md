# Reverse-Cipher

> We have recovered a binary and a text file. Can you reverse the flag.

The provided text file:

```
$ cat rev_this
picoCTF{w1{1wq84>654f26}
```

And some details on the binary:

```
$ file rev
rev: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=523d51973c11197605c76f84d4afb0fe9e59338c, not stripped
```

## Reverse Engineering The Binary

Let's run the binary through `gdb`. There looks to be some basic setup/file
reading at the start of `main`, let's inspect that

```
$ gdb ./rev
(gdb) break main
(gdb) run
(gdb) x/20i *main
   0x555555555185 <main>:	push   rbp
   0x555555555186 <main+1>:	mov    rbp,rsp
=> 0x555555555189 <main+4>:	sub    rsp,0x50
   0x55555555518d <main+8>:	lea    rsi,[rip+0xe74]        # 0x555555556008
   0x555555555194 <main+15>:	lea    rdi,[rip+0xe6f]        # 0x55555555600a
   0x55555555519b <main+22>:	call   0x555555555070 <fopen@plt>
   0x5555555551a0 <main+27>:	mov    QWORD PTR [rbp-0x18],rax
   0x5555555551a4 <main+31>:	lea    rsi,[rip+0xe68]        # 0x555555556013
   0x5555555551ab <main+38>:	lea    rdi,[rip+0xe63]        # 0x555555556015
   0x5555555551b2 <main+45>:	call   0x555555555070 <fopen@plt>
   0x5555555551b7 <main+50>:	mov    QWORD PTR [rbp-0x20],rax
   0x5555555551bb <main+54>:	cmp    QWORD PTR [rbp-0x18],0x0
   0x5555555551c0 <main+59>:	jne    0x5555555551ce <main+73>
   0x5555555551c2 <main+61>:	lea    rdi,[rip+0xe57]        # 0x555555556020
   0x5555555551c9 <main+68>:	call   0x555555555030 <puts@plt>
   0x5555555551ce <main+73>:	cmp    QWORD PTR [rbp-0x20],0x0
   0x5555555551d3 <main+78>:	jne    0x5555555551e1 <main+92>
   0x5555555551d5 <main+80>:	lea    rdi,[rip+0xe7e]        # 0x55555555605a
   0x5555555551dc <main+87>:	call   0x555555555030 <puts@plt>
   0x5555555551e1 <main+92>:	mov    rdx,QWORD PTR [rbp-0x18]
(gdb) x/s 0x555555556008
0x555555556008:	"r"
(gdb) x/s 0x55555555600a
0x55555555600a:	"flag.txt"
(gdb) x/s 0x555555556013
0x555555556013:	"a"
(gdb) x/s 0x555555556015
0x555555556015:	"rev_this"
(gdb) x/s 0x555555556020
0x555555556020:	"No flag found, please make sure this is run on the server"
(gdb) x/s 0x55555555605a
0x55555555605a:	"please run this on the server"
```

From these strings, and reading some of the instructions, it appears we start
something like:

```c
int main() {
    FILE *flag_file = fopen("flag.txt", "r");
    FILE *out_file = fopen("rev_this", "a");

    if (flag_flag == NULL)
        puts("No flag found, please make sure this is run on the server");
    if (out_file == NULL)
        puts("please run this on the server");

}
```

Also of note, we've made `0x50` bytes of room on the stack for local variables.
And for future reference:

* `flag_file` is at `rbp-0x18`
* `out_file` is at `rbp-0x20`

Glancing further ahead:

```
(gdb) x/12 *main+92
   0x5555555551e1 <main+92>:	mov    rdx,QWORD PTR [rbp-0x18]
   0x5555555551e5 <main+96>:	lea    rax,[rbp-0x50]
   0x5555555551e9 <main+100>:	mov    rcx,rdx
   0x5555555551ec <main+103>:	mov    edx,0x1
   0x5555555551f1 <main+108>:	mov    esi,0x18
   0x5555555551f6 <main+113>:	mov    rdi,rax
   0x5555555551f9 <main+116>:	call   0x555555555040 <fread@plt>
   0x5555555551fe <main+121>:	mov    DWORD PTR [rbp-0x24],eax
   0x555555555201 <main+124>:	cmp    DWORD PTR [rbp-0x24],0x0
   0x555555555205 <main+128>:	jg     0x555555555211 <main+140>
   0x555555555207 <main+130>:	mov    edi,0x0
   0x55555555520c <main+135>:	call   0x555555555080 <exit@plt>
```

Given where we stored `flag_file` this looks to be something like:

```c
    char flag[0x18];
    size_t count = fread(flag, 0x1, 0x18, flag_file);

    if (count == 0)
        exit(0);
```

Again for reference we have `flag` at `rbp-0x50`. Also note `0x18` appears to
be the length of the encoded flag we received

```
$ head -c $((0x18)) flag.txt
picoCTF{w1{1wq84>654f26}
```

Looking further ahead, it looks like there's a `for` loop:

```
(gdb) x/14 *main+140
   0x555555555211 <main+140>:	mov    DWORD PTR [rbp-0x8],0x0          # int i = 0
   0x555555555218 <main+147>:	jmp    0x55555555523d <main+184>
   0x55555555521a <main+149>:	mov    eax,DWORD PTR [rbp-0x8]
   0x55555555521d <main+152>:	cdqe
   0x55555555521f <main+154>:	movzx  eax,BYTE PTR [rbp+rax*1-0x50]    # char c = flag[i] 
   0x555555555224 <main+159>:	mov    BYTE PTR [rbp-0x1],al
   0x555555555227 <main+162>:	movsx  eax,BYTE PTR [rbp-0x1]
   0x55555555522b <main+166>:	mov    rdx,QWORD PTR [rbp-0x20]         # out_file
   0x55555555522f <main+170>:	mov    rsi,rdx
   0x555555555232 <main+173>:	mov    edi,eax
   0x555555555234 <main+175>:	call   0x555555555060 <fputc@plt>       # fputc(c, out_file)
   0x555555555239 <main+180>:	add    DWORD PTR [rbp-0x8],0x1          # i++
   0x55555555523d <main+184>:	cmp    DWORD PTR [rbp-0x8],0x7
   0x555555555241 <main+188>:	jle    0x55555555521a <main+149>        # i <= 0x7
```

Which appears to be rather simple:

```c
    for (int i = 0; i <= 0x7; i++) {
        char c = flag[i];
        putc(c, out_file);
    }
```

Assuming our flag has the normal `picoCTF{....}` structure, this would just be
printing `picoCTF{` to `rev_this`.

Looking ahead again, it appears there's another loop:

```
(gdb) x/26 *main+190
   0x555555555243 <main+190>:	mov    DWORD PTR [rbp-0xc],0x8          # int i = 0x8
   0x55555555524a <main+197>:	jmp    0x55555555528f <main+266>
   0x55555555524c <main+199>:	mov    eax,DWORD PTR [rbp-0xc]
   0x55555555524f <main+202>:	cdqe
   0x555555555251 <main+204>:	movzx  eax,BYTE PTR [rbp+rax*1-0x50]    # char c = flag[i]
   0x555555555256 <main+209>:	mov    BYTE PTR [rbp-0x1],al
   0x555555555259 <main+212>:	mov    eax,DWORD PTR [rbp-0xc]
   0x55555555525c <main+215>:	and    eax,0x1
   0x55555555525f <main+218>:	test   eax,eax
   0x555555555261 <main+220>:	jne    0x55555555526f <main+234>        # if (c % 2 == 0)
   0x555555555263 <main+222>:	movzx  eax,BYTE PTR [rbp-0x1]
   0x555555555267 <main+226>:	add    eax,0x5                          #   c += 5
   0x55555555526a <main+229>:	mov    BYTE PTR [rbp-0x1],al
   0x55555555526d <main+232>:	jmp    0x555555555279 <main+244>
   0x55555555526f <main+234>:	movzx  eax,BYTE PTR [rbp-0x1]           # else
   0x555555555273 <main+238>:	sub    eax,0x2                          #   c -= 2
   0x555555555276 <main+241>:	mov    BYTE PTR [rbp-0x1],al
   0x555555555279 <main+244>:	movsx  eax,BYTE PTR [rbp-0x1]
   0x55555555527d <main+248>:	mov    rdx,QWORD PTR [rbp-0x20]
   0x555555555281 <main+252>:	mov    rsi,rdx
   0x555555555284 <main+255>:	mov    edi,eax
   0x555555555286 <main+257>:	call   0x555555555060 <fputc@plt>       # fputc(c, out_file)
   0x55555555528b <main+262>:	add    DWORD PTR [rbp-0xc],0x1          # i++
   0x55555555528f <main+266>:	cmp    DWORD PTR [rbp-0xc],0x16
   0x555555555293 <main+270>:	jle    0x55555555524c <main+199>        # i <= 0x16
```

So this loop looks like:

```c
    for (int i = 0x8; i <= 0x16; i++) {
        char c = flag[i];
        if (c % 2 == 0)
            c += 5;
        else
            c -= 2;
        fputc(c, out_file);
    }
```

Again looking at the encoded flag we received, we see this is the actual flag section:

```
$ head -c $((0x17)) flag.txt  | tail -c $((0x16 - 0x8))
1{1wq84>654f26
```

Now we look at what's left of `main`:

```
(gdb) x/16 *main+272
   0x555555555295 <main+272>:	movzx  eax,BYTE PTR [rbp-0x39]      # char c = flag[0x18 - 1]
   0x555555555299 <main+276>:	mov    BYTE PTR [rbp-0x1],al
   0x55555555529c <main+279>:	movsx  eax,BYTE PTR [rbp-0x1]
   0x5555555552a0 <main+283>:	mov    rdx,QWORD PTR [rbp-0x20]
   0x5555555552a4 <main+287>:	mov    rsi,rdx
   0x5555555552a7 <main+290>:	mov    edi,eax
   0x5555555552a9 <main+292>:	call   0x555555555060 <fputc@plt>   # fputc(c, out_file);
   0x5555555552ae <main+297>:	mov    rax,QWORD PTR [rbp-0x20]
   0x5555555552b2 <main+301>:	mov    rdi,rax
   0x5555555552b5 <main+304>:	call   0x555555555050 <fclose@plt>  # flcose(out_file)
   0x5555555552ba <main+309>:	mov    rax,QWORD PTR [rbp-0x18]
   0x5555555552be <main+313>:	mov    rdi,rax
   0x5555555552c1 <main+316>:	call   0x555555555050 <fclose@plt>  # fclose(flag_file)
   0x5555555552c6 <main+321>:	nop
   0x5555555552c7 <main+322>:	leave
   0x5555555552c8 <main+323>:	ret
```

Which looks to just be some final writing and cleanup:

```c
    char c = flag[0x18 - 1];
    fputc(c, out_file);

    fclose(out_file);
    return fclose(flag_file);
```

So putting all we have together:

```c
#include <stdio.h>
#include <stdlib.h>

#define FLAG_LEN 24

int main()
{
    char flag[FLAG_LEN];
    char c;
    FILE *flag_file = fopen("flag.txt", "r");
    FILE *out_file = fopen("rev_this", "r");

    if (flag == NULL)
        puts("No flag found, please make sure this is run on the server");
    if (out_file == NULL)
        puts("please run this on the server");

    if (fread(flag, 1, FLAG_LEN, flag_file) == 0)
        exit(0);
    // flag = "picoCTF{<contents>}\n"

    // "picoCTF{"
    for (int i = 0; i <= 7; i++) {
        fputc(flag[i], out_file);
    }

    // <contents>
    for (int i = 8; i < FLAG_LEN - 2; i++) {
        c = flag[i];
        if (i % 2 == 0)
            c += 5;
        else
            c -=  2;
        fputc(c, out_file);
    }
    
    // "}", note we never add "\n" to out_file
    fputc(flag[FLAG_LEN - 1], out_file);
    fclose(out_file);
    return fclose(flag_file);
}
```
