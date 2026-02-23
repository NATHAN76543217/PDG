import os
from dotenv import load_dotenv

# Env initialisation
load_dotenv()

APPLICATION_NAME = os.getenv("APPLICATION_NAME", "Photo Distribution Game aka PDG")
GIVER_NAME = os.getenv("GIVER_NAME", "-Redacted-")

WORKING_DIRECTORY=os.getenv("WORKING_DIRECTORY", ".")
SERIALIZED_DIRECTORY = os.path.join(WORKING_DIRECTORY, os.getenv("SERIALIZED_DIR_NAME", "Serialized"))
ASSETS_DIRECTORY = os.path.join(WORKING_DIRECTORY, os.getenv("ASSETS_DIR_NAME", "assets"))
REWARDS_DIRECTORY = os.path.join(WORKING_DIRECTORY, os.getenv("REWARDS_DIR_NAME", "Rewards"))
DEFAULT_DB_PATH = os.path.join(WORKING_DIRECTORY, os.getenv("DB_FILENAME", "db.txt"))
SERIALIZED_NAME_LENGHT = int(os.getenv("SERIALIZED_NAME_LENGHT", 16))

BACKGROUND_COLOR = (240, 240, 240)
DEBUG_MODE = int(os.getenv("DEBUG_MODE", 1))

WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", 600))
WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", 700))
HEADER_HEIGHT = int(os.getenv("HEADER_HEIGHT", 100))

WINDOW_MAX_WIDTH = int(os.getenv("WINDOW_MAX_WIDTH", 800))
WINDOW_MIN_WIDTH = int(os.getenv("WINDOW_MIN_WIDTH", 300))
WINDOW_MAX_HEIGHT = int(os.getenv("WINDOW_MAX_HEIGHT", 800))
WINDOW_MIN_HEIGHT = int(os.getenv("WINDOW_MIN_HEIGHT", 300))

GAME_MAX_WIDTH = WINDOW_MAX_WIDTH
GAME_MIN_WIDTH = WINDOW_MIN_WIDTH
GAME_MAX_HEIGHT = WINDOW_MAX_HEIGHT - HEADER_HEIGHT
GAME_MIN_HEIGHT = WINDOW_MIN_HEIGHT - HEADER_HEIGHT


# TileGame
NB_BLOCK_X=int(os.getenv("NB_BLOCK_X", 4))
NB_BLOCK_Y=int(os.getenv("NB_BLOCK_Y", 4))
INITIAL_SHUFFLE=int(os.getenv("INITIAL_SHUFFLE", 4))

# Common imports
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
from pygame.locals import *
