mm - MasterMind
===============

Python program for solving the board game of MasterMind™.
It loosely follows Knuth's algorithm [1].

If the program is run without any argument it expects to play
a "live" a game. It will try to guess the secret color code
you keep in mind (or written down). After each guess it expects
hints about the code on its standard input in this way (order
is not significant):

- Enter 'r' (for "red") for each color pin in the correct
  position.

- Enter 'w' (for "white") for each pin the color of which
  appears in the code, but it is not in the correct position.

The program expects a code of 5 pins with a choice of 6 different
colors (one color may appear multiple times in the code). The
colors of the "pins" are represented by these letters:

| Character | Color  |
| :-------: | :---   |
|    `w`    | White  |
|    `k`    | blacK  |
|    `b`    | Blue   |
|    `r`    | Red    |
|    `y`    | Yellow |
|    `g`    | Green  |

When the program is given an argument, it is exepcted to be the
path of a file describing a (partly finished) game. If you want
to cheat in e.g. an online game, use the program this way.

There is an example file called included. See: "mm.txt"

Progress bar:

The program is prepared to use "tqdm" for displaying a progress
bar while thinking, but does not require it. you can install
"tqdm" with:

    pip install tqdm


Todo:
Generating MasterMind puzzles

[1] http://www.dcc.fc.up.pt/~sssousa/RM09101.pdf

