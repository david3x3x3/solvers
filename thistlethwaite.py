from copy import deepcopy
from random import *

import bisect

def cmp(a,b):
    return (a > b) - (a < b)
    
# next_permutation copied from here:
# http://blog.bjrn.se/2008/04/lexicographic-permutations-using.html

def next_permutation(seq, pred=cmp):
    """Like C++ std::next_permutation() but implemented as
    generator. Yields copies of seq."""

    def reverse(seq, start, end):
        # seq = seq[:start] + reversed(seq[start:end]) + \
        #       seq[end:]
        end -= 1
        if end <= start:
            return
        while True:
            seq[start], seq[end] = seq[end], seq[start]
            if start == end or start+1 == end:
                return
            start += 1
            end -= 1
    
    if not seq:
        raise StopIteration

    try:
        seq[0]
    except TypeError:
        raise TypeError("seq must allow random access.")

    first = 0
    last = len(seq)
    seq = seq[:]

    # Yield input sequence as the STL version is often
    # used inside do {} while.
    yield seq
    
    if last == 1:
        raise StopIteration

    while True:
        next = last - 1

        while True:
            # Step 1.
            next1 = next
            next -= 1
            
            if pred(seq[next], seq[next1]) < 0:
                # Step 2.
                mid = last - 1
                while not (pred(seq[next], seq[mid]) < 0):
                    mid -= 1
                seq[next], seq[mid] = seq[mid], seq[next]
                
                # Step 3.
                reverse(seq, next1, last)

                # Change to yield references to get rid of
                # (at worst) |seq|! copy operations.
                yield seq[:]
                break
            if next == first:
                raise StopIteration
    raise StopIteration

def turn_once(pos,facenum):
    turn_table = [
        #           corner pos,      corner orient,
        #             edge pos,        edge orient
        [ [ [  0,  1,  3,  2 ], [  0,  0,  0,  0 ] ],
          [ [  0,  1,  2,  3 ], [  0,  0,  0,  0 ] ] ], #U
        [ [ [  0,  4,  5,  1 ], [  2,  1,  2,  1 ] ],
          [ [  0,  7,  8,  4 ], [  1,  1,  1,  1 ] ] ], #F
        [ [ [  0,  2,  6,  4 ], [  1,  2,  1,  2 ] ],
          [ [  3,  6, 11,  7 ], [  0,  0,  0,  0 ] ] ], #R
        [ [ [  4,  6,  7,  5 ], [  0,  0,  0,  0 ] ],
          [ [  8, 11, 10,  9 ], [  0,  0,  0,  0 ] ] ], #D
        [ [ [  2,  3,  7,  6 ], [  1,  2,  1,  2 ] ],
          [ [  2,  5, 10,  6 ], [  1,  1,  1,  1 ] ] ], #B
        [ [ [  1,  5,  7,  3 ], [  2,  1,  2,  1 ] ],
          [ [  1,  4,  9,  5 ], [  0,  0,  0,  0 ] ] ], #L
    ]
    #print('facenum = ' + str(facenum))
    #pos_copy = deepcopy(pos)
    #new_pos = deepcopy(pos)
    for k in range(2): #corners and edges
        for j in range(4):
            pos[k][1][turn_table[facenum][k][0][j]] = \
                (pos[k][1][turn_table[facenum][k][0][j]] + 
                 turn_table[facenum][k][1][j]) % (3-k)
        for part in range(2): # piece num, orientation
            m = pos[k][part][turn_table[facenum][k][0][3]]
            for j in range(3,0,-1):
                pos[k][part][turn_table[facenum][k][0][j]] = \
                    pos[k][part][turn_table[facenum][k][0][j-1]]
            pos[k][part][turn_table[facenum][k][0][0]] = m
    return

def turn(pos,face_times):
    face = face_times[0]
    times = int(face_times[1])
    facenum = "UFRDBL".index(face)
    for i in range(times):
        turn_once(pos, facenum)
    return

