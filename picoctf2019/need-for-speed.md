# Need For Speed

> The name of the game is speed. Are you quick enough to solve this problem and
> keep it above 50 mph?

## Reassembling

First, let's try and (roughly) reassemble some functions, using `objdump -dM
intel` to read them (note that `flag` and `key` are stored as globals:

### `calculate_key`

```
0000000000000841 <calculate_key>:
 841:   55                      push   rbp
 842:   48 89 e5                mov    rbp,rsp
 845:   c7 45 fc 1c 07 c2 d8    mov    DWORD PTR [rbp-0x4],0xd8c2071c
 84c:   83 6d fc 01             sub    DWORD PTR [rbp-0x4],0x1
 850:   81 7d fc 8e 03 61 ec    cmp    DWORD PTR [rbp-0x4],0xec61038e
 857:   75 f3                   jne    84c <calculate_key+0xb>
 859:   8b 45 fc                mov    eax,DWORD PTR [rbp-0x4]
 85c:   5d                      pop    rbp
 85d:   c3                      ret
```

```c
int calculate_key() {
    int key = 0xd8c2071c;
    do {
        key--;
    } while (key != 0xec61038e);
    return key;
}
```

### `set_timer`

```
000000000000087f <set_timer>:
 87f:   55                      push   rbp
 880:   48 89 e5                mov    rbp,rsp
 883:   48 83 ec 10             sub    rsp,0x10
 887:   c7 45 f4 01 00 00 00    mov    DWORD PTR [rbp-0xc],0x1
 88e:   48 8d 35 c9 ff ff ff    lea    rsi,[rip+0xffffffffffffffc9]        # 85e <alarm_handler>
 895:   bf 0e 00 00 00          mov    edi,0xe
 89a:   e8 e1 fd ff ff          call   680 <__sysv_signal@plt>
 89f:   48 89 45 f8             mov    QWORD PTR [rbp-0x8],rax
 8a3:   48 83 7d f8 ff          cmp    QWORD PTR [rbp-0x8],0xffffffffffffffff
 8a8:   75 20                   jne    8ca <set_timer+0x4b>
 8aa:   be 3c 00 00 00          mov    esi,0x3c
 8af:   48 8d 3d b2 01 00 00    lea    rdi,[rip+0x1b2]        # a68 <_IO_stdin_used+0x28>
 8b6:   b8 00 00 00 00          mov    eax,0x0
 8bb:   e8 a0 fd ff ff          call   660 <printf@plt>
 8c0:   bf 00 00 00 00          mov    edi,0x0
 8c5:   e8 c6 fd ff ff          call   690 <exit@plt>
 8ca:   8b 45 f4                mov    eax,DWORD PTR [rbp-0xc]
 8cd:   89 c7                   mov    edi,eax
 8cf:   e8 9c fd ff ff          call   670 <alarm@plt>
 8d4:   90                      nop
 8d5:   c9                      leave
 8d6:   c3                      ret
```

```c
void set_timer() {
    void (*handler)(int) = &alarm_handler;

    // 0xe = SIGALRM
    // Note: __sysv_signal() is the binary standard, source standard is
    // signal(), see:
    // https://refspecs.linuxfoundation.org/LSB_5.0.0/LSB-Core-generic/LSB-Core-generic/baselib---sysv-signal-1.html

    if (signal(SIGALRM, handler) == SIG_ERR) {
        printf("\n\nSomething bad happened here...\n");
        exit(0);
    }
    alarm(1);
}
```

### `alarm_handler`

```
000000000000085e <alarm_handler>:
 85e:   55                      push   rbp
 85f:   48 89 e5                mov    rbp,rsp
 862:   48 83 ec 10             sub    rsp,0x10
 866:   89 7d fc                mov    DWORD PTR [rbp-0x4],edi
 869:   48 8d 3d e0 01 00 00    lea    rdi,[rip+0x1e0]        # a50 <_IO_stdin_used+0x10>
 870:   e8 db fd ff ff          call   650 <puts@plt>
 875:   bf 00 00 00 00          mov    edi,0x0
 87a:   e8 11 fe ff ff          call   690 <exit@plt>
