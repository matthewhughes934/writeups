# `Special`

We're dropped in a shell that's 'special', e.g. it seems to want to capitalise
the first letter and spell correct some things:

``` console
Special$ ls -l
Is al 
sh: 1: Is: not found
Special$ echo
Echo 
sh: 1: Echo: not found
```

We can get around these two limitations by:

  - Having some throw-away data start the comment, e.g. `: echo`
  - Using only commands that are valid English words, e.g. `cat`

Combining those two we can get the flag from:

    : ; cat ./blargh/flag.txt
