# `reverse`

We're given an ELF binary:

    $ file ret 
    ./reverse/ret: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=6c43c1779ecbf9a8df208682dd85fdba5bf8110f, for GNU/Linux 3.2.0, not stripped

The flag can be found easily enough by running the program through `strings`,
but let's try and actually solve it, inspecting the `main` function via:

    $ objdump -dM intel ./ret | sed -n '/^[a-f0-9]\+ <main>/,/^$/p'

``` asm
endbr64
push   rbp
mov    rbp,rsp
sub    rsp,0x60
mov    rax,QWORD PTR fs:0x28

mov    QWORD PTR [rbp-0x8],rax
xor    eax,eax
movabs rax,0x7b4654436f636970

movabs rdx,0x337633725f666c33

mov    QWORD PTR [rbp-0x30],rax
mov    QWORD PTR [rbp-0x28],rdx
movabs rax,0x75735f676e693572

movabs rdx,0x6c75663535656363

mov    QWORD PTR [rbp-0x20],rax
mov    QWORD PTR [rbp-0x18],rdx
movabs rax,0x383235386561395f

mov    QWORD PTR [rbp-0x10],rax
lea    rdi,[rip+0xdd7]        # 2008 <_IO_stdin_used+0x8>
mov    eax,0x0
call   10b0 <printf@plt>
lea    rax,[rbp-0x60]
mov    rsi,rax
lea    rdi,[rip+0xde8]        # 2031 <_IO_stdin_used+0x31>
mov    eax,0x0
call   10d0 <__isoc99_scanf@plt>
lea    rax,[rbp-0x60]
mov    rsi,rax
lea    rdi,[rip+0xdd3]        # 2034 <_IO_stdin_used+0x34>
mov    eax,0x0
call   10b0 <printf@plt>
lea    rdx,[rbp-0x30]
lea    rax,[rbp-0x60]
mov    rsi,rdx
mov    rdi,rax
call   10c0 <strcmp@plt>
test   eax,eax
jne    129c <main+0xd3>
lea    rdi,[rip+0xdbf]        # 2048 <_IO_stdin_used+0x48>
call   1090 <puts@plt>
lea    rax,[rbp-0x30]
mov    rdi,rax
call   1090 <puts@plt>
jmp    12a8 <main+0xdf>
lea    rdi,[rip+0xdf3]        # 2096 <_IO_stdin_used+0x96>
call   1090 <puts@plt>
mov    eax,0x0
mov    rcx,QWORD PTR [rbp-0x8]
xor    rcx,QWORD PTR fs:0x28

je     12c1 <main+0xf8>
call   10a0 <__stack_chk_fail@plt>
leave
ret
cs nop WORD PTR [rax+rax*1+0x0]

nop    DWORD PTR [rax]
```

So it looks to build a string starting a `$rbp-0x30` (see the loading happening
near the start of the function), then get the input from the user, then compare
the input with this constructed string (at the `strcmp`) so some ways to solve:

  - Build up the string from the raw bytes in the `movabs` instructions above to
    know the key
  - Run a debugger until just before the `strcmp` value and read off the
    expected value, or
  - Run a debugger until just before the `strcmp` value with any input and
    manually set `eax=0` just before the `test` instruction