```

```c
void alarm_handler(int sig) {
    puts("Not fast enough. BOOM!");
    exit(0);
}
```

### `header`

```
0000000000000932 <header>:
 932:   55                      push   rbp
 933:   48 89 e5                mov    rbp,rsp
 936:   48 83 ec 10             sub    rsp,0x10
 93a:   48 8d 3d cf 01 00 00    lea    rdi,[rip+0x1cf]        # b10 <title>
 941:   e8 0a fd ff ff          call   650 <puts@plt>
 946:   c7 45 fc 00 00 00 00    mov    DWORD PTR [rbp-0x4],0x0
 94d:   eb 0e                   jmp    95d <header+0x2b>
 94f:   bf 3d 00 00 00          mov    edi,0x3d
 954:   e8 e7 fc ff ff          call   640 <putchar@plt>
 959:   83 45 fc 01             add    DWORD PTR [rbp-0x4],0x1
 95d:   8b 45 fc                mov    eax,DWORD PTR [rbp-0x4]
 960:   83 f8 1b                cmp    eax,0x1b
 963:   76 ea                   jbe    94f <header+0x1d>
 965:   48 8d 3d c1 01 00 00    lea    rdi,[rip+0x1c1]        # b2d <title+0x1d>
 96c:   e8 df fc ff ff          call   650 <puts@plt>
 971:   90                      nop
 972:   c9                      leave
 973:   c3                      ret
```

```c
void header() {
    puts("Keep this thing over 50 mph!");
    for (int i = 0; i < 0x3d; i++)
        putchar('=');
    puts("\n");
}
```

### `get_key`

```
00000000000008d7 <get_key>:
 8d7:   55                      push   rbp
 8d8:   48 89 e5                mov    rbp,rsp
 8db:   48 8d 3d fc 01 00 00    lea    rdi,[rip+0x1fc]        # ade <_IO_stdin_used+0x9e>
 8e2:   e8 69 fd ff ff          call   650 <puts@plt>
 8e7:   b8 00 00 00 00          mov    eax,0x0
 8ec:   e8 50 ff ff ff          call   841 <calculate_key>
 8f1:   89 05 65 07 20 00       mov    DWORD PTR [rip+0x200765],eax        # 20105c <key>
 8f7:   48 8d 3d f0 01 00 00    lea    rdi,[rip+0x1f0]        # aee <_IO_stdin_used+0xae>
 8fe:   e8 4d fd ff ff          call   650 <puts@plt>
 903:   90                      nop
 904:   5d                      pop    rbp
 905:   c3                      ret
```

```c
void get_key() {
    puts("Creating key...");
    key = calculate_key();
    puts("Finished");
}
```

### `print_flag`

```
0000000000000906 <print_flag>:
 906:   55                      push   rbp
 907:   48 89 e5                mov    rbp,rsp
 90a:   48 8d 3d e6 01 00 00    lea    rdi,[rip+0x1e6]        # af7 <_IO_stdin_used+0xb7>
 911:   e8 3a fd ff ff          call   650 <puts@plt>
 916:   8b 05 40 07 20 00       mov    eax,DWORD PTR [rip+0x200740]        # 20105c <key>
 91c:   89 c7                   mov    edi,eax
 91e:   e8 97 fe ff ff          call   7ba <decrypt_flag>
 923:   48 8d 3d f6 06 20 00    lea    rdi,[rip+0x2006f6]        # 201020 <flag>
 92a:   e8 21 fd ff ff          call   650 <puts@plt>
 92f:   90                      nop
 930:   5d                      pop    rbp
 931:   c3                      ret
