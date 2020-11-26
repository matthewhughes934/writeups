# Integer Division

Just some notes about integer division patterns in assembly (at least, in x86).
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
    ; so edx contains the multiple
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
