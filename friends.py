#!/usr/local/bin/python3
from collections import defaultdict
import sys
from functools import reduce

def formatTime(time):
    """@param time - like '10:46 PM - 11:59 PM'
       @return start, end - where each is 24HR time"""

    def to24Time(t):
        hh, mm = t[: len(t) - 3].split(':')
        if t.endswith('PM'):
            hh = (int(hh) + 12) % 24

        return str(hh) + ':' + str(mm)

    pair = time.split(' - ')
    return to24Time(pair[0]), to24Time(pair[1])

def findFirstGte(lis, hour):
    """@param lis - list sorted in ascending order
       @return position of first element that is >= target"""
    i = 0
    for i, x in enumerate(lis):
        if x >= hour:
            return i

    return len(lis)

def getSchedule(dayFile):
    """@return times, stages - each is a map with artist name as key. times maps
               to time range and stages maps to stage
    """

    schedule = []  # each element is (time, artist, stage)
    with open(dayFile, 'r') as f:
        lines = [ l.rstrip() for l in f.readlines() ]

    stage = None
    for line in lines:
        if line == '':
            continue
        elif ',' in line:
            # artist,time where each time is like '10:46 PM - 11:59 PM'
            artist, time = line.split(',')
            artist = preprocess(artist)
            time = formatTime(time)
            schedule.append((time, artist, stage))
        else:
            stage = line

    schedule.sort()

    # assume festival does not start before 16:00, and rotate schedule accordingly
    i = findFirstGte([int(x[0][0].split(':')[0]) for x in schedule], 16)
    schedule = schedule[i :] + schedule[: i]
    return schedule


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
    """Replaces each in lis to the corresponding element in stdList if they 'match'"""

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
    """@param s - string
       @return - preprocessed string"""
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
    firstName, mainFri, mainSat, mainSun = readFile(first)
    friFriends, satFriends, sunFriends = defaultdict(list), defaultdict(list), defaultdict(list)
    for x in mainFri:
        friFriends[x].append(firstName)
    for x in mainSat:
        satFriends[x].append(firstName)
    for x in mainSun:
        sunFriends[x].append(firstName)

    friSchedule = getSchedule('friday.txt')
    satSchedule = getSchedule('saturday.txt')
    sunSchedule = getSchedule('sunday.txt')
    for i in range(2, len(sys.argv)):
        name, secFri,secSat, secSun = readFile(sys.argv[i])
        applyMatchRules([ x[1] for x in friSchedule ], secFri)
        applyMatchRules([ x[1] for x in satSchedule ], secSat)
        applyMatchRules([ x[1] for x in sunSchedule ], secSun)
        for x in secFri:
            friFriends[x].append(name)
        for x in secSat:
            satFriends[x].append(name)
        for x in secSun:
            sunFriends[x].append(name)

        mainFri = list(friFriends.keys())
        mainSat = list(satFriends.keys())
        mainSun = list(sunFriends.keys())

    print('Friday')
    for time, artist, stage in friSchedule:
        if artist in friFriends:
            csv = '%s,%s,%s,%s' % ( str(time), artist, stage, str(friFriends[artist]) )
            print(csv)
    print('')
    print('Saturday')
    for time, artist, stage in satSchedule:
        if artist in satFriends:
            csv = '%s,%s,%s,%s' % ( str(time), artist, stage, str(satFriends[artist]) )
            print(csv)
    print('')
    print('Sunday')
    for time, artist, stage in sunSchedule:
        if artist in sunFriends:
            csv = '%s,%s,%s,%s' % ( str(time), artist, stage, str(sunFriends[artist]) )
            print(csv)