def int_to_pos(phase, posno):
    parity = 0
    pos = [
        [ [ 0,1,2,3,4,5,6,7 ],
          [ 0,0,0,0,0,0,0,0 ] ],
        [ [ 0,1,2,3,4,5,6,7,8,9,10,11 ],
          [ 0,0,0,0,0,0,0,0,0,0,0,0 ] ]
    ]
    if phase == 0:
        # decode edge orientation
        for i in range(10,-1,-1):
            pos[1][1][i] = posno % 2
            parity = (parity + posno % 2) % 2
            posno = posno // 2
        pos[1][1][11] = (2 - parity) % 2
    elif phase == 1:
        # decode edge position
        permno = posno % 495
        perm = int_to_perm1[permno]
        for i in range(12):
            pos[1][0][i] = perm[i]*4
        posno = posno // 495
        # decode corner orientation
        for i in range(6,-1,-1):
            pos[0][1][i] = posno % 3
            parity = (parity + (posno % 3)) % 3
            posno = posno // 3
        pos[0][1][7] = (3 - parity) % 3
    elif phase == 2:
        # edge orbits
        permno = posno % 70
        perm = int_to_perm2[permno]
        edges = [0,1,2,3,8,9,10,11]
        for i in range(8):
            j = edges[i]
            pos[1][0][j] = perm[i]
        # corner orbits
        permno = permno // 70
        perm = int_to_perm2[permno]
        for i in range(8):
            pos[0][0][i] = perm[i]
    return pos

def pos_to_int(phase, pos):
    res = 0
    if phase == 0:
        for i in range(11):
            res = res * 2 + pos[1][1][i]
    elif phase == 1:
        # count the corner twists
        for i in range(7):
            res = res * 3 + pos[0][1][i]
        # find the permutation of the middle edges
        res = res * 495
        perm = 0
        for i in range(12):
            p = pos[1][0][i]
            perm = perm * 2
            if p >= 4 and p <= 7:
                perm = perm + 1
        res = res + perm_to_int1[perm]
    elif phase == 2:
        # corners 0,3,5,6 and 1,2,4,7 are in different orbits
        perm = 0
        for i in range(7):
            perm = perm * 2
            if pos[0][0][i] in [1,2,4,7]:
                perm = perm + 1
        res = res + perm_to_int2[perm]
        perm = [0]*8
        # U and D edges in different orbits
        edges = [0,1,2,3,8,9,10,11]
        for i in range(8):
            j = edges[i]
            if pos[1][0][j] in [1,3,9,11]:
                perm[i]=1
        res = res*70 + (bisect.bisect(int_to_perm2, perm)-1)
        
    return res
            
def phase_moves(phase):
    moves = []
    for faceno in range(6):
        face = ['U','F','R','D','B','L'][faceno]
        for times in range(1,4):
            if (phase > 0 and faceno % 3 == 1 or
                phase > 1 and faceno % 3 == 2 or
                phase > 2) and times % 2 != 0:
                continue
            moves.append(face + str(times))
    return moves

