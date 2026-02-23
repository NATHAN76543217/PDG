import os
import pickle

import string
import base64
import secrets

from io import BytesIO 
from PIL import Image as PIL_image

from sources.utils.MyConfig import *
from sources.utils.Reward import Reward
from sources.utils.Button import Button
from sources.games.TileGame import TileGame
from sources.menu.TryAgainMenu import TryAgainMenu
from sources.menu.GameClearMenu import GameClearMenu
from sources.menu.GameSelectionMenu import GameSelectionMenu

class PDG_database :
	"""Handle all the database operations for PDG
	"""
	def __init__(self, db_path, assets_path, serial_path):
		self.db_path = db_path
		self.assets_path = assets_path
		self.serial_path = serial_path
		self.loaded_bdd = {
			"Rewards" : []
			}

	def serializeImages(self, file_list):
		"""Load images, serialize them and write them on filesystem and create the Reward entry in the db.

		Args:
			file_list (str): list of files to load

		Returns:
			_type_: _description_
		"""
		nbFiles = len(file_list)
		for idx, filename in enumerate(file_list):
			try:
				newReward = self.serialize_one_image(os.path.join(self.assets_path, filename))
			except PIL_image.UnidentifiedImageError as e:
				print(f"Serialization: Invalid image file skipping '{filename}'")
				continue
			print("Database: New", newReward, f" {idx + 1}/{nbFiles}")
			ret = self.write_serialized_file(newReward)
			if (ret == False):
				print("Database: Failed to write file: {filename}.")
				continue
			newReward.image = None
			self.loaded_bdd["Rewards"].append(newReward)
		return True


	def write_serialized_file(self, reward):
		filepath = os.path.join(self.serial_path, reward.serial_name)
		with open(filepath, mode="wb") as out_file:
			pickle.dump(reward, out_file)
		if (DEBUG_MODE):
			print(f"Database: Serial file {filepath} saved.")
		return True


	def write_db_to_file(self, db_path:str = ""):
		if (db_path == ""):
			db_path = self.db_path
		with open(db_path, "wb") as dbfile:
			pickle.dump(self.loaded_bdd, dbfile)
		print(f"Database: Database writed to {db_path}")
		
	def load_db_from_file(self, db_path):
		self.db_path = db_path
		with open(self.db_path, "rb") as db_file:
			self.loaded_bdd = pickle.load(db_file)
		if (self.loaded_bdd == None):
			print("Error: No BDD loaded.")
			return False
		if (DEBUG_MODE):
			print("PDG: Database successfully loaded.")
		return True

	def reorient_image(self, img):
		try:
			# Get EXIF orientation data
			exif = img._getexif()
			if exif is not None:
				orientation = exif.get(274)  # 274 is the EXIF tag for Orientation
				if orientation == 3:
					img = img.transpose(PIL_image.ROTATE_180)
				elif orientation == 6:
					img = img.transpose(PIL_image.ROTATE_270)
				elif orientation == 8:
					img = img.transpose(PIL_image.ROTATE_90)
		except (AttributeError, KeyError, TypeError):
			pass  # invalid or missing EXIF data
		return img 

	def serialize_one_image(self, filename):
		random_name = self.generate_random_string()
		if (DEBUG_MODE):
			print(f"Database: Processing <{filename}>")
		loaded_image = PIL_image.open(filename)  # Load image from file
		loaded_image = self.reorient_image(loaded_image)
		buffer = BytesIO()
		loaded_image.save(buffer, format="PNG")
		img_bytes = buffer.getvalue()
		base64_str = base64.b64encode(img_bytes).decode("utf-8")
		serial_path = os.path.join(self.serial_path, random_name)
		newReward = Reward(serial_path, filename, base64_str)
		return newReward

	def select_reward(self):
		"""Select a reward in database

		Returns: (Reward | Bool | None): 
   				Return None if no reward is available. 
   				Return False if no rewards are not granted. 
   				Else return the selected Reward. 
		"""
		if len(self.loaded_bdd["Rewards"]) < 1:
			return None
		for reward in self.loaded_bdd["Rewards"]:
			if reward.isWon() == False:
				return reward
			else:
				continue
		return False 

	def reset_rewards(self):
		"""Reset all won rewards in the database
		"""
		for reward in self.loaded_bdd["Rewards"]:
			reward.resetWon()
	
	def generate_random_string(self):
		length = SERIALIZED_NAME_LENGHT
		secure_string = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
		return secure_string

	def nbAvailableRewards(self):
		nbAvailableRewards = 0
		for reward in self.loaded_bdd["Rewards"]:
			if not reward.isWon():
				nbAvailableRewards += 1
		return nbAvailableRewards

