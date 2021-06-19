# Shellcode

## x86 Shellcode for `execve` with `argv`

Consider the example of writing shellcode to cat the contents of some file,
e.g. writing shellcode to invoke `cat myfile`, or in C:

```C
#include <unistd.h>

int main(void)
{
    const char *filename = "/bin/cat";
    char *const argv[] = { "/bin/cat", "myfile", NULL };

    execve(filename, argv, NULL);
    return 0;
}
```

Compiling and testing:

```
$ echo 'some content' > myfile
$ gcc -o cat cat.c
$ ./cat
$ some content
```

To construct the `argv` in assembly we will push some strings onto the stack,
then push the address to those strings also onto the stack:

```asm
global _start
_start:
    ; params into rdi, rsi, rdx
    xor rcx, rcx                    ; store NULL for reuse
    mov rbp, rsp                    ; for easier addressing

    push rcx                        ; '\0', terminator for following string
    mov rax, 0x7461632f6e69622f     ; "/bin/cat"
    push rax                        ; rbp-0x10 = "/bin/cat\0"
    mov rax, 0x000656c6966796d      ; "myfile\x00\x00"
    push rax                        ; rbp-0x18 = "myfile\0\0"
    push rcx                        ; rbp-0x20 = NULL

    lea rax, [rbp-0x18]
    push rax                        ; rbp-0x28 -> "myfile"
    lea rax, [rbp-0x10]
    push rax                        ; rbp-0x30 -> "/bin/cat"

    lea rdi, [rbp-0x10]             ; const char *filename = "/bin/cat"
    lea rsi, [rbp-0x30]             ; char *const argv[] = { "/bin/cat", "myfile", NULL }
    xor rdx, rdx                    ; char *const envp[] = NULL

    xor rax, rax
    mov al, 0x3b                    ; execve syscall
    syscall
```

Testing:

```
$ nasm -f elf64 -o cat64.o cat64.asm
$ ld -o cat64 cat64.o
$ ./cat64
new content
```

Trying out the shellcode:

```
$ objdump -d cat64 | \
    awk -F'\t' '{print $2}' | \
    tr -d '\n' | \
    sed \
        -e 's/[^ ]\{2\}/\\x&/g' \
        -e 's/ \+//g' \
        -e 's/$/\n/'
\x48\x31\xc9\x48\x89\xe5\x51\x48\xb8\x2f\x62\x69\x6e\x2f\x63\x61\x74\x50\x48\xb8\x6d\x79\x66\x69\x6c\x65\x00\x00\x50\x51\x48\x8d\x45\xe8\x50\x48\x8d\x45\xf0\x50\x48\x8d\x7d\xf0\x48\x8d\x75\xd0\x48\x31\xd2\x48\x31\xc0\xb0\x3b\x0f\x05
```

```C
#include <unistd.h>

const char code[] = "\x48\x31\xc9\x48\x89\xe5\x51\x48\xb8\x2f\x62\x69\x6e\x2f\x63"
                    "\x61\x74\x50\x48\xb8\x6d\x79\x66\x69\x6c\x65\x00\x00\x50\x51"
                    "\x48\x8d\x45\xe8\x50\x48\x8d\x45\xf0\x50\x48\x8d\x7d\xf0\x48"
                    "\x8d\x75\xd0\x48\x31\xd2\x48\x31\xc0\xb0\x3b\x0f\x05";


int main(void)
{
    ((void (*)())(code))();
    return 0;
}
```

```
$ gcc -z execstack -o test test.c
$ ./test
new content
```