```

```c
void print_flag() {
    puts("Printing flag...");
    decrypt_flag(key);
    puts(flag);
}
```

### `decrypt_flag`

This is the most complicated function, so there are some added annotations:

```
00000000000007ba <decrypt_flag>:
 7ba:   55                      push   rbp
 7bb:   48 89 e5                mov    rbp,rsp
 7be:   89 7d ec                mov    DWORD PTR [rbp-0x14],edi # key
 7c1:   c7 45 fc 00 00 00 00    mov    DWORD PTR [rbp-0x4],0x0  # int i = 0;
 7c8:   eb 6c                   jmp    836 <decrypt_flag+0x7c>
 7ca:   8b 45 fc                mov    eax,DWORD PTR [rbp-0x4]
 7cd:   48 63 d0                movsxd rdx,eax
 7d0:   48 8d 05 49 08 20 00    lea    rax,[rip+0x200849]       # 201020 <flag>
 7d7:   0f b6 0c 02             movzx  ecx,BYTE PTR [rdx+rax*1] # flag[i]
 7db:   8b 45 fc                mov    eax,DWORD PTR [rbp-0x4]
 7de:   99                      cdq                             # Begin i % 2
 7df:   c1 ea 1f                shr    edx,0x1f
 7e2:   01 d0                   add    eax,edx
 7e4:   83 e0 01                and    eax,0x1
 7e7:   29 d0                   sub    eax,edx                  # End i % 2
 7e9:   48 98                   cdqe                            # rax = i % 2
 7eb:   48 8d 55 ec             lea    rdx,[rbp-0x14]
 7ef:   48 01 d0                add    rax,rdx
 7f2:   0f b6 00                movzx  eax,BYTE PTR [rax]       # (i % 2)th byte of key
 7f5:   31 c1                   xor    ecx,eax
 7f7:   8b 45 fc                mov    eax,DWORD PTR [rbp-0x4]
 7fa:   48 63 d0                movsxd rdx,eax
 7fd:   48 8d 05 1c 08 20 00    lea    rax,[rip+0x20081c]       # 201020 <flag>
 804:   88 0c 02                mov    BYTE PTR [rdx+rax*1],cl  # flag[i] ^= (i % 2)th byte of key
 807:   8b 4d fc                mov    ecx,DWORD PTR [rbp-0x4]
 80a:   ba 56 55 55 55          mov    edx,0x55555556           # begin i / 3
 80f:   89 c8                   mov    eax,ecx
 811:   f7 ea                   imul   edx
 813:   89 c8                   mov    eax,ecx
 815:   c1 f8 1f                sar    eax,0x1f
 818:   29 c2                   sub    edx,eax                  # end i / 3
 81a:   89 d0                   mov    eax,edx                  # eax = i / 3
 81c:   01 c0                   add    eax,eax
 81e:   01 d0                   add    eax,edx
 820:   29 c1                   sub    ecx,eax
 822:   89 ca                   mov    edx,ecx                  # edx = i - 3 * (i / 3) = i % 3
 824:   83 fa 02                cmp    edx,0x2
 827:   75 09                   jne    832 <decrypt_flag+0x78>
 829:   8b 45 ec                mov    eax,DWORD PTR [rbp-0x14]
 82c:   83 c0 01                add    eax,0x1
 82f:   89 45 ec                mov    DWORD PTR [rbp-0x14],eax # key++
 832:   83 45 fc 01             add    DWORD PTR [rbp-0x4],0x1  # i++;
 836:   8b 45 fc                mov    eax,DWORD PTR [rbp-0x4]
 839:   83 f8 36                cmp    eax,0x36                 # i <=  36
 83c:   76 8c                   jbe    7ca <decrypt_flag+0x10>
 83e:   90                      nop
 83f:   5d                      pop    rbp
 840:   c3                      ret
