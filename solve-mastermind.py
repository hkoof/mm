#!/usr/bin/env python

# Solve mastermind by reading a (partly finished) game from
# simple text file using Donald Knuth's five-guess algorithm.
# (see: http://www.dcc.fc.up.pt/~sssousa/RM09101.pdf)
#
# License: GPL
# (c) Heiko Noordhof

import sys
import itertools

progress_bar = True
try:
    from tqdm import tqdm
except ImportError:
    progress_bar = False

codelen = 5
colors = frozenset(['w', 'k', 'b', 'r', 'y', 'g'])

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
        elif clr == 'b':
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

def main(gamefile):
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

    untried_codes = set(all_possible_codes())
    remaining_codes = set(all_possible_codes())
    number_of_possible_codes = len(untried_codes)
    i = 0
    for turn in game:
        i += 1
        code = turn[0]
        hint = turn[1]
        untried_codes.discard(code)
        remaining_codes.discard(code)
        for d in get_non_matching_codes(remaining_codes, code, hint):
            remaining_codes.discard(d)
        print "Turn #%d:" % i, turn
        print "Remaining matching codes:", len(remaining_codes)
        print

    # Now find best  next move.
    # This is most often a code from remaining_codes, but not always.
    #
    n = len(remaining_codes)
    if n == 0:
        raise RuntimeError("No possible code left. Wrong hint somewhere!")
    if n == 1:
        print remaining_codes
        print "Done!"
        sys.exit(0)

    # For each code not played yet, calculate a score by trying how many
    # codes would be dropped from remaining_codes for each possible hint.
    # The codes that would drop the most for sure (at least, minimally)
    # score higher. Of the highest scoring codes, it is best to pick one
    # that is also in remaining_codes, because only then it could
    # accidentally be The One Code we're looking for.
    #
    n = len(remaining_codes)
    max_score = 0
    max_total_dropped = 0
    best_codes = list()
    hints = all_possible_hints()
    if progress_bar and n >= 60:
        loop_iterator = tqdm(remaining_codes, "thinking...", n)
    else:
        loop_iterator = remaining_codes
    for code in loop_iterator:
        total_dropped = 0
        min_dropped = number_of_remaining_codes
        for hint in hints:
            n_dropped = len(get_non_matching_codes(remaining_codes, code, hint))
            total_dropped += n_dropped
            if n_dropped < min_dropped:
                min_dropped = n_dropped
        if total_dropped > max_total_dropped:
            max_total_dropped = total_dropped
        if min_dropped > max_score:
            best_codes = list()
            max_score = min_dropped
        if min_dropped == max_score and total_dropped > max_total_dropped:
            best_codes = list()
        if min_dropped >= max_score:
            best_codes.append((code, min_dropped, total_dropped))

    print "Best next moves: (%d)" % len(best_codes)
    print "---------------------------------------------------"
    for best in best_codes:
        print best

if __name__ == "__main__":
    if len(sys.argv) > 2:
        raise RuntimeError("max 1 argument accepted (for game file)")
    elif len(sys.argv) == 2:
        gamefile = open(sys.argv[1])
    else:
        gamefile = sys.stdin
    main(gamefile)

