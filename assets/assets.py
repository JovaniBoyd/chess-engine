"""
Chess piece images and fonts.
Images should be placed in assets/images/ folder.
"""
import pygame
import os

# Initialize pygame font system
pygame.font.init()

# Get the directory where this file is located
ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')

def load_piece_image(filename, size):
    """Load and scale a piece image, return None if not found."""
    filepath = os.path.join(IMAGES_DIR, filename)
    try:
        if os.path.exists(filepath):
            img = pygame.image.load(filepath)
            return pygame.transform.scale(img, size)
    except pygame.error as e:
        print(f"Warning: Could not load {filepath}: {e}")
    return None

# Try to load piece images (will be None if images don't exist)
PIECE_IMAGES = {}

# Define piece image mappings
PIECE_IMAGE_FILES = {
    'white_pawns': ('white pawn.png', (70, 70)),
    'black_pawns': ('black pawn.png', (70, 70)),
    'white_knight': ('white knight.png', (80, 80)),
    'black_knight': ('black knight.png', (80, 80)),
    'white_rook': ('white rook.png', (80, 80)),
    'black_rook': ('black rook.png', (80, 80)),
    'white_bishop': ('white bishop.png', (80, 80)),
    'black_bishop': ('black bishop.png', (80, 80)),
    'white_queen': ('white queen.png', (80, 80)),
    'black_queen': ('black queen.png', (80, 80)),
    'white_king': ('white king.png', (80, 80)),
    'black_king': ('black king.png', (80, 80)),
}

# Load all piece images
for piece_name, (filename, size) in PIECE_IMAGE_FILES.items():
    img = load_piece_image(filename, size)
    if img:
        PIECE_IMAGES[piece_name] = img

# Fonts - use system fonts as fallback
try:
    FONTS = {
        "small": pygame.font.Font('freesansbold.ttf', 20),
        "medium": pygame.font.Font('freesansbold.ttf', 40),
        "large": pygame.font.Font('freesansbold.ttf', 50)
    }
except:
    FONTS = {
        "small": pygame.font.SysFont('Arial', 20),
        "medium": pygame.font.SysFont('Arial', 32),
        "large": pygame.font.SysFont('Arial', 42)
    }

# Legacy exports for compatibility
piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']

# Individual piece images (legacy compatibility)
white_images = []
black_images = []

for piece in ['pawns', 'queen', 'bishop', 'knight', 'rook', 'king']:
    white_key = f'white_{piece}'
    black_key = f'black_{piece}'
    if white_key in PIECE_IMAGES:
        white_images.append(PIECE_IMAGES[white_key])
    if black_key in PIECE_IMAGES:
        black_images.append(PIECE_IMAGES[black_key])