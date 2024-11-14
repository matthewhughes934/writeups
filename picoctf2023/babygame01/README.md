# `babygame01`

Reverse engineering the file (which conveniently still has some symbols,
including function names) using a debugger, it yields something like:

``` c
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
    int has_flag;
};

void init_player(struct player *player) {
    player->row = 4;
    player->column = 4;
    player->has_flag = 0;
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

void print_flag_status(struct player *player) {
  printf("Player has flag: %d\n",(char)(player->has_flag));
  return;
}

void print_map(char *map, struct player *player) {
    clear_screen();
    find_player_pos(map);
    find_end_tile_pos(map);
    print_flag_status(player);

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
    if ((char)player.has_flag != '\0') {
        puts("flage");
        win();
        fflush(stdout);
    }

    return 0;
}
```

So we want to set the `has_flag` field on the `player` struct (specifically, the
first byte in that field) to a non-zero value. There's nowhere in the program
that actually sets this value, however we note the `player` is declared just
above the `map` in `main` so probably there's some buffer underflow we can
abuse. Looking in the main loop, we see we keep moving the player as long as
we're not at the end position, notably there's no bounds checking to ensure
we're before the start of the map, so the following should work:

  - Move player to 0 position
  - Keep moving player left 4 more bytes, to get us on the first byte of
    `player.has_flag`
  - Finish the game

Convenient, we can pass `p` as an input and `move_player` will call
`solve_round` for us to move the player do the end, so we don't have to enter
all those movements to get us to the end.
