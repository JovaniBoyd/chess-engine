import pygame
import os

# Try to import assets, fall back to basic rendering if not available
try:
    from assets.assets import FONTS, PIECE_IMAGES
    ASSETS_AVAILABLE = True
except ImportError:
    ASSETS_AVAILABLE = False
    PIECE_IMAGES = {}
    FONTS = {}

TILE_SIZE = 80
BOARD_SIZE = TILE_SIZE * 8

# Colors
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)      # Yellow-green for selection
MOVE_HIGHLIGHT = (130, 151, 105)       # Green tint for legal move squares
MOVE_DOT_COLOR = (100, 111, 64)        # Darker green for move dots
CHECK_HIGHLIGHT = (255, 100, 100, 128) # Red tint for check

# Unicode pieces (fallback if images not available)
PIECE_SYMBOLS = {
    'white_king': '♔', 'white_queen': '♕', 'white_rook': '♖',
    'white_bishop': '♗', 'white_knight': '♘', 'white_pawns': '♙',
    'black_king': '♚', 'black_queen': '♛', 'black_rook': '♜',
    'black_bishop': '♝', 'black_knight': '♞', 'black_pawns': '♟',
}


def square_to_coords(square):
    """Convert board square (0-63) to screen coordinates."""
    row = 7 - (square // 8)
    col = square % 8
    x = col * TILE_SIZE
    y = row * TILE_SIZE
    return x, y


def draw_board(screen, state, legal_moves=None, in_check=False):
    """Draw the chess board with highlighting for selection, legal moves, and check."""
    
    # Get destination squares for the selected piece
    legal_destinations = set()
    if legal_moves and state.selection < 64:
        legal_destinations = {to_sq for from_sq, to_sq in legal_moves if from_sq == state.selection}
    
    # Find king square if in check
    king_square = None
    if in_check:
        king_key = f'{state.current_turn}_king'
        king_bb = state.bitboards.get(king_key, 0)
        if king_bb:
            king_square = (king_bb & -king_bb).bit_length() - 1
    
    for rank in range(8):
        for file in range(8):
            square = rank * 8 + file
            x = file * TILE_SIZE
            y = (7 - rank) * TILE_SIZE
            
            # Determine base square color
            if (rank + file) % 2 == 0:
                color = LIGHT
            else:
                color = DARK
            
            # Highlight selected square
            if state.selection == square:
                color = HIGHLIGHT_COLOR
            # Highlight legal move destinations
            elif square in legal_destinations:
                color = MOVE_HIGHLIGHT
            # Highlight king in check
            elif square == king_square and in_check:
                color = (255, 150, 150)  # Light red
            
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))
            
            # Draw indicators for legal moves
            if square in legal_destinations:
                center = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                # Check if square is empty (dot) or occupied (ring for capture)
                if not (state.all_occ >> square) & 1:
                    # Empty square - draw dot
                    pygame.draw.circle(screen, MOVE_DOT_COLOR, center, 12)
                else:
                    # Capture - draw ring
                    pygame.draw.circle(screen, MOVE_DOT_COLOR, center, 36, 5)


def draw_pieces(screen, state):
    """Draw all pieces on the board using images or Unicode fallback."""
    
    for piece_type in state.bitboards:
        image = PIECE_IMAGES.get(piece_type) if ASSETS_AVAILABLE else None
        
        for square in state.get_occupied_squares(piece_type):
            x, y = square_to_coords(square)
            
            if image:
                # Draw image centered in tile
                offset_x = (TILE_SIZE - image.get_width()) // 2
                offset_y = (TILE_SIZE - image.get_height()) // 2
                screen.blit(image, (x + offset_x, y + offset_y))
            else:
                # Fallback to Unicode symbols
                _draw_unicode_piece(screen, piece_type, x, y)


