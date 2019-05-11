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
                1 <= editDistance(s0, s1) <= max(1, countNonAlpha(s0), countNonAlpha(s1)))

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
                new[j] = stdList[i]

    for j in range(len(lis)):
        if j in new:
            lis[j] = new[j]

    return


def preprocess(s):
    def cutPresents(s):
        i = s.find(' presents ')
        return s if i < 0 else s[:i]

    def cutParens(s):
        i = s.find('(')
        return s if i < 0 else s[:i]

    res = s.lower().replace('&', 'and').rstrip()
    res = cutPresents(res)
    res = cutParens(res)
    return res.rstrip()


def readFile(path):

    with open(path, 'r') as f:
        lines = [ l.rstrip() for l in f.readlines() ]

    fri, sat, sun = [], [], []
    name = lines[0].rstrip()
    dupes = set()
    for l in lines[1 :]:
        e = preprocess(l)
        if e == '' or e in dupes:
            continue
        elif e.startswith('friday'):
            lis = fri
            dupes.clear()
        elif e.startswith('saturday'):
            lis = sat
            dupes.clear()
        elif e.startswith('sunday'):
            lis = sun
            dupes.clear()
        else:
            lis.append(e)
            dupes.add(e)

    return name, fri, sat, sun


if __name__ == '__main__':
    first = sys.argv[1]
    firstName, firstFri, firstSat, firstSun = readFile(first)
    fri, sat, sun = defaultdict(list), defaultdict(list), defaultdict(list)
    for x in firstFri:
        fri[x].append(firstName)
    for x in firstSat:
        sat[x].append(firstName)
    for x in firstSun:
        sun[x].append(firstName)

    for i in range(2, len(sys.argv)):
        name, secFri,secSat, secSun = readFile(sys.argv[i])
        applyMatchRules(firstFri, secFri)
        applyMatchRules(firstSat, secSat)
        applyMatchRules(firstSun, secSun)
        for x in secFri:
            fri[x].append(name)
        for x in secSat:
            sat[x].append(name)
        for x in secSun:
            sun[x].append(name)

    print('Friday')
    for k in sorted(fri.keys()):
        print(k, fri[k])
    print('')
    print('Saturday')
    for k in sorted(sat.keys()):
        print(k, sat[k])
    print('')
    print('Sunday')
    for k in sorted(sun.keys()):
        print(k, sun[k])