```

```c
void decrypt_flag(int key) {
    for (int i = 0; i <= 0x36; i++) {
        if ((i % 2) == 0)
            flag[i] ^= key & 0xff;
        else
            flag[i] ^= (key & 0xff00) >> 0x8;

        if ((i % 3) == 2)
            key++;
    }
}
```

### `main`

```
0000000000000974 <main>:
 974:   55                      push   rbp
 975:   48 89 e5                mov    rbp,rsp
 978:   48 83 ec 10             sub    rsp,0x10
 97c:   89 7d fc                mov    DWORD PTR [rbp-0x4],edi
 97f:   48 89 75 f0             mov    QWORD PTR [rbp-0x10],rsi
 983:   b8 00 00 00 00          mov    eax,0x0
 988:   e8 a5 ff ff ff          call   932 <header>
 98d:   b8 00 00 00 00          mov    eax,0x0
 992:   e8 e8 fe ff ff          call   87f <set_timer>
 997:   b8 00 00 00 00          mov    eax,0x0
 99c:   e8 36 ff ff ff          call   8d7 <get_key>
 9a1:   b8 00 00 00 00          mov    eax,0x0
 9a6:   e8 5b ff ff ff          call   906 <print_flag>
 9ab:   b8 00 00 00 00          mov    eax,0x0
 9b0:   c9                      leave
 9b1:   c3                      ret
 9b2:   66 2e 0f 1f 84 00 00    nop    WORD PTR cs:[rax+rax*1+0x0]
 9b9:   00 00 00
 9bc:   0f 1f 40 00             nop    DWORD PTR [rax+0x0]
```

```c
int main() {
    header();
    set_timer();
    get_key();
    print_flag();
    return 0;
}
```

## Solution 1: Reassemble and Tweak

First let's try running the program as-is:

```
$ ./need-for-speed
Keep this thing over 50 mph!
============================

Creating key...
Not fast enough. BOOM!
```

Glancing at the code, we can see that `set_timer` has set our program
to exit on `SIGALRM` and also set the program to receive `SIGALRM`
after 1 second. The for loop in `get_key` is going to take longer than
one second to run, so it's going to `BOOM!`. The simplest work around
would be to just have `get_key` return the key directly, rather than
looping, then compile the program and run.

## Solution 2: Patching

You can patch a binary file using `vim` and `xxd`. First open the file with
vim, then you can edit the hexdump of the file via `:%!xxd`, the find the
target to patch, in this case the line:

```
00000840: c355 4889 e5c7 45fc 1c07 c2d8 836d fc01  .UH...E......m..
```

Changing the sequence `1c 07 c2 d8` to `8f 03 61 ec` should be all we need.
Make the change, save the file, and read the hexdump back with `%!xxd -revert`
(or just `%!xxd -r`), set the file to `binary` and save with `:set binary | :x`

## Post Script

Piecing everything together, the original program would be something
like:

```c
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <unistd.h>

#define FLAG_LEN 0x37

int key;
// Taken from gdb session
char flag[FLAG_LEN] =  "\xde\x4a\xcd\x4c\xcc\x57\xd6\x78\xd7\x6c\xfe\x67\xb2"
                       "\x69\xfd\x61\xb3\x68\xf1\x66\xe4\x6a\xfb\x64\xb6\x61"
                       "\xe3\x70\xb7\x20\xaa\x30\xae\x60\xfb\x32\xf9\x3a\xba"
                       "\x70\xeb\x66\xf9\x67\xf5\x6d\xfa\x23\xff\x6f\xf1\x6d"
                       "\xf8\x22\xdd";

void decrypt_flag(int key) {
    for (int i = 0; i < FLAG_LEN; i++) {
        if ((i % 2) == 0)
            flag[i] ^= key & 0xff;
        else
            flag[i] ^= (key & 0xff00) >> 0x8;

        if ((i % 3) == 2)
            key++;
    }
}

void alarm_handler(int sig) {
    puts("Not fast enough. BOOM!");
    exit(0);
}

void header() {
    puts("Keep this thing over 50 mph!");
    for (int i = 0; i < 0x3d; i++)
        putchar('=');
    puts("\n");
}

void set_timer() {
    if (signal(SIGALRM, alarm_handler) == SIG_ERR) {
        printf("\n\nSomething bad happened here...\n");
        exit(0);
    }
    alarm(1);
}

int calculate_key()
{
    int x = 0xd8c2071c;
    do {
        x--;
    } while (x != 0xec61038e);
    return x;
}

void get_key()
{
    puts("Creating key...");
    key = calculate_key();
    puts("Finished");
}

void print_flag() {
    puts("Printing flag...");
    decrypt_flag(key);
    puts(flag);
}

int main()
{
    header();
    set_timer();
    get_key();
    print_flag();
    return 0;
}
```
