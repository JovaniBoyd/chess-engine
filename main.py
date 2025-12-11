import pygame
import numpy as np
from engine.bitboard import BitboardState
from engine.move_generator import *
from engine.move_validator import get_legal_moves, is_in_check, get_game_status
from ui import draw_board, draw_pieces, draw_info_panel, BOARD_SIZE, TILE_SIZE


def main():
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE + 200, BOARD_SIZE + 100))
    pygame.display.set_caption("Bitboard Chess Engine")

    clock = pygame.time.Clock()
    state = BitboardState()
    
    # Initialize occupancy boards
    update_occupancy(state)
    
    # Compute initial legal moves
    legal_moves = get_legal_moves(state, state.current_turn)
    game_status = 'ongoing'

    running = True
    while running:
        clock.tick(60)
        screen.fill((30, 30, 30))
        
        # Check for check and game status
        in_check = is_in_check(state, state.current_turn)
        
        draw_board(screen, state, legal_moves, in_check)
        draw_pieces(screen, state)
        draw_info_panel(screen, state, in_check, game_status)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_status == 'ongoing':
                    x_coord, y_coord = pygame.mouse.get_pos()
                    move_made = handle_click(x_coord, y_coord, state, legal_moves)
                    if move_made:
                        # Recompute legal moves for new turn
                        legal_moves = get_legal_moves(state, state.current_turn)
                        game_status = get_game_status(state, state.current_turn)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset game
                    state = BitboardState()
                    update_occupancy(state)
                    legal_moves = get_legal_moves(state, state.current_turn)
                    game_status = 'ongoing'

        pygame.display.flip()

    pygame.quit()


def update_occupancy(state):
    """Update all occupancy bitboards."""
    state.white_occ = (
        state.bitboards['white_pawns'] | state.bitboards['white_rook'] |
        state.bitboards['white_bishop'] | state.bitboards['white_knight'] |
        state.bitboards['white_queen'] | state.bitboards['white_king']
    )
    state.black_occ = (
        state.bitboards['black_pawns'] | state.bitboards['black_rook'] |
        state.bitboards['black_bishop'] | state.bitboards['black_knight'] |
        state.bitboards['black_queen'] | state.bitboards['black_king']
    )
    state.all_occ = state.white_occ | state.black_occ


def handle_click(x, y, state, legal_moves):
    """
    Handle mouse click at screen coords (x,y).
    Returns True if a move was made, False otherwise.
    """
    clicked_square = coords_to_square(x, y)
    if clicked_square is None or clicked_square < 0 or clicked_square > 63:
        return False

    # Step 0: Select a piece
    if state.turn_step == 0:
        # Check if clicked square has a piece belonging to current player
        if state.current_turn == 'white':
            own_occ = state.white_occ
        else:
            own_occ = state.black_occ
        
        if (own_occ >> clicked_square) & 1:
            # Check if this piece has any legal moves
            piece_has_moves = any(from_sq == clicked_square for from_sq, to_sq in legal_moves)
            if piece_has_moves:
                state.selection = clicked_square
                state.turn_step = 1
        return False

    # Step 1: Select destination
    elif state.turn_step == 1:
        from_sq = state.selection
        to_sq = clicked_square

        # Click same square to deselect
        if from_sq == to_sq:
            state.selection = 100
            state.turn_step = 0
            return False
        
        # Check if clicking on another own piece (switch selection)
        if state.current_turn == 'white':
            own_occ = state.white_occ
        else:
            own_occ = state.black_occ
        
        if (own_occ >> to_sq) & 1:
            # Switch to selecting this piece instead
            piece_has_moves = any(f == to_sq for f, t in legal_moves)
            if piece_has_moves:
                state.selection = to_sq
            return False

        # Check if move is legal
        if (from_sq, to_sq) not in legal_moves:
            return False

        # Make the move
        make_move(state, from_sq, to_sq)
        
        # Reset selection and switch turn
        state.selection = 100
        state.turn_step = 0
        state.current_turn = 'black' if state.current_turn == 'white' else 'white'
        
        return True

    return False


def make_move(state, from_sq, to_sq):
    """Execute a move on the board."""
    from_mask = np.uint64(1) << from_sq
    to_mask = np.uint64(1) << to_sq

    # Find and move the piece
    for piece_name in list(state.bitboards.keys()):
        if (state.bitboards[piece_name] >> from_sq) & 1:
            # Move this piece
            state.bitboards[piece_name] &= ~from_mask
            state.bitboards[piece_name] |= to_mask
            break

    # Remove any captured piece
    enemy_pieces = ['black_pawns', 'black_rook', 'black_bishop', 'black_knight', 
                    'black_queen', 'black_king'] if state.current_turn == 'white' else \
                   ['white_pawns', 'white_rook', 'white_bishop', 'white_knight',
                    'white_queen', 'white_king']
    
    for piece in enemy_pieces:
        if (state.bitboards[piece] >> to_sq) & 1:
            state.bitboards[piece] &= ~to_mask
            break

    # Update occupancy
    update_occupancy(state)


def coords_to_square(x, y):
    """Convert screen coordinates to board square (0-63)."""
    if x < 0 or x >= 8 * TILE_SIZE or y < 0 or y >= 8 * TILE_SIZE:
        return None
    
    file = x // TILE_SIZE
    rank = 7 - (y // TILE_SIZE)
    
    return rank * 8 + file


if __name__ == "__main__":
    main()