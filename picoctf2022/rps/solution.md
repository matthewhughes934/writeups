# RPS

Noting the hint:

> How does the program check if you won?

An naively glancing at the check in `play`:

``` c
  if (strstr(player_turn, loses[computer_turn])) {
    puts("You win! Play again?");
    return true;
  } else {
    puts("Seems like you didn't win this time. Play again?");
    return false;
  }
```

`strstr` will just check if `loses[computer_turn]` appears as a substring
anywhere in `player_turn`. Given there's no validation on the player's input
(i.e. that it's one of "rock", "paper", or "scissors") then if we submit e.g.
"rockpaperscissors" then any computer turn will be a substring of this, hence
when can easily win 5 turns then quit:

``` console
$ perl -e 'print("1\nrockpaperscissors\n" x 5 . "2\n")' | nc saturn.picoctf.net 56981
```