class PhotoDistributionGame :
	def __init__(self, db_path:str = DEFAULT_DB_PATH, image:str = ASSETS_DIRECTORY, serial_dir:str = SERIALIZED_DIRECTORY, reward_dir:str = REWARDS_DIRECTORY):
		"""Warning: Arguments must be sanitized before the class instanciation.

		Args:
			db_path (str, optional): Path to the db.txt file. Defaults to DEFAULT_DB_PATH.
			image (str, optional): Path to an image or a directory. Defaults to ASSETS_DIRECTORY.
		"""
		self.database_path = db_path 
		self.serial_path = serial_dir
		self.assets_path = image 
		self.reward_dir = reward_dir
		self.db = PDG_database(self.database_path, self.assets_path, self.serial_path)
		self.selected_game : classmethod
		self.current_game = None
		self.current_reward = None
		self.window = None
		self.header_surface = None
		self.game_surface = None


	def select_reward(self):
		reward = self.db.select_reward()
		if reward == None:
			print("BUG: Empty database.")
			return None
		elif isinstance(reward, Reward):
			if (DEBUG_MODE):
				print("PDG: Selected reward : ", reward)
			self.current_reward = reward
			return True
		elif reward == False:
			print("PDG: Game cleared, all rewards are already awarded.")
			return False
		else:
			print("BUG: Invalid reward.")
			return None

	def openMenu(self, menu):
		TAM = menu(self)
		TAM.init_components()
		return TAM.render()

	def grantReward(self):
		if (not os.path.isdir(self.reward_dir)):
			print("PDG: Create the reward directory at '" + self.reward_dir + "'.")
			os.mkdir(self.reward_dir, mode=0o744)

		# Set reward as won in database
		for reward in self.db.loaded_bdd["Rewards"]:
			if reward.serial_name == self.current_reward.serial_name:
				reward.won()
				self.db.write_db_to_file(self.database_path)
				print(f"PDG: '{reward.serial_name}' updated as won in the database.")
				break
		# Write reward in the REWARDS directory
		output_path = os.path.join(self.reward_dir, os.path.basename(self.current_reward.original_path))
		self.current_reward.original_image.save(output_path)
		print(f"PDG: Reward '{self.current_reward.serial_name}' written at {output_path}.")
		return True

	def setGame(self, game:classmethod):
		"""Select the game that will be played.

		Args:
			gameID (int): The ID of the game you want to play
		"""
		self.selected_game = game

	def get_loadable_elements(self, allowed_extentions=[".jpg", ".jpeg", ".png"]):
		"""If self.assets_path point to a file -> Check the extention type and return the given file 
			If self.assets_path point to a directory -> Return the name of all files ending with <allowed_extentions> in this directory 
		"""
		loadable_files = []
		if ( os.path.isfile(self.assets_path)):
			path, ext = os.path.splitext(self.assets_path)
			if (ext in allowed_extentions):
				if  (DEBUG_MODE):
					print(f"Assets: Valid {ext} file.")
			else:
				print(f"Assets: Unsupported {ext} extention.")
		elif (os.path.isdir(self.assets_path)):
			dir = os.listdir(self.assets_path)
			for elem in dir:
				main, ext = os.path.splitext(elem)
				if ext in allowed_extentions:
					loadable_files.append(elem) 
		else:
			print("Error: Invalid type for assets path.")
			return []
		return loadable_files

	def clearSerialDir(self):
		# Clear serialised directory before writting
		print(f"Database: Removing content from data directory. ({self.serial_path})")
		for filename in os.listdir(self.serial_path):
			file_path = os.path.join(self.serial_path, filename)
			if os.path.isfile(file_path):
				if (DEBUG_MODE):
					print(f"Suppression de : {file_path}")
				try:
					os.remove(file_path)
				except FileNotFoundError:
					print(f"Erreur : Le fichier '{file_path}' n'existe pas.")
				except PermissionError:
					print(f"Erreur : Permission refusée pour supprimer '{file_path}'.")
				except OSError as e:
					print(f"Erreur système imprévue : {e}")


	def create_database(self):
		files_to_load = self.get_loadable_elements()
		print(f"Database: {len(files_to_load)} loadable elements found.")
		if (DEBUG_MODE):
			print(f"Full list = {files_to_load}")
		# serialize files and write database
		if (len(files_to_load) == 0):
			print(f"Error: No loadable files found in {self.assets_path}.")
			return False

		self.clearSerialDir()

		if not self.db.serializeImages(files_to_load):
			print("Error: Failed to add files to the database")
			return False
		else:
			processed = len(self.db.loaded_bdd["Rewards"])
			print(f"Database: {processed} images serialized with success.")
		self.db.write_db_to_file()
		return True

	def reset_database(self):
		if not self.db.load_db_from_file(self.database_path):
			print("Error: Fail to load the database.")
			return False
		self.db.reset_rewards()
		self.db.write_db_to_file()

	def display_header(self):
		quit_button = Button("Return to menu.", 30, False, 0, 0, int(self.window.get_size()[0]), HEADER_HEIGHT)
		self.window.blit(quit_button.surface, (quit_button.x, quit_button.y))
		# Header Borders
		pygame.draw.rect(self.window, (160, 82, 45), quit_button.rect, 3)

	def resize_screen(self, newSize:list):
		print(">> Resizing screen <<")
		# Ensure a restricted windows size
		if (newSize[0] > WINDOW_MAX_WIDTH):
			newSize[0] = WINDOW_MAX_WIDTH
		elif newSize[0] < WINDOW_MIN_WIDTH:
			newSize[0] = WINDOW_MIN_WIDTH
		if (newSize[1] > WINDOW_MAX_HEIGHT):
			newSize[1] = WINDOW_MAX_HEIGHT
		elif newSize[1] < WINDOW_MIN_HEIGHT:
			newSize[1] = WINDOW_MIN_HEIGHT

		self.window = pygame.display.set_mode(newSize, pygame.RESIZABLE)
		win_w, win_h = self.window.get_size()
		print("Window size = ", (win_w, win_h) )
  
		# Compute Header zone
		header_rect = pygame.Rect(0, 0, win_w, HEADER_HEIGHT)
		if (DEBUG_MODE):
			print("Header Rect = ", header_rect)
		self.header_surface = self.window.subsurface(header_rect)

		# Compute Game zone
		game_rect = pygame.Rect(0, HEADER_HEIGHT, win_w, win_h - HEADER_HEIGHT)
		print("  Game Rect = ", game_rect)
		self.game_surface = self.window.subsurface(game_rect)

		self.display_header()
		return self.game_surface
  
	def play(self):

		self.window = pygame.display.set_mode((WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT), pygame.RESIZABLE)

		print(f"PDG: Selected Game: {self.selected_game.name}.")
		self.current_game = self.selected_game(self, self.current_reward)	
		self.current_game.init()
		print("PDG: Game start !")
		outcome = self.current_game.play(self.game_surface)
		return outcome

	def main_loop(self):
		if not self.db.load_db_from_file(self.database_path):
			print("Error: Fail to load the database.")
			return False
		
		pygame.init()
		pygame.font.init()
		alive = True
		while alive:
			if (self.db.nbAvailableRewards() == 0):
				print("All rewards are already awarded.")
				self.openMenu(GameClearMenu)
				break
			game_selected = self.openMenu(GameSelectionMenu)
			if (game_selected == False):
				alive = None
			else:
				play = True
				print("PDG: Play", game_selected.name)
				self.setGame(game_selected)
				while play:
					if (not self.select_reward()):
						alive = False 
						print("BUG: No reward available.")
					if self.play() == True:
						self.grantReward()
					else:
						print("Sorry but you loose the game, no rewards will be granted.")

					if (self.db.nbAvailableRewards() == 0):
						print("No more rewards available. Game Cleared !")
						self.openMenu(GameClearMenu)
						play = False
						alive = False
					else:
						play = self.openMenu(TryAgainMenu)
		pygame.quit()