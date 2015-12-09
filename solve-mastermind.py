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
    for i in positions:
        for j in positions:
            if c[i] == code[j]:
                correctColor += 1
                break
    return (correctColor, correctPosition,)

def remove_codes_with_non_matching_hints(codes, code, hint):
    dellist = list()
    for c in codes:
        h = calculate_hint(c, code)
        if h != hint:
            dellist.append(c)
    for d in dellist:
        codes.discard(d)

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
    i = 0
    for turn in game:
        i += 1
        code = turn[0]
        hint = turn[1]
        untried_codes.discard(code)
        remove_codes_with_non_matching_hints(remaining_codes, code, hint)
        print "TURN #%d:" % i, turn
        print "REMAINING:", len(remaining_codes)
        for c in remaining_codes:
            print c
        print

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

