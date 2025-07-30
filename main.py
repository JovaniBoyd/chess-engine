import pygame
import numpy as np
from engine.bitboard import BitboardState
from engine.move_generator import *
from ui.pygame_ui import draw_board, draw_pieces, BOARD_SIZE

def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE + 200, BOARD_SIZE+ 100))
    pygame.display.set_caption("Bitboard Chess Visualizer")

    clock = pygame.time.Clock()
    state = BitboardState()

    running = True
    while running:
        clock.tick(60)
        screen.fill((0,0,0))
        draw_board(screen, state)
        draw_pieces(screen, state)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif  event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x_coord, y_coord = pygame.mouse.get_pos()
                handle_click(x_coord, y_coord, state)


            

        pygame.display.flip()

    pygame.quit()

def handle_click(x, y, state):
#Handles mouse clock at screen coords (x,y), updates state if valid move is made

    
    clicked_square = coords_to_square(x, y)
    if clicked_square is None or clicked_square < 0 or clicked_square > 63:
        return # ignore outside clicks
    
    # FOR step 0: select a piece
    if state.turn_step % 2 == 0:
        # check if clicked square has apiece belonging to curr player
        if state.current_turn == 'white':
            if ((state.bitboards['white_pawns'] >> clicked_square) & 1) or \
            ((state.bitboards['white_rook'] >> clicked_square) & 1) or \
            ((state.bitboards['white_bishop'] >> clicked_square) & 1) or \
            ((state.bitboards['white_knight'] >> clicked_square) & 1) or \
            ((state.bitboards['white_king'] >> clicked_square) & 1) or \
            ((state.bitboards['white_queen'] >> clicked_square) & 1):
                state.selection = clicked_square
                state.turn_step += 1    #go to destination selection
        elif state.current_turn == 'black':
            if ((state.bitboards['black_pawns'] >> clicked_square) & 1) or \
            ((state.bitboards['black_rook'] >> clicked_square) & 1) or \
            ((state.bitboards['black_bishop'] >> clicked_square) & 1) or \
            ((state.bitboards['black_knight'] >> clicked_square) & 1) or \
            ((state.bitboards['black_king'] >> clicked_square) & 1) or \
            ((state.bitboards['black_queen'] >> clicked_square) & 1):
                state.selection = clicked_square
                state.turn_step += 1

    # FOR STEP 1: Select Destination
    elif state.turn_step % 2 == 1:
        from_sq = state.selection
        to_sq = clicked_square

        if from_sq == to_sq:
            state.selection = 100
            state.turn_step -= 1
            return

        #====== Generate legal moves ===
        legal_moves = []
        legal_moves += generate_pawn_moves(state, state.current_turn)
        legal_moves += generate_rook_moves(state, state.current_turn) 
        legal_moves += generate_bishop_moves(state, state.current_turn) 
        legal_moves += generate_knight_moves(state, state.current_turn) 
        legal_moves += generate_queen_moves(state, state.current_turn)
        legal_moves += generate_king_moves(state, state.current_turn)
        if (from_sq, to_sq) not in legal_moves:
            print("Illegal move.")
            return
        #==== make move /// modified to change opps board when captured

        from_mask = np.uint64(1) << from_sq
        to_mask = np.uint64(1) << to_sq

        if state.current_turn == 'white':
            # Move white pawn if it's the one selected
            if (state.bitboards['white_pawns'] >> from_sq) & 1:
                state.bitboards['white_pawns'] &= ~from_mask
                state.bitboards['white_pawns'] |= to_mask

            # Move white rook if selected
            if (state.bitboards['white_rook'] >> from_sq) & 1:
                state.bitboards['white_rook'] &= ~from_mask
                state.bitboards['white_rook'] |= to_mask

            # Move white bishop if selected
            if (state.bitboards['white_bishop'] >> from_sq) & 1:
                state.bitboards['white_bishop'] &= ~from_mask
                state.bitboards['white_bishop'] |= to_mask

            if (state.bitboards['white_queen'] >> from_sq) & 1:
                state.bitboards['white_queen'] &= ~from_mask
                state.bitboards['white_queen'] |= to_mask

            if (state.bitboards['white_knight'] >> from_sq) & 1:
                state.bitboards['white_knight'] &= ~from_mask
                state.bitboards['white_knight'] |= to_mask

            if (state.bitboards['white_king'] >> from_sq) & 1:
                state.bitboards['white_king'] &= ~from_mask
                state.bitboards['white_king'] |= to_mask    

            # Remove black piece at destination if present
            for piece in ['black_pawns', 'black_rook', 'black_bishop', 'black_knight', 'black_queen', 'black_king']:
                if (state.bitboards[piece] >> to_sq) & 1:
                    state.bitboards[piece] &= ~to_mask

        else:  # Black's turn
            if (state.bitboards['black_pawns'] >> from_sq) & 1:
                state.bitboards['black_pawns'] &= ~from_mask
                state.bitboards['black_pawns'] |= to_mask

            if (state.bitboards['black_rook'] >> from_sq) & 1:
                state.bitboards['black_rook'] &= ~from_mask
                state.bitboards['black_rook'] |= to_mask

            if (state.bitboards['black_bishop'] >> from_sq) & 1:
                state.bitboards['black_bishop'] &= ~from_mask
                state.bitboards['black_bishop'] |= to_mask

            if (state.bitboards['black_knight'] >> from_sq) & 1:
                state.bitboards['black_knight'] &= ~from_mask
                state.bitboards['black_knight'] |= to_mask

            if (state.bitboards['black_queen'] >> from_sq) & 1:
                state.bitboards['black_queen'] &= ~from_mask
                state.bitboards['black_queen'] |= to_mask

            if (state.bitboards['black_king'] >> from_sq) & 1:
                state.bitboards['black_king'] &= ~from_mask
                state.bitboards['black_king'] |= to_mask

            for piece in ['white_pawns', 'white_rook', 'white_bishop','white_knight', 'white_queen', 'white_king']:
                if (state.bitboards[piece] >> to_sq) & 1:
                    state.bitboards[piece] &= ~to_mask





        #==== Update occupancy and switch turn ====

        state.selection = 100
        state.turn_step = 0
        state.white_occ = state.bitboards['white_pawns'] | state.bitboards['white_rook'] | state.bitboards['white_bishop'] | state.bitboards['white_knight']| state.bitboards['white_queen'] | state.bitboards['white_king']
        state.black_occ = state.bitboards['black_pawns'] | state.bitboards['black_rook'] | state.bitboards['black_bishop'] | state.bitboards['black_knight'] |state.bitboards['black_queen'] | state.bitboards['black_king']
        state.all_occ = state.white_occ | state.black_occ
        state.current_turn = 'black' if state.current_turn == 'white' else 'white'


            

    


def coords_to_square(x, y):
    #Covert screen coordinates to board square
    TILE_SIZE = 80
    #ignore clicks outside the board
    if x < 0 or x >= 8 * TILE_SIZE or y < 0 or y >= 8 * TILE_SIZE:
        return None
    
    file = x // TILE_SIZE
    rank = 7 - (y // TILE_SIZE)

    return rank * 8 + file



if __name__ == "__main__":
    main()