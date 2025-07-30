import numpy as np
FILE_A_MASK = np.uint64(0xfefefefefefefefe)
FILE_H_MASK = np.uint64(0x7f7f7f7f7f7f7f7f)
FILE_AB_MASK = np.uint64(0xfcfcfcfcfcfcfcfc)
FILE_GH_MASK = np.uint64(0x3f3f3f3f3f3f3f3f)

def generate_moves(state):
    all_moves = []
    all_moves += generate_pawn_moves(state)
    all_moves += generate_rook_moves(state, 'white')
    all_moves += generate_bishop_moves(state, 'white')
#add other piece moves
    return all_moves


def generate_pawn_moves(state, color):
    moves = []

    empty_squares = ~state.all_occ # invert occupied squares

    if color == 'white':
        pawns = state.bitboards['white_pawns']
        one_step = shift_north(pawns) & empty_squares  
        for to_square in bit_indices(one_step):
            from_square = to_square - 8
            moves.append((from_square, to_square))

        #  Double move (if both squares are empty)
        rank2_mask = np.uint64(0x000000000000FF00)
        pawns_on_rank2 = pawns & rank2_mask
        one_step_rank2 = shift_north(pawns_on_rank2) & empty_squares
        two_step = shift_north(one_step_rank2) & empty_squares
        for to_square in bit_indices(two_step):
            from_square = to_square - 16
            moves.append((from_square, to_square))

        # Diagonal captures, only where there's an enemy piece
        northeast_attacks = shift_northeast(pawns) & state.black_occ
        northwest_attacks = shift_northwest(pawns) & state.black_occ
        for to_square in bit_indices(northeast_attacks):
            from_square = to_square - 9
            moves.append((from_square, to_square))
        for to_square in bit_indices(northwest_attacks):
            from_square = to_square - 7
            moves.append((from_square, to_square))     



    elif color == 'black':
            pawns = state.bitboards['black_pawns']
            one_step = shift_south(pawns) & empty_squares  
            for to_square in bit_indices(one_step):
                from_square = to_square + 8
                moves.append((from_square, to_square))

            #  Double move from rank 7 (if both squares are empty)
            rank7_mask = np.uint64(0x00FF000000000000)
            pawns_on_rank7 = pawns & rank7_mask
            one_step_rank7 = shift_south(pawns_on_rank7) & empty_squares
            two_step = shift_south(one_step_rank7) & empty_squares
            for to_square in bit_indices(two_step):
                from_square = to_square + 16
                moves.append((from_square, to_square))

            # Diagonal captures, only where there's an enemy piece
            southeast_attacks = shift_southeast(pawns) & state.white_occ
            southwest_attacks = shift_southwest(pawns) & state.white_occ
            for to_square in bit_indices(southeast_attacks):
                from_square = to_square + 9
                moves.append((from_square, to_square))
            for to_square in bit_indices(southwest_attacks):
                from_square = to_square + 7
                moves.append((from_square, to_square)) 

    return moves

def generate_rook_moves(state, color):
    moves = []
    rook_bb = state.bitboards[f'{color}_rook']
    enemy_color = 'white' if color == 'black' else 'black'
    enemy_bb = (
        state.bitboards[f'{enemy_color}_pawns'] |
        state.bitboards[f'{enemy_color}_rook'] |
        state.bitboards[f'{enemy_color}_bishop'] |
        state.bitboards[f'{enemy_color}_knight'] |
        state.bitboards[f'{enemy_color}_queen'] |
        state.bitboards[f'{enemy_color}_king']
    )
    all_occ = state.all_occ

    for square in bit_indices(rook_bb):
        #Directions N,S,E,W
        for delta in [+8, -8, +1, - 1]:
            current = square
            while True:
                next_square = current + delta

                #edge checks
                if next_square < 0 or next_square > 63:
                    break
                if (delta == +1 and current % 8 == 7): break
                if (delta == -1 and current % 8 == 0): break

                mask = np.uint64(1) << next_square

                if all_occ & mask:
                    if enemy_bb & mask:
                        moves.append((square, next_square)) #capture
                    break
                else:
                    moves.append((square, next_square))
                    current = next_square
    return moves

def generate_bishop_moves(state, color):
    moves = []
    bishop_bb = state.bitboards[f'{color}_bishop']
    enemy_color = 'white' if color == 'black' else 'black'
    enemy_bb = (
        state.bitboards[f'{enemy_color}_pawns'] |
        state.bitboards[f'{enemy_color}_rook'] |
        state.bitboards[f'{enemy_color}_bishop'] |
        state.bitboards[f'{enemy_color}_knight'] |
        state.bitboards[f'{enemy_color}_queen'] |
        state.bitboards[f'{enemy_color}_king']
    )
    all_occ = state.all_occ

    for square in bit_indices(bishop_bb):
            #diagonals
            for delta in [+9, -7, -9, +7]:
                current = square
                while True:
                    next_square = current + delta

                    #edge
                    if next_square < 0 or next_square > 63:
                        break
                    if (delta == +1 and current % 8 == 7): break
                    if (delta == +1 and current % 8 == 0): break

                    mask = np.uint64(1) << next_square

                    if all_occ & mask:
                        if enemy_bb & mask:
                            moves.append((square, next_square))
                        break
                    else:
                        moves.append((square, next_square))
                        current = next_square
    return moves


def generate_queen_moves(state, color):
    moves = []
    queen_bb = state.bitboards[f'{color}_queen']
    enemy_color = 'white' if color == 'black' else 'black'
    enemy_bb = (
        state.bitboards[f'{enemy_color}_pawns'] |
        state.bitboards[f'{enemy_color}_rook'] |
        state.bitboards[f'{enemy_color}_bishop'] |
        state.bitboards[f'{enemy_color}_knight'] |
        state.bitboards[f'{enemy_color}_queen'] |
        state.bitboards[f'{enemy_color}_king']
    )
    all_occ = state.all_occ
    for square in bit_indices(queen_bb):
            #Directions N,S,E,W, diagonals 
            for delta in [+8, -8, +1, - 1, +9, -7, -9, +7]:
                current = square
                while True:
                    next_square = current + delta

                    #edge checks
                    if next_square < 0 or next_square > 63:
                        break
                    if (delta == +1 and current % 8 == 7): break
                    if (delta == -1 and current % 8 == 0): break

                    mask = np.uint64(1) << next_square

                    if all_occ & mask:
                        if enemy_bb & mask:
                            moves.append((square, next_square)) #capture
                        break
                    else:
                        moves.append((square, next_square))
                        current = next_square
    return moves
    
def generate_king_moves(state, color):
    moves = []
    if color == 'white':
        king_bb = state.bitboards['white_king']
        friends_occ = state.white_occ
        enemy_occ = state.black_occ
    else:
        king_bb = state.bitboards['black_king']
        friends_occ = state.black_occ
        enemy_occ = state.white_occ

    empty_squares = ~state.all_occ

    king_square = bit_indices(king_bb)[0]

    #Define direction and shifts
    directions = [
        (8,   None),                      # North
        (-8,  None),                      # South
        (1,   FILE_H_MASK),              # East (can't move if on H file)
        (-1,  FILE_A_MASK),              # West
        (9,   FILE_H_MASK),              # NE
        (7,   FILE_A_MASK),              # NW
        (-7,  FILE_H_MASK),              # SE
        (-9,  FILE_A_MASK),              # SW
    ]

    for offset, edge_mask in directions:
        to_sq = king_square + offset
        if 0 <= to_sq < 64:
            if edge_mask:
                if not (np.uint64(1) << king_square) & edge_mask:
                    continue  # would wrap around board edge
            to_mask = np.uint64(1) << to_sq
            if not (to_mask & friends_occ):  # can move to empty or enemy square
                moves.append((king_square, to_sq))

    return moves



def generate_knight_moves(state, color):
    moves = []
    knight_bb = state.bitboards[f'{color}_knight']
    own_occ = state.white_occ if color == 'white' else state.black_occ

    def shift_knight(pos, offset):
        return pos << offset if offset > 0 else pos >> abs(offset)

    # Precomputed shifts and masks to prevent wrap-around
    knight_offsets = [
        (17, 0x7f7f7f7f7f7f7f7f),  # NNE
        (15, 0xfefefefefefefefe), # NNW
        (10, 0x3f3f3f3f3f3f3f3f), # ENE
        (6,  0xfcfcfcfcfcfcfcfc), # WNW
        (-17, 0xfefefefefefefefe),# SSW
        (-15, 0x7f7f7f7f7f7f7f7f),# SSE
        (-10, 0xfcfcfcfcfcfcfcfc),# WSW
        (-6,  0x3f3f3f3f3f3f3f3f) # ESE
    ]

    for from_sq in range(64):
        if (knight_bb >> from_sq) & 1:
            from_mask = 1 << from_sq
            for offset, mask in knight_offsets:
                if (from_mask & mask) != 0:
                    to_sq = from_sq + offset
                    if 0 <= to_sq < 64:
                        to_mask = 1 << to_sq
                        if not (own_occ & to_mask):
                            moves.append((from_sq, to_sq))
    return moves

    



#Helpers to shift 

def shift_north(bb): return (bb << 8)  #move up one rank, mask to ensure still fits 64
def shift_south(bb): return (bb >> 8) 
def shift_northeast(bb): return (bb << 9) & np.uint64(0xFEFEFEFEFEFEFEFE)#mask to prevent wrap around 
def shift_northwest(bb): return (bb <<7) & np.uint64(0x7F7F7F7F7F7F7F7F)

def shift_southeast(bb): return (bb >> 9) & np.uint64(0xFEFEFEFEFEFEFEFE)#mask to prevent wrap around 
def shift_southwest(bb): return (bb >> 7) & np.uint64(0x7F7F7F7F7F7F7F7F)

def shift_east(bb): return (bb >> 1) & np.uint64(0xFEFEFEFEFEFEFEFE)
def shift_west(bb): return (bb << 1) & np.uint64(0x7F7F7F7F7F7F7F7F)

def bit_indices(bb):
    #return inices of set bits (0-63)
    return [i for i in range(64) if (bb >> i) & 1]