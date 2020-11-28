# Integer Division

Just some notes about integer division patterns in assembly (at least, in x86).

## Example: Division by 3

Here's an example for integer division by `3` using the magic number
`0x55555556`:

```asm
; division.asm
global _start
_start:
    ; 28 / 3
    mov ecx, 0x1c
    ; 0x55555556 = 0x100000000 / 3 + 1
    mov edx, 0x55555556

    mov eax, ecx
    ; imul: edx * eax -> EDX:EAX
    ; so quotient in edx, remainder in eax
    imul edx
    mov eax, ecx

    ; Get sign bit of original number (to handle -ve case)
    sar eax, 0x1f
    sub edx, eax

    ; exit with the resulting value
    mov edi, edx
    xor eax, eax
    add eax, 0x3c
    syscall
```

We can give this a test:

```
nasm -f elf64 -o division.o division.asm
ld -o division division.o
./division
echo $?
```

The assembly above is a common pattern in optimised compiler output. Similar
'magic numbers' exist for other denominators.

## Example: Division by 30

```asm
global _start
_start:
    ; 59 / 30
    mov cl, 0x3b
    ; 0x8888888888888889 = 0x100000000000000000 // 30 + 1
    ; Note 0x8888888888888889 is -ve 64bit int under 2's complement
    mov qword rdx, 0x8888888888888889

    mov eax, ecx
    imul rdx
    ; rdx will be sign extended (padded with 1s)
    ; reverse this
    lea rax, [rdx + rcx]
    ; quotient will be in the 2nd hex digit, so shift off first
    sar rax, 0x4

    mov rdx, rax
    mov rax, rcx

    ; Get sign bit of original number (to handle -ve case)
    sar rax, 0x3f
    sub rdx, rax

    ; exit with the resulting value
    mov rdi, rdx
    xor eax, eax
    add eax, 0x3c
    syscall
```
