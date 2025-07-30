import pygame

pygame.font.init()
PIECE_IMAGES = {
    'white_pawns': pygame.transform.scale(pygame.image.load('assets/images/white pawn.png'), (70, 70)),
    'black_pawns': pygame.transform.scale(pygame.image.load('assets/images/black pawn.png'), (70, 70)),
    'white_knight': pygame.transform.scale(pygame.image.load('assets/images/white knight.png'), (80, 80)),
    'black_knight': pygame.transform.scale(pygame.image.load('assets/images/black knight.png'), (80, 80)),
    'white_rook': pygame.transform.scale(pygame.image.load('assets/images/white rook.png'), (80, 80)),
    'black_rook': pygame.transform.scale(pygame.image.load('assets/images/black rook.png'), (80, 80)),
    'white_bishop': pygame.transform.scale(pygame.image.load('assets/images/white bishop.png'), (80, 80)),
    'black_bishop': pygame.transform.scale(pygame.image.load('assets/images/black bishop.png'), (80, 80)),
    'white_queen': pygame.transform.scale(pygame.image.load('assets/images/white queen.png'), (80, 80)),
    'black_queen': pygame.transform.scale(pygame.image.load('assets/images/black queen.png'), (80, 80)),
    'white_king': pygame.transform.scale(pygame.image.load('assets/images/white king.png'), (80, 80)),
    'black_king': pygame.transform.scale(pygame.image.load('assets/images/black king.png'), (80, 80))

    # Add other pieces similarly...
}

FONTS = {
    "small": pygame.font.Font('freesansbold.ttf', 20),
    "medium": pygame.font.Font('freesansbold.ttf', 40),
   #  "medium": pygame.font.SysFont("arial", 32),

    "large": pygame.font.Font('freesansbold.ttf', 50)
}





# set images
black_queen = pygame.image.load('assets/images/black queen.png')
black_queen = pygame.transform.scale(black_queen, (80, 80))
black_king = pygame.image.load('assets/images/black king.png')
black_king = pygame.transform.scale(black_king, (80, 80))
black_pawn = pygame.image.load('assets/images/black pawn.png')
black_pawn = pygame.transform.scale(black_pawn, (55, 55))
black_knight = pygame.image.load('assets/images/black knight.png')
black_knight = pygame.transform.scale(black_knight, (80, 80))
black_rook = pygame.image.load('assets/images/black rook.png')
black_rook = pygame.transform.scale(black_rook, (80, 80))
black_bishop = pygame.image.load('assets/images/black bishop.png')
black_bishop = pygame.transform.scale(black_bishop, (80, 80))


white_queen = pygame.image.load('assets/images/white queen.png')
white_queen = pygame.transform.scale(white_queen, (80, 80))
white_king = pygame.image.load('assets/images/white king.png')
white_king = pygame.transform.scale(white_king, (80, 80))
white_pawn = pygame.image.load('assets/images/white pawn.png')
white_pawn = pygame.transform.scale(white_pawn, (55, 55))
white_knight = pygame.image.load('assets/images/white knight.png')
white_knight = pygame.transform.scale(white_knight, (80, 80))
white_rook = pygame.image.load('assets/images/white rook.png')
white_rook = pygame.transform.scale(white_rook, (80, 80))
white_bishop = pygame.image.load('assets/images/white bishop.png')
white_bishop = pygame.transform.scale(white_bishop, (80, 80))

white_images = [white_pawn, white_queen, white_bishop, white_knight, white_rook,  white_king]
black_images = [black_pawn, black_queen, black_bishop, black_knight, black_rook,  black_king]

piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']
# check variables/flashing counter


