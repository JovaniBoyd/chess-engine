import pygame
from assets import FONTS, piece_list,  PIECE_IMAGES

TILE_SIZE = 80
BOARD_SIZE = TILE_SIZE * 8

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
WHITE_PAWN_COLOR = (255, 255, 255)
BLACK_PAWN_COLOR = (0, 0, 0)

def draw_board(screen, state):
    for rank in range(8):
        for file in range(8):
            x = file * TILE_SIZE
            y = (7 - rank) * TILE_SIZE # flip vertically to match bitboard 

            if (rank + file) % 2 == 0:
                color = LIGHT
            else:
                color = DARK

            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

    
        pygame.draw.rect(screen, 'chocolate', [0, BOARD_SIZE, BOARD_SIZE, 100])
        pygame.draw.rect(screen, 'aliceblue', (BOARD_SIZE, 0, 200, BOARD_SIZE), 5)
        pygame.draw.rect(screen, 'aliceblue', [0, BOARD_SIZE, BOARD_SIZE, 100], 5)
        status_text = ['White: select a piece to move', 'White: select a destination',
                       'Black: select a piece to move', 'Black: select a destination']
        screen.blit(FONTS["medium"].render(status_text[state.turn_step], True, 'black'), (20, BOARD_SIZE + 20))


#def draw_pieces(screen, bitboards, images):

def draw_pieces(screen, state):
    for piece_type in state.bitboards:
        image = PIECE_IMAGES.get(piece_type)
        if image:
            for square in state.get_occupied_squares(piece_type):
                x, y = square_to_coords(square)

                offset_x = (TILE_SIZE - image.get_width()) // 2
                offset_y = (TILE_SIZE - image.get_height()) // 2

                screen.blit(image, (x + offset_x, y + offset_y))





def square_to_coords(square):
    row = 7 - (square // 8)
    col = square % 8
    x = col * TILE_SIZE
    y = row * TILE_SIZE
    return x, y
    
    

