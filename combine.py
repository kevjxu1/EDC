#!/usr/local/bin/python3
from collections import defaultdict
import sys
from functools import reduce

def editDistance(sA, sB):
    if len(sA) <= len(sB):
        small, big = sA, sB
    else:
        small, big = sB, sA

    opt = [ [ 0 for i in range(len(small) + 1) ] for j in range(2) ]
    for j in range(len(small) + 1):
        opt[0][j] = j

    for i in range(1, len(big) + 1):
        opt[i % 2][0] = i
        for j in range(1, len(small) + 1):
            if small[j - 1] == big[i - 1]:
                opt[i % 2][j] = opt[(i - 1) % 2][j - 1]
            else:
                opt[i % 2][j] = 1 + min(opt[(i - 1) % 2][j], opt[i % 2][j - 1], opt[(i - 1) % 2][j - 1])

    return opt[len(big) % 2][len(small)]

def applyMatchRules(stdList, lis):

    def countNonAlpha(s):
        return reduce(lambda acc, c: acc + (0 if c.isalpha() else 1), s, 0)

    def isTypo(s0, s1):
        return (len(s0) >= 5 and len(s1) >= 5 and
                1 <= editDistance(s0, s1) <= max(countNonAlpha(s0), countNonAlpha(s1)))

    def isEquivalent(s0, s1):
        table = { 'btsm': 'black tiger sex machine' }
        if s0 in table:
            return s1 == table[s0]
        elif s1 in table:
            return s0 == table[s1]
        else:
            return s0 == s1

    def cutPresents(s0, s1):
        i = s0.find(' presents ')
        t0 = s0[: i] if i >= 0 else s0
        j = s1.find(' presents ')
        t1 = s1[: j] if j >= 0 else s1
        return t0 == t1


    new = dict()
    for i in range(len(stdList)):
        for j in range(len(lis)):
            if isTypo(stdList[i], lis[j]) or isEquivalent(stdList[i], lis[j]):
                new[j] = lis[j]

    for j in range(len(lis)):
        if j in new:
            lis[j] = new[j]

    return

def readFile(path):
    with open(path, 'r') as f:
        lines = [ l.rstrip() for l in f.readlines() ]

    lis = []
    name = lines[0].rstrip()
    for l in lines[1 :]:
        if l == '':
            continue
        else:
            lis.append(l)

    return name, lis


def preprocess(lis):
    def cutPresents(s):
        i = s.find(' presents ')
        return s if i < 0 else s[:i]

    def cutParens(s):
        i = s.find('(')
        return s if i < 0 else s[:i]

    res = [ x.lower().replace('&', 'and').rstrip() for x in lis ]
    res = [ cutPresents(s) for s in res ]
    res = [ cutParens(s) for s in res ]
    return res

if __name__ == '__main__':
    first = sys.argv[1]
    firstName, firstList = readFile(first)
    firstList = preprocess(firstList)
    firstList = list(set(firstList))
    m = defaultdict(list)
    for x in firstList:
        m[x].append(firstName)

    for i in range(2, len(sys.argv)):
        name, lis = readFile(sys.argv[i])
        lis = preprocess(lis)
        lis = list(set(lis))
        applyMatchRules(firstList, lis)
        for x in lis:
            m[x].append(name)

    for k in sorted(m.keys()):
        print(k, m[k])