def _draw_unicode_piece(screen, piece_type, x, y):
    """Draw a piece using Unicode symbol (fallback when images unavailable)."""
    symbol = PIECE_SYMBOLS.get(piece_type, '?')
    font = pygame.font.SysFont('Segoe UI Symbol', 56)
    
    if piece_type.startswith('white'):
        color = (255, 255, 255)
        outline_color = (0, 0, 0)
    else:
        color = (0, 0, 0)
        outline_color = (50, 50, 50)
    
    text = font.render(symbol, True, color)
    text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
    
    # Draw outline
    outline = font.render(symbol, True, outline_color)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        outline_rect = outline.get_rect(center=(x + TILE_SIZE // 2 + dx, y + TILE_SIZE // 2 + dy))
        screen.blit(outline, outline_rect)
    
    screen.blit(text, text_rect)


def draw_info_panel(screen, state, in_check=False, game_status='ongoing'):
    """Draw the info panel below and beside the board."""
    
    # Bottom panel
    pygame.draw.rect(screen, 'chocolate', [0, BOARD_SIZE, BOARD_SIZE, 100])
    pygame.draw.rect(screen, 'aliceblue', [0, BOARD_SIZE, BOARD_SIZE, 100], 5)
    
    # Side panel
    pygame.draw.rect(screen, (50, 50, 50), [BOARD_SIZE, 0, 200, BOARD_SIZE + 100])
    pygame.draw.rect(screen, 'aliceblue', (BOARD_SIZE, 0, 200, BOARD_SIZE + 100), 5)
    
    # Get fonts
    if ASSETS_AVAILABLE and FONTS:
        medium_font = FONTS.get("medium", pygame.font.SysFont('Arial', 32))
        small_font = FONTS.get("small", pygame.font.SysFont('Arial', 20))
    else:
        medium_font = pygame.font.SysFont('Arial', 32)
        small_font = pygame.font.SysFont('Arial', 20)
    
    # Status text for bottom panel
    if game_status == 'white_wins':
        status = "CHECKMATE! White wins!"
        status_color = 'gold'
    elif game_status == 'black_wins':
        status = "CHECKMATE! Black wins!"
        status_color = 'gold'
    elif game_status == 'stalemate':
        status = "STALEMATE! Draw."
        status_color = 'gray'
    elif in_check:
        turn = state.current_turn.capitalize()
        if state.turn_step == 0:
            status = f"{turn}: CHECK! Select piece"
        else:
            status = f"{turn}: CHECK! Select destination"
        status_color = 'red'
    else:
        status_texts = [
            'White: select a piece to move',
            'White: select a destination',
            'Black: select a piece to move',
            'Black: select a destination'
        ]
        status = status_texts[state.turn_step]
        status_color = 'black'
    
    screen.blit(medium_font.render(status, True, status_color), (20, BOARD_SIZE + 30))
    
    # Side panel info
    panel_x = BOARD_SIZE + 15
    
    # Turn indicator
    turn_text = f"Turn: {state.current_turn.capitalize()}"
    screen.blit(small_font.render(turn_text, True, 'white'), (panel_x, 20))
    
    # Selection info
    if state.selection < 64:
        file_letter = chr(ord('a') + (state.selection % 8))
        rank_number = (state.selection // 8) + 1
        sel_text = f"Selected: {file_letter}{rank_number}"
    else:
        sel_text = "Selected: None"
    screen.blit(small_font.render(sel_text, True, 'white'), (panel_x, 50))
    
    # Check indicator
    if in_check and game_status == 'ongoing':
        screen.blit(small_font.render("CHECK!", True, 'red'), (panel_x, 80))
    
    # Instructions
    instructions = [
        "Controls:",
        "Click to select piece",
        "Click to move",
        "Click same to deselect",
        "Press R to reset"
    ]
    for i, inst in enumerate(instructions):
        color = 'lightgray' if i > 0 else 'white'
        screen.blit(small_font.render(inst, True, color), (panel_x, 130 + i * 25))