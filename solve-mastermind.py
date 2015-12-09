#!/usr/bin/env python

# Solve mastermind by reading a (partly finished) game from
# simple text file using Donald Knuth's five-guess algorithm.
# (see: http://www.dcc.fc.up.pt/~sssousa/RM09101.pdf)
#
# License: GPL
# (c) Heiko Noordhof

import sys
import itertools

codelen = 5
colors = frozenset(['w', 'z', 'b', 'r', 'y', 'g'])

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
        elif clr == 'z':
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
        try:
            code, hint = line.split()
        except ValueError:
            raise RuntimeError("invalid line %d" % ln)
        code = parseCode(code.strip(), ln)
        hint = parseHint(hint.strip(), ln)
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

        print "TURN #%d:" % i, turn
        print "REMAINING:", len(remaining_codes)
        for c in remaining_codes:
            print c
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
    max_score = 0
    best_codes = list()
    hints = all_possible_hints()
    for code in untried_codes:
        min_dropped = number_of_possible_codes
        for hint in hints:
            n_dropped = len(get_non_matching_codes(remaining_codes, code, hint))
            if n_dropped < min_dropped:
                min_dropped = n_dropped
        if min_dropped > max_score:
            best_codes = list()
        if min_dropped >= max_score:
            best_codes.append((code, min_dropped))
            max_score = min_dropped

    print "BEST:"
    for best in best_codes:
        print best

if __name__ == "__main__":
    print sys.argv
    print len(sys.argv)
    if len(sys.argv) > 2:
        raise RuntimeError("max 1 argument accepted (for game file)")
    elif len(sys.argv) == 2:
        gamefile = open(sys.argv[1])
    else:
        gamefile = sys.stdin
    main(gamefile)

