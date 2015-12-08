#!/usr/bin/env python

# Solve mastermind by reading a (partly finished) game from
# simple text file using Donald Knuth's five-guess algorithm.
# (see: http://www.dcc.fc.up.pt/~sssousa/RM09101.pdf)
#
# License: GPL
# (c) Heiko Noordhof
#
# See

import sys
import itertools

codelen = 5
colors = frozenset(['w', 'z', 'b', 'r', 'y', 'g'])

possible_codes = list(itertools.product(*[colors for dummy in range(codelen)]))

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
    return (correctColor, correctPosition)

def main():
    ln = 0
    for line in sys.stdin:
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
        print code, hint


if __name__ == "__main__":
    main()