def build_tables():
    global table
    global int_to_perm1
    global int_to_perm2
    global perm_to_int1
    global perm_to_int2
    table_sizes = [2**11, 3**7 * 495, 70 * 495]
    table = [None]*4
    
    z = [0]*8+[1]*4
    int_to_perm1 = list(next_permutation(z))
    int_to_perm1[0] = z # I don't know why next_permutation reverses the first item
    print('int_to_perm1 size = ' + str(len(int_to_perm1)))
    perm_to_int1 = [-1]*(2**12)
    for i in range(len(int_to_perm1)):
        p = int_to_perm1[i]
        j = 0
        for k in p:
            j = j * 2 + k
        perm_to_int1[j] = i
    
    z = [0]*4+[1]*4
    int_to_perm2 = list(next_permutation(z))
    int_to_perm2[0] = z
    print('int_to_perm2 size = ' + str(len(int_to_perm2)))
    perm_to_int2 = [-1]*(2**8)
    for i in range(len(int_to_perm)):
        p = int_to_perm2[i]
        j = 0
        for k in p:
            j = j * 2 + k
        perm_to_int2[j] = i

    pos = [
        [ [ 0,1,2,3,4,5,6,7 ],
          [ 0,0,0,0,0,0,0,0 ] ],
        [ [ 0,1,2,3,4,5,6,7,8,9,10,11 ],
          [ 0,0,0,0,0,0,0,0,0,0,0,0 ] ]
    ]

    # build the tables for each phase
    for phase in range(3):
        p_m = phase_moves(phase)
        print('phase_moves ' + str(phase) + ' = ' + str(p_m))
        depth = 0
        table[phase] = [-1]*table_sizes[phase]
        table[phase][pos_to_int(phase,pos)] = 0
        count = 1
        while count > 0:
            count = 0
            for i in range(table_sizes[phase]):
                if table[phase][i] == depth:
                    pos = int_to_pos(phase, i)
                    for faceno in range(6):
                        face = ['U','F','R','D','B','L'][faceno]
                        times = 0
                        for times in range(4):
                            turn_once(pos, faceno)
                            times = times + 1
                            move = face + str(times)
                            if move in p_m:
                                posno = pos_to_int(phase, pos)
                                if table[phase][posno] == -1:
                                    # if depth == 0:
                                    #     print(move + ' gives ' + str(pos))
                                    count = count + 1
                                    table[phase][posno] = depth+1
            print('phase ' + str(phase) + ' ' + str(count) + ' positions at distance ' + str(depth+1))
            # if phase == 1 and depth == 6:
            #     exit(0)
            depth = depth + 1


def main():
    # corner order: URF UFL UBR ULB DFR DLF DRB DBL
    # edge order: UF UL UB UR FL BL BR FR DF DL DB DR

    build_tables()

    pos = [
        [ [ 0,1,2,3,4,5,6,7 ],
          [ 0,0,0,0,0,0,0,0 ] ],
        [ [ 0,1,2,3,4,5,6,7,8,9,10,11 ],
          [ 0,0,0,0,0,0,0,0,0,0,0,0 ] ]
    ]
    print("pos = " + str(pos))
    print('turning U1')
    turn(pos, 'U1')
    print(str(pos))
    print('turning R1')
    turn(pos, 'R1')
    print(str(pos))
    posno = pos_to_int(1, pos)
    print('posno 1 = ' + str(posno))
    print('calling int_to_pos 1')
    pos = int_to_pos(1, posno)
    print("pos = " + str(pos))

    # random scramble
    pos = [
        [ [ 0,1,2,3,4,5,6,7 ],
          [ 0,0,0,0,0,0,0,0 ] ],
        [ [ 0,1,2,3,4,5,6,7,8,9,10,11 ],
          [ 0,0,0,0,0,0,0,0,0,0,0,0 ] ]
    ]
    prev1 = ''
    prev2 = ''
    count = 0
    seq = []
    while count < 25:
        face = sample(['U','F','R','D','B','L'], 1)[0]
        if face == prev1:
            continue
        times = randint(2, 3)
        seq.append(face + str(times))
        prev2 = prev1
        prev1 = face
        count = count + 1
    print('scramble = ' + str(seq))
    for move in seq:
        turn(pos, move)
        print(move + ': ' + str(pos))

    # solve
    for phase in range(2):
        print('solving phase ' + str(phase))
        dist = table[phase][pos_to_int(phase, pos)]
        while dist > 0:
            for move in phase_moves(phase):
                pos2 = deepcopy(pos)
                turn(pos2, move)
                posno2 = pos_to_int(phase, pos2)
                nextdist = table[phase][posno2]
                if nextdist < dist:
                    #print('dist = ' + str(dist) + ', next dist = ' + str(nextdist))
                    nextmove = move
                    nextpos = pos2
            print('move = ' + nextmove)
            dist = dist - 1
            pos = nextpos
            #print(pos)
    
main()
