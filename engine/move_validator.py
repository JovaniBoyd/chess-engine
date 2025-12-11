"""
Move Validator - Handles king safety, check detection, castling, and en passant
"""
import numpy as np
from engine.move_generator import (
    generate_pawn_moves, generate_knight_moves, generate_bishop_moves,
    generate_rook_moves, generate_queen_moves, generate_king_moves,
    bit_indices
)


def is_square_attacked(state, square, by_color):
    """
    Check if a square is attacked by any piece of the given color.
    Used for check detection and castling validation.
    """
    # Get attacker's pieces
    if by_color == 'white':
        pawns = state.bitboards['white_pawns']
        knights = state.bitboards['white_knight']
        bishops = state.bitboards['white_bishop']
        rooks = state.bitboards['white_rook']
        queens = state.bitboards['white_queen']
        king = state.bitboards['white_king']
    else:
        pawns = state.bitboards['black_pawns']
        knights = state.bitboards['black_knight']
        bishops = state.bitboards['black_bishop']
        rooks = state.bitboards['black_rook']
        queens = state.bitboards['black_queen']
        king = state.bitboards['black_king']
    
    file = square % 8
    rank = square // 8
    
    # Check pawn attacks
    if by_color == 'white':
        # White pawns attack diagonally upward
        if file > 0 and square >= 9:
            if (pawns >> (square - 9)) & 1:  # SW of target
                return True
        if file < 7 and square >= 7:
            if (pawns >> (square - 7)) & 1:  # SE of target
                return True
    else:
        # Black pawns attack diagonally downward
        if file > 0 and square <= 54:
            if (pawns >> (square + 7)) & 1:  # NW of target
                return True
        if file < 7 and square <= 56:
            if (pawns >> (square + 9)) & 1:  # NE of target
                return True
    
    # Check knight attacks
    knight_offsets = [
        (-17, lambda f, r: f > 0 and r > 1),   # SSW
        (-15, lambda f, r: f < 7 and r > 1),   # SSE
        (-10, lambda f, r: f > 1 and r > 0),   # WSW
        (-6,  lambda f, r: f < 6 and r > 0),   # ESE
        (6,   lambda f, r: f > 1 and r < 7),   # WNW
        (10,  lambda f, r: f < 6 and r < 7),   # ENE
        (15,  lambda f, r: f > 0 and r < 6),   # NNW
        (17,  lambda f, r: f < 7 and r < 6),   # NNE
    ]
    for offset, valid_check in knight_offsets:
        from_sq = square - offset
        if 0 <= from_sq < 64 and valid_check(file, rank):
            if (knights >> from_sq) & 1:
                return True
    
    # Check king attacks (for adjacent squares)
    king_offsets = [-9, -8, -7, -1, 1, 7, 8, 9]
    for offset in king_offsets:
        from_sq = square + offset
        if 0 <= from_sq < 64:
            from_file = from_sq % 8
            # Prevent wrap-around
            if abs(from_file - file) <= 1:
                if (king >> from_sq) & 1:
                    return True
    
    # Check sliding pieces (rook, bishop, queen)
    # Rook directions (and queen)
    rook_directions = [
        (8, lambda f, r: r < 7),    # North
        (-8, lambda f, r: r > 0),   # South
        (1, lambda f, r: f < 7),    # East
        (-1, lambda f, r: f > 0),   # West
    ]
    
    for delta, can_continue in rook_directions:
        current = square
        while True:
            current_file = current % 8
            current_rank = current // 8
            if not can_continue(current_file, current_rank):
                break
            next_sq = current + delta
            if next_sq < 0 or next_sq > 63:
                break
            # Prevent wrap on east/west
            if delta in [1, -1] and abs((next_sq % 8) - current_file) != 1:
                break
            
            next_mask = np.uint64(1) << next_sq
            if (rooks | queens) & next_mask:
                return True
            if state.all_occ & next_mask:
                break  # Blocked by another piece
            current = next_sq
    
    # Bishop directions (and queen)
    bishop_directions = [
        (9, lambda f, r: f < 7 and r < 7),   # NE
        (7, lambda f, r: f > 0 and r < 7),   # NW
        (-7, lambda f, r: f < 7 and r > 0),  # SE
        (-9, lambda f, r: f > 0 and r > 0),  # SW
    ]
    
    for delta, can_continue in bishop_directions:
        current = square
        while True:
            current_file = current % 8
            current_rank = current // 8
            if not can_continue(current_file, current_rank):
                break
            next_sq = current + delta
            if next_sq < 0 or next_sq > 63:
                break
            
            next_mask = np.uint64(1) << next_sq
            if (bishops | queens) & next_mask:
                return True
            if state.all_occ & next_mask:
                break
            current = next_sq
    
    return False


