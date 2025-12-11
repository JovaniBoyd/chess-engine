import numpy as np

SQUARE_MASKS = [np.uint64(1) << i for i in range(64)]

class BitboardState:
    def __init__(self):
        self.bitboards = { 
            'white_pawns' : np.uint64(0),
            'black_pawns' : np.uint64(0),
            'white_knight' : np.uint64(0),
            'black_knight' : np.uint64(0),
            'white_rook' : np.uint64(0),
            'black_rook' : np.uint64(0),
            'white_bishop' : np.uint64(0),
            'black_bishop' : np.uint64(0),
            'white_queen' : np.uint64(0),
            'black_queen' : np.uint64(0),
            'white_king' : np.uint64(0),
            'black_king' : np.uint64(0)

        }
        

        self.white_occ = np.uint64(0) #bitboard representing all squares occupied by white pieces (bit at i is 1 if occupied)
        self.black_occ = np.uint64(0)   
        self.all_occ = np.uint64(0) #bitboard representing all occupied squares
    
        self.init_starting_position()
        #if fen:
            #self.load_fen(fen)

        self.turn_step = 0 # 0 = select, 1 = destination
        self.selection = 100

        self.current_turn = 'white' #Track who's turn
        self.valid_moves = []

    def init_starting_position(self):
        for i in range(8, 16):
            self.bitboards['white_pawns'] |= SQUARE_MASKS[i]#setting the bitboard for white pawns

        for i in range (48, 56):
            self.bitboards['black_pawns'] |= SQUARE_MASKS[i]

        for i in [1, 6]:
                self.bitboards['white_knight'] |= SQUARE_MASKS[i]

        for i in [57, 62]:
                self.bitboards['black_knight'] |= SQUARE_MASKS[i]

        for i in [0, 7]:
            self.bitboards['white_rook'] |= SQUARE_MASKS[i]

        for i in [56, 63]:
            self.bitboards['black_rook'] |= SQUARE_MASKS[i]

        for i in [2, 5]:
                self.bitboards['white_bishop'] |= SQUARE_MASKS[i]

        for i in [58, 61]:
                self.bitboards['black_bishop'] |= SQUARE_MASKS[i]

        for i in [3]:  # d1 - Queen on d-file
            self.bitboards['white_queen'] |= SQUARE_MASKS[i]

        for i in [59]:  # d8
            self.bitboards['black_queen'] |= SQUARE_MASKS[i]

        for i in [4]:  # e1 - King on e-file
                self.bitboards['white_king'] |= SQUARE_MASKS[i]

        for i in [60]:  # e8
                self.bitboards['black_king'] |= SQUARE_MASKS[i]



    def get_occupied_squares(self, piece_type):
        bb = self.bitboards[piece_type]
        return [i for i in range(64) if (bb >> i) & 1] #return list of ints



    def load_fen(self, fen_str):
        pass