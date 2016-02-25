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
colors = frozenset(['w', 'k', 'b', 'r', 'y', 'g'])
all_codes = itertools.product(*[colors for dummy in range(codelen)])



if __name__ == "__main__":
    counts = dict()
    for code in all_codes:
        cfreq = dict()
        for c in code:
            cfreq[c] = cfreq.get(c, 0) + 1
        freqs = cfreq.values()
        freqs.sort()
        key = tuple(freqs)
        counts[key] = counts.get(key, 0) + 1
    for k,v in counts.iteritems():
        print k,v