def is_in_check(state, color):
    """Check if the given color's king is in check."""
    if color == 'white':
        king_bb = state.bitboards['white_king']
        attacker = 'black'
    else:
        king_bb = state.bitboards['black_king']
        attacker = 'white'
    
    king_squares = bit_indices(king_bb)
    if not king_squares:
        return False  # No king (shouldn't happen)
    
    king_sq = king_squares[0]
    return is_square_attacked(state, king_sq, attacker)


def make_move_copy(state, from_sq, to_sq):
    """
    Make a move on a copy of the state and return the new state.
    Used for checking if a move leaves the king in check.
    """
    import copy
    new_state = copy.deepcopy(state)
    
    from_mask = np.uint64(1) << from_sq
    to_mask = np.uint64(1) << to_sq
    
    # Find which piece is moving
    moved_piece = None
    for piece_name, bb in new_state.bitboards.items():
        if bb & from_mask:
            moved_piece = piece_name
            break
    
    if moved_piece is None:
        return new_state
    
    # Move the piece
    new_state.bitboards[moved_piece] &= ~from_mask
    new_state.bitboards[moved_piece] |= to_mask
    
    # Remove any captured piece
    for piece_name, bb in new_state.bitboards.items():
        if piece_name != moved_piece and bb & to_mask:
            new_state.bitboards[piece_name] &= ~to_mask
    
    # Update occupancy
    new_state.white_occ = (
        new_state.bitboards['white_pawns'] | new_state.bitboards['white_rook'] |
        new_state.bitboards['white_bishop'] | new_state.bitboards['white_knight'] |
        new_state.bitboards['white_queen'] | new_state.bitboards['white_king']
    )
    new_state.black_occ = (
        new_state.bitboards['black_pawns'] | new_state.bitboards['black_rook'] |
        new_state.bitboards['black_bishop'] | new_state.bitboards['black_knight'] |
        new_state.bitboards['black_queen'] | new_state.bitboards['black_king']
    )
    new_state.all_occ = new_state.white_occ | new_state.black_occ
    
    return new_state


def get_legal_moves(state, color):
    """
    Generate all legal moves for the given color.
    A move is legal if:
    1. It's a valid piece move
    2. It doesn't leave the king in check
    """
    # Generate all pseudo-legal moves
    pseudo_legal = []
    pseudo_legal += generate_pawn_moves(state, color)
    pseudo_legal += generate_knight_moves(state, color)
    pseudo_legal += generate_bishop_moves(state, color)
    pseudo_legal += generate_rook_moves(state, color)
    pseudo_legal += generate_queen_moves(state, color)
    pseudo_legal += generate_king_moves(state, color)
    
    # TODO: Add castling moves
    # pseudo_legal += generate_castling_moves(state, color)
    
    # Filter out moves that leave king in check
    legal_moves = []
    for from_sq, to_sq in pseudo_legal:
        new_state = make_move_copy(state, from_sq, to_sq)
        if not is_in_check(new_state, color):
            legal_moves.append((from_sq, to_sq))
    
    return legal_moves


def is_checkmate(state, color):
    """Check if the given color is in checkmate."""
    if not is_in_check(state, color):
        return False
    return len(get_legal_moves(state, color)) == 0


def is_stalemate(state, color):
    """Check if the given color is in stalemate (not in check but no legal moves)."""
    if is_in_check(state, color):
        return False
    return len(get_legal_moves(state, color)) == 0


def get_game_status(state, current_turn):
    """
    Returns the game status.
    Returns: 'ongoing', 'white_wins', 'black_wins', or 'stalemate'
    """
    if is_checkmate(state, current_turn):
        return 'black_wins' if current_turn == 'white' else 'white_wins'
    if is_stalemate(state, current_turn):
        return 'stalemate'
    return 'ongoing'