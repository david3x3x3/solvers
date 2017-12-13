from copy import deepcopy
from random import *

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
    pos_copy = deepcopy(pos)
    new_pos = deepcopy(pos)
    for k in range(2): #corners and edges
        for j in range(4):
            pos_copy[k][1][turn_table[facenum][k][0][j]] = \
                (pos_copy[k][1][turn_table[facenum][k][0][j]] +
                 turn_table[facenum][k][1][j]) % (3-k)
        for part in range(2): # piece num, orientation
            for j in range(4):
                new_pos[k][part][turn_table[facenum][k][0][(j+1)%4]] = \
                    pos_copy[k][part][turn_table[facenum][k][0][j]]
    return new_pos

def turn(pos,face_times):
    face = face_times[0]
    times = int(face_times[1])
    facenum = "UFRDBL".index(face)
    for i in range(times):
        pos = turn_once(pos, facenum)
    return pos

def int_to_pos(phase, posno):
    parity = 0
    pos = [
        [ [ 0,1,2,3,4,5,6,7 ],
          [ 0,0,0,0,0,0,0,0 ] ],
        [ [ 0,1,2,3,4,5,6,7,8,9,10,11 ],
          [ 0,0,0,0,0,0,0,0,0,0,0,0 ] ]
    ]
    if phase == 0:
        for i in range(10,-1,-1):
            pos[1][1][i] = posno % 2
            parity = (parity + posno % 2) % 2
            posno = posno // 2
        pos[1][1][11] = (2 - parity) % 2
    elif phase == 1:
        for i in range(6,-1,-1):
            pos[0][1][i] = posno % 3
            parity = (parity + (posno % 3)) % 3
            posno = posno // 3
        pos[0][1][7] = (3 - parity) % 3
    return pos

def pos_to_int(phase, pos):
    res = 0
    if phase == 0:
        for i in range(11):
            res = res * 2
            res = res + pos[1][1][i]
    elif phase == 1:
        for i in range(7):
            res = res * 3
            res = res + pos[0][1][i]
    return res
            
def phase_moves(phase):
    moves = []
    for faceno in range(6):
        face = ['U','F','R','D','B','L'][faceno]
        for times in range(1,4):
            if phase > 0 and faceno % 3 == 1 and times % 2 != 0:
                continue
            moves.append(face + str(times))
    return moves

def build_tables():
    global table
    table_sizes = [2**11, 3**7]
    table = [None]*4
    
    pos = [
        [ [ 0,1,2,3,4,5,6,7 ],
          [ 0,0,0,0,0,0,0,0 ] ],
        [ [ 0,1,2,3,4,5,6,7,8,9,10,11 ],
          [ 0,0,0,0,0,0,0,0,0,0,0,0 ] ]
    ]

    # build the tables for each phase
    for phase in range(2):
        print('phase_moves ' + str(phase) + ' = ' + str(phase_moves(phase)))
        depth = 0
        table[phase] = [-1]*table_sizes[phase]
        table[phase][pos_to_int(phase,pos)] = 0
        count = 1
        while count > 0:
            count = 0
            for i in range(table_sizes[phase]):
                if table[phase][i] == depth:
                    pos = int_to_pos(phase, i)
                    for move in phase_moves(phase):
                        pos2 = turn(pos, move)
                        posno2 = pos_to_int(phase, pos2)
                        if table[phase][posno2] == -1:
                            if depth == 0:
                                print(move + ' gives ' + str(pos2))
                            count = count + 1
                            table[phase][posno2] = depth+1
            print('phase ' + str(phase) + ' ' + str(count) + ' positions at distance ' + str(depth+1))
            depth = depth + 1


def main():
    # corner order: URF UFL UBR ULB DFR DLF DRB DBL
    # edge order: UF UL UB UR FL BL BR FR DF DL DB DR
    pos = [
        [ [ 0,1,2,3,4,5,6,7 ],
          [ 0,0,0,0,0,0,0,0 ] ],
        [ [ 0,1,2,3,4,5,6,7,8,9,10,11 ],
          [ 0,0,0,0,0,0,0,0,0,0,0,0 ] ]
    ]
    print("pos = " + str(pos))
    print('turning U1')
    pos = turn(pos, 'U1')
    print(str(pos))
    print('turning R1')
    pos = turn(pos, 'R1')
    print(str(pos))
    posno = pos_to_int(1, pos)
    print('posno 1 = ' + str(posno))
    print('calling int_to_pos 1')
    pos = int_to_pos(1, posno)
    print("pos = " + str(pos))

    build_tables()

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
        pos = turn(pos, move)
        print(move + ': ' + str(pos))

    # solve
    for phase in range(2):
        print('solving phase ' + str(phase))
        dist = table[phase][pos_to_int(phase, pos)]
        while dist > 0:
            for move in phase_moves(phase):
                pos2 = turn(pos, move)
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
