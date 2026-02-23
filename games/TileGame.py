from __future__ import annotations
import os
import json
import random

from PIL import Image as PIL_image
from sources.utils.MyConfig import *
from sources.utils.Reward import Reward
from sources.utils.Button import Button

class TileGame :
	name = "Tile Game"
	@staticmethod
	def valueHandler(x):
		return x

	class Tile :
		def __init__(self, id : int, position : int, surface : pygame.Surface = None) :
			self.id = id
			self.position = position
			self.surface = surface

		def __str__(self):
			return str(f"Tile({str(self.id)}, {self.position}, {self.surface != None})")

		def __json__(self):
			return {
				"id": self.id,
				"pos": self.position,
				"Have surface": self.surface != None
			}
		def to_dict(self):
			return self.__json__()
		
		class TileEncoder(json.JSONEncoder):
			def default(self, obj):
				if isinstance(obj, TileGame.Tile):
					return obj.to_dict()
				return super().default(obj)

	def __init__(self, pdg, reward : Reward) :
		self.title = "-- Tile Game --"
		self.pdg = pdg
		self.reward = reward
		self.running = True
		self.victory = False
		self.tiles = {}
		self.w = 0
		self.h = 0
		self.nb_block_x = NB_BLOCK_X
		self.nb_block_y = NB_BLOCK_Y
		self.block_size_w = int(WINDOW_WIDTH / self.nb_block_x)
		self.block_size_h = int(WINDOW_HEIGHT / self.nb_block_y)
		self.nb_tile = self.nb_block_y * self.nb_block_x

	def init(self):
		if self.reward.image == None:
			if not self.reward.load_image():
				print("Error when loading Reward's image.")
				return False
			else:
				print("TileGame: Reward image loaded.")
		else:
			print("TileGame: Reward image already loaded.")

		print("TileGame: Originale image size:", self.reward.original_image.size)
		self.initial_image_scaling()
		print("TileGame: New image size:", self.reward.image.size)
		# Set screen size at the resricted image size + header
		self.game_screen = self.pdg.resize_screen([self.reward.image.size[0], self.reward.image.size[1] + HEADER_HEIGHT])
		self.block_size_w = int(self.game_screen.get_rect().size[0] / self.nb_block_x)
		self.block_size_h = int(self.game_screen.get_rect().size[1] / self.nb_block_y)
		self.w, self.h = self.reward.image.size
		self.split_initial_image(self.reward.image)
		self.initial_shuffle()
		return True

	def initial_image_scaling(self):
		"""
			Upscale image if it is smaller than min_win
			Downscale image if it is bigger than max_win
		"""
		img_w, img_h = self.reward.image.size
		if img_w > GAME_MAX_WIDTH or img_h > GAME_MAX_HEIGHT:
			self.reward.resize(GAME_MAX_WIDTH, GAME_MAX_HEIGHT)
		if (img_w < GAME_MIN_WIDTH or img_h < GAME_MIN_HEIGHT):
			self.reward.resize(GAME_MIN_WIDTH, GAME_MIN_HEIGHT)
			

		
	def split_initial_image(self, image):
		"""Split a given image into several tiles

		Args:
			image (str): The original background image
		"""
		if (DEBUG_MODE):
			print(f"  Blocksize = x={self.block_size_w}, y= {self.block_size_h}")

		for y in range(0, self.nb_block_y):
			self.tiles[y] = {}
			for x in range(0, self.nb_block_x):
				tile_position = (x * self.block_size_w, y * self.block_size_h)
				tile_image = None
				if  ((x + 1) * (y + 1) != self.nb_tile):
					p1_x = tile_position[0]
					p1_y = tile_position[1] 
					p2_x =  p1_x + self.block_size_w 
					p2_y =  p1_y + self.block_size_h 
					box = (p1_x, p1_y, p2_x, p2_y)
					subimage = image.crop(box)
					tile_image = pygame.image.fromstring(subimage.tobytes(), subimage.size, subimage.mode).convert_alpha()
				newTile = TileGame.Tile(y * self.nb_block_x + x, tile_position, tile_image)					
				self.tiles[y][x] = newTile


	def initial_shuffle(self):
		print(f"TileGame: Shuffling tiles {INITIAL_SHUFFLE} times.")
		empty_tile_position = [self.nb_block_x - 1, self.nb_block_y - 1]
		for move in range(INITIAL_SHUFFLE):
			# Select random position
			random_direction = random.choice(("NORTH", "SOUTH", "EAST", "WEST"))
			# print(f"TileGame: Direction = {random_direction}.")
			# Check if the move is allowed (boudaries)
			if (empty_tile_position[0] == 0 and random_direction == "WEST"):
				continue
			elif (empty_tile_position[0] >= self.nb_block_x - 1 and random_direction == "EAST"):
				continue

			if (empty_tile_position[1] == 0 and random_direction == "NORTH"):
				continue
			elif (empty_tile_position[1] >= self.nb_block_y - 1 and random_direction == "SOUTH"):
				continue
			
			# Compute new position
			newPos = list(empty_tile_position)
			match random_direction:
				case "NORTH":
					newPos[1] = newPos[1] - 1
				case "SOUTH":
					newPos[1] = newPos[1] + 1
				case "EAST":
					newPos[0] = newPos[0] + 1
				case "WEST":
					newPos[0] = newPos[0] - 1
				case _:
					print(f"Error invalid match key: {random_direction}.")

			# Swap positions
			# print(f"Swapping {empty_tile_position} and {newPos}.")
			self.swap(empty_tile_position, newPos)
			empty_tile_position = list(newPos)

	def play(self, screen):
		"""Run the game and return the outcome of the party
		"""
		self.game_screen = screen
		pygame.display.set_caption(self.title)
		outcome = self._game_loop()
		return outcome

	def printTiles(self):
		"""Print all Tiles in a pretty formated way
		"""
		print(json.dumps(self.tiles, indent=4, cls=TileGame.Tile.TileEncoder))

	def draw_tile(self, x, y):
		if self.tiles == None:
			return
		tile = self.tiles[y][x]
		if (tile == None):
			print("BUG: Drawing invalid tile.")
			return 
		if (tile.surface != None):
			# print(f"Draw {tile} at {tile.position}")
			# self.game_screen.blit(tile.surface, tile.position)
			self.game_screen.blit(tile.surface, tile.position)

	def blitText(self, text, fontSize, textColor, centerX : int, centerY: int):
		"""Blit text centered on X at the Y y * h / 15 
		"""
		used_font = pygame.font.SysFont(None, fontSize)
		surface_text = used_font.render(text, True, textColor)
		text_rect = surface_text.get_rect(centerx=centerX, centery=centerY)
		self.pdg.window.blit(surface_text, text_rect)

	def display_victory_text(self):
		screen_rect = self.game_screen.get_rect()
		if (screen_rect.w < 400 or screen_rect.h < 350):
			fontSize = 25
			btnFontSize = 18
		elif (screen_rect.w < 600 or screen_rect.h < 550):
			fontSize = 36
			btnFontSize = 25
		else:
			fontSize = 50
			btnFontSize = 30
		# self.game_screen.fill((30, 80, 50))
		self.blitText("Well done, you win !", fontSize, (235, 10, 110), self.pdg.window.get_rect().centerx, 4 * int(self.pdg.window.get_rect().h / 15))
		self.blitText("You can find your trophy saved at", fontSize, (235, 10, 110), self.pdg.window.get_rect().centerx, 5 * int(self.pdg.window.get_rect().h / 15))

		rewardPath = ""
		# Set reward as won in database
		for reward in self.pdg.db.loaded_bdd["Rewards"]:
			if reward.serial_name == self.reward.serial_name:
				rewardPath = os.path.join(self.pdg.reward_dir, os.path.basename(reward.original_path))
				break
		# Write reward in the REWARDS directory
		self.blitText("'" + rewardPath + "'", fontSize, (40, 40, 40), self.pdg.window.get_rect().centerx, 6 * int(self.pdg.window.get_rect().h / 15))
		# text2 = font.render("Press ENTER to continue", True, (245, 150, 190))
		quit_button = Button("Press ENTER to continue", btnFontSize, False, self.pdg.window.get_size()[0] / 4, 7 * int(self.pdg.window.get_size()[1] / 10), int(self.pdg.window.get_size()[0] / 2), int(self.pdg.window.get_size()[1] / 10))
		self.pdg.window.blit(quit_button.surface, (quit_button.x, quit_button.y))
		# text1_rect = text1.get_rect(center=screen_rect.center)
		# text2_rect = text2.get_rect(centerx=screen_rect.center[0], centery=int(screen_rect.h / 2) + int(screen_rect.h / 10))
		# self.game_screen.blit(text1, text1_rect)

	def emptyAround(self, x, y):
		""" Check if the position (x, y) have an empty neightbour
		Args:
			x (int): x coordinate
			y (int): y coordinate

		Returns:
			tuple: Return (x, y) or None
		"""
		# Check left
		if x > 0:
			# self.printTiles()
			if self.tiles[y][x - 1].surface == None:
				return (x - 1, y)
		# Check right
		if x < self.nb_block_x - 1:
			if self.tiles[y][x + 1].surface == None:
				return (x + 1, y)
		# Check up
		if y > 0:
			if self.tiles[y - 1][x].surface == None:
				return (x, y - 1)
		# Check down
		if y < self.nb_block_y - 1:
			if self.tiles[y + 1][x].surface == None:
				return (x, y + 1)
		return None

	def swap(self, tileA, tileB):
		"""

		Args:
			tileA (tuple): positions in the format (x, y)
			tileB (tuple): positions in the format (x, y)
		"""
		tmp = TileGame.Tile(self.tiles[tileA[1]][tileA[0]].id, (0, 0), self.tiles[tileA[1]][tileA[0]].surface)

		self.tiles[tileA[1]][tileA[0]].id = self.tiles[tileB[1]][tileB[0]].id
		self.tiles[tileA[1]][tileA[0]].surface = self.tiles[tileB[1]][tileB[0]].surface
  
		self.tiles[tileB[1]][tileB[0]].id = tmp.id
		self.tiles[tileB[1]][tileB[0]].surface = tmp.surface

	def click_on_tile(self, pos_x, pos_y):
		tile_x = int(pos_x / self.block_size_w)
		tile_y = int(pos_y / self.block_size_h)
		if (tile_x > self.nb_block_x - 1 ):
			tile_x = self.nb_block_x - 1 
		if (tile_y > self.nb_block_y - 1 ):
			tile_y = self.nb_block_y - 1

		if (DEBUG_MODE):
			print(f"TileGame: Clicked at ({pos_x}, {pos_y}) on [{tile_x}, {tile_y}]")
		tile = self.tiles[tile_y][tile_x]
		# Check if tile is not a hole and have an empty neightbour to move on
		dest = None
		if tile.surface != None:
			dest = self.emptyAround(tile_x, tile_y)
			if dest != None:
				print(f"TileGame: Move [{tile_x},{tile_y}] to [{dest[0]},{dest[1]}].")
				self.swap((tile_x, tile_y), dest)
				if (self.isVictoryConfiguration()):
					print("TileGame: You WIN !!!")
					self.victory = True

	def _locate_empty(self):
		for y in self.tiles:
			for x in self.tiles[y]:
				if (self.tiles[y][x].surface == None):
					return (x,y)

	def arrow_move(self, keypressed):
		empty = self._locate_empty()
		target = empty
		match keypressed:
			case pygame.K_UP:
				if (target[1] < self.nb_block_y - 1):
					print("TileGame: Arrow UP")
					target = (empty[0], empty[1] + 1)
			case pygame.K_DOWN:
				if (target[1] > 0):
					print("TileGame: Arrow DOWN")
					target = (empty[0], empty[1] - 1)
			case pygame.K_LEFT:
				if (target[0] < self.nb_block_x - 1):
					print("TileGame: Arrow LEFT")
					target = (empty[0] + 1, empty[1])
			case pygame.K_RIGHT:
				# Click on tile bellow the empty tile
				if (target[0] > 0):
					print("TileGame: Arrow RIGHT")
					target = (empty[0] - 1, empty[1])
			case _:
				print(f"TileGame: Error: Invalid keypressed value ({keypressed})")
		target_pos = self.tiles[target[1]][target[0]].position
		self.click_on_tile(target_pos[0], target_pos[1])

	def isVictoryConfiguration(self):
		current = -1
		for y in range(0, self.nb_block_y):
			for x in range(0, self.nb_block_x):
				if (self.tiles[y][x].id == current + 1):
					current += 1 
				else:
					break
		if (current == self.nb_tile - 1):
			return True
		else:
			return False

	def window_resize(self, newSize):
		# Resize Window
		self.game_screen = self.pdg.resize_screen(newSize)
		game_w, game_h = self.game_screen.get_rect().size
		if (DEBUG_MODE):
			print("Previous game size: ", self.reward.image.size)
		print("New game size: ", game_w, game_h)
		self.reward.resize(game_w, game_h)

		self.block_size_w = int(game_w / self.nb_block_x)
		self.block_size_h = int(game_h / self.nb_block_y)

		# Resize Tiles
		for y in self.tiles:
			for x in self.tiles[y]:
				self.tiles[y][x].position = (x * self.block_size_w, y * self.block_size_h)
				if (self.tiles[y][x].surface == None):
					continue
				source_pos_x = (self.tiles[y][x].id % self.nb_block_x) * self.block_size_w
				source_pos_y = int(self.tiles[y][x].id / self.nb_block_y) * self.block_size_h
				newbox = (source_pos_x, source_pos_y, source_pos_x + self.block_size_w, source_pos_y + self.block_size_h)
				subimage = self.reward.image.crop(newbox)
				self.tiles[y][x].surface = pygame.image.frombytes(subimage.tobytes(), subimage.size, subimage.mode).convert_alpha()
		
	def _game_loop(self):
		print("Entering game loop.")
		while self.running:
			self.game_screen.fill((20, 20, 20))
			# Event selection
			for event in pygame.event.get():
				match event.type:
					case pygame.QUIT:
						self.running = False
					case pygame.VIDEORESIZE:
						self.window_resize([event.w, event.h])
					case pygame.KEYDOWN:
						match event.key:
							case pygame.K_ESCAPE:
								print("ESCAPE_KEY pressed.")
								self.running = False
							case (pygame.K_UP | pygame.K_DOWN | pygame.K_LEFT | pygame.K_RIGHT):
								if not self.victory:
									self.arrow_move(event.key)
							case (pygame.K_KP_ENTER | pygame.K_RETURN | pygame.K_SPACE):
								if self.victory:
									self.running = False
				# Mouse click
					case pygame.MOUSEBUTTONDOWN:
						if (self.victory):
							# Once win message is displayed, closethe game on click
							self.running = False
						else:
							x, y = pygame.mouse.get_pos()
							if y < HEADER_HEIGHT:
								self.running = False
							else:
								self.click_on_tile(x, y - HEADER_HEIGHT)


			# Print tiles
			for y in range(0, self.nb_block_y):
				for x in range(0, self.nb_block_x):
					self.draw_tile(x, y)

			if (self.victory):
				self.display_victory_text()
			# Update screen
			pygame.display.flip()
			pygame.time.Clock().tick(60)

		return self.victory
