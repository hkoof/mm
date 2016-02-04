#!/usr/bin/env python

# Solve mastermind by reading a (partly finished) game from
# simple text file using Donald Knuth's five-guess algorithm.
# (see: http://www.dcc.fc.up.pt/~sssousa/RM09101.pdf)
#
# License: GPL
# (c) Heiko Noordhof

import sys
import random
import itertools

# just importing "readline" makes input() and raw_input()
# behave more user friendly.
import readline

progress_bar = True
try:
    from tqdm import tqdm
except ImportError:
    progress_bar = False

# Limit on set of codes to consifer for a move.
# Prevents unneeded thinking times for early moves.
#
max_code_set = 300

codelen = 5
colors = frozenset(['w', 'k', 'b', 'r', 'y', 'g'])

number_of_possible_codes = None

def format_code(move):
    return "".join(move)

def format_turn(turn):
    code = turn[0]
    hint = turn[1]
    return "%s %s%s" % (format_code(code), "w" * hint[0], "r" * hint[1])

def read_hint_input():
    hint = None
    while hint is None:
        string = raw_input("Hint: ")
        try:
            hint = parseHint(string, 0)
        except RuntimeError, message:
            print message
            hint = None
        print
    return hint

def all_possible_hints():
    hints = list()
    for white in range(codelen + 1):
        for black in range(codelen - white + 1):
            if white == 1 and black == (codelen - 1):
                continue  # Exception: this hint cannot happen.
            hints.append((white, black,))
    return hints

def all_possible_codes():
    return itertools.product(*[colors for dummy in range(codelen)])

def parseCode(string, lineNumber):
    if len(string) != codelen:
        raise RuntimeError("invalid code in line %d" % lineNumber)
    for clr in string:
        if clr not in colors:
            raise RuntimeError("invalid color '%s' in line %d" % (clr, lineNumber))
    return tuple(string)

def parseHint(string, lineNumber):
    if len(string) > codelen: 
        raise RuntimeError("invalid hint in line %d" % lineNumber)
    correctColor = 0
    correctPosition = 0
    for clr in string:
        if clr == 'w':
            correctColor += 1
        elif clr == 'r':
            correctPosition += 1
        else:
            raise RuntimeError("invalid hint color '%s' in line %d" % (clr, lineNumber))
    if correctColor + correctPosition > codelen:
        raise RuntimeError("invalid hint length in line %d" % lineNumber)
    return (correctColor, correctPosition,)

def calculate_hint(c, code):
    correctColor = 0
    correctPosition = 0
    positions = range(codelen)
    for i in range(codelen):
        if c[i] == code[i]:
            correctPosition += 1
            positions.remove(i)
    codecopy = list(code)
    for i in positions:
        for j in positions:
            if c[i] == codecopy[j]:
                correctColor += 1
                codecopy[j] = None # prevent counting this one again
                break
    return (correctColor, correctPosition,)

def get_non_matching_codes(codes, code, hint):
    # Return a list of codes that do not result in <hint> when
    # checked against <code>.
    dontmatch = list()
    for c in codes:
        h = calculate_hint(c, code)
        if h != hint:
            dontmatch.append(c)
    return dontmatch

def load_game(gamefile):
    ln = 0
    game = list()
    for line in gamefile:
        ln += 1
        line = line.strip()
        if not line:
            continue
        turn = line.split()
        if len(turn) == 1:
           turn.append("")
        elif len(turn) > 2:
            raise RuntimeError("invalid line %d" % ln)
        code = parseCode(turn[0].strip(), ln)
        hint = parseHint(turn[1].strip(), ln)
        game.append((code, hint,))
    return game

def process_move(code, hint, untried_codes, remaining_codes):
    untried_codes.discard(code)
    if hint == (0, 5,):   # Found the code!   *\o/*
        remaining_codes.clear()
        remaining_codes.add(code)
        return
    remaining_codes.discard(code)
    for d in get_non_matching_codes(remaining_codes, code, hint):
        remaining_codes.discard(d)

def run_game(game, untried_codes, remaining_codes):
    i = 0
    for turn in game:
        i += 1
        code = turn[0]
        hint = turn[1]
        print "Possible codes left: %d" % len(remaining_codes)
        print "Turn #%d:" % i
        print format_turn(turn)
        print
        process_move(code, hint, untried_codes, remaining_codes)

def calculate_best_move(remaining_codes):
    n = len(remaining_codes)
    if n == number_of_possible_codes:
        # First move, don't care too much. Not just any code tho,
        # so do calculate, but from a random sample of all possible codes.
        n = 100
        code_set = random.sample(remaining_codes, n)
    elif n > max_code_set:
        n = max_code_set
        code_set = random.sample(remaining_codes, max_code_set)
    else:
        code_set = remaining_codes
    if n == 0:
        raise RuntimeError("No possible code left. Wrong hint somewhere!")
    if n == 1:
        return remaining_codes.pop()
    #
    # For each code not played yet, calculate a score by trying how many
    # codes would be dropped from the code_set for each possible hint.
    #
    max_score = 0
    max_total_dropped = 0
    best_codes = list()
    hints = all_possible_hints()
    if progress_bar and n >= 60:
        loop_iterator = tqdm(code_set, total=n, ncols=70)
    else:
        loop_iterator = code_set
    for code in loop_iterator:
        total_dropped = 0
        min_dropped = number_of_possible_codes
        for hint in hints:
            n_dropped = len(get_non_matching_codes(code_set, code, hint))
            total_dropped += n_dropped
            if n_dropped < min_dropped:
                min_dropped = n_dropped
        if total_dropped > max_total_dropped:
            max_total_dropped = total_dropped
        if min_dropped > max_score:
            #best_codes = list()
            max_score = min_dropped
        if min_dropped == max_score and total_dropped > max_total_dropped:
            #best_codes = list()
            pass
        if min_dropped >= max_score:
            best_codes.append((code, min_dropped, total_dropped))
    print "------------ All possible codes ---------"
    for c in remaining_codes:
        print c
    print "-----------------------------------------"
    best_codes.sort(key=lambda t: t[1:])
    for c in best_codes:
        print c
    print "-----------------------------------------"
    print "Best codes to choose from:", len(best_codes)
    return random.choice(best_codes)[0]

def main(gamefile):
    global number_of_possible_codes

    untried_codes = set(all_possible_codes())
    remaining_codes = set(all_possible_codes())
    number_of_possible_codes = len(untried_codes)

    if gamefile is not None:
        game = load_game(gamefile)
        run_game(game, untried_codes, remaining_codes)
        move = calculate_best_move(remaining_codes)
        if len(remaining_codes) == 0:
            print "Code found:", format_code(move)
        else:
            print "Possible codes left: %d" % len(remaining_codes)
            print "Best move:", format_code(move)
        sys.exit()

    # Interactive game
    #
    game = list()
    while True:
        print "Possible codes left: %d" % len(remaining_codes)
        move = calculate_best_move(remaining_codes)
        print "Move:", format_code(move)
        hint = read_hint_input()
        process_move(move, hint, untried_codes, remaining_codes)
        if len(remaining_codes) == 1:
            print "Code found:", format_code(remaining_codes.pop())
            sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        raise RuntimeError("max 1 argument accepted (for game file)")
    elif len(sys.argv) == 2:
        gamefile = open(sys.argv[1])
    else:
        gamefile = None
    main(gamefile)

