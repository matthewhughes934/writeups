# Times Up

> Time waits for no one. Can you solve this before time runs out?

## Solution

Running the program:

```
$ ./times-up
Challenge: (((((-1631418784) - (1768505183)) - ((-1647763714) + (-1309653988))) + (((-1715854880) + (574621648)) + ((-2012003930) + (-1947034772)))) + ((((-741163913) + (-1170220973)) + ((-193932616) - (-2019644244))) + (((1569469014) + (1369351594)) + ((-1346291262) + (-460777088)))))
Setting alarm...
Solution? Alarm clock
```

And noting the hint:

> Can you interact with the program using a script?

Let's guess that we need to provide the program with the result of the
arithmetic expression provided before some time limit. That means we will need
to read from the program's stdout and write to its stdin, a normal pipe will
not suffice here since these are unidirectional. However, we should be able to
use a named pipe.

First, let's write a script to handle the computation for us:

```sh
#!/bin/bash

while true
do
    if read line
    then
        if [[ "$line" =~ "Challenge" ]]
        then
            # use `bc` to perform the arithmetic
            cut -d' ' -f 2- <<< "$line" | bc
        else
            # Read back any other line 
            echo "$line" >&2
            if [[ "$line" =~ "Solution?" ]]
            then
                # Last line we're interested in, abort
                break
            fi
        fi
    fi
done
```

The idea is to write the solution of the expression back to the program, but
still be able to read any other line hence using different streams for each
`echo` statement. Next we just create a named pipe and perform the required
redirection:

```
$ mkfifo pipe
$ ./times-up <pipe | ./script.sh 2>&1 >pipe
```
