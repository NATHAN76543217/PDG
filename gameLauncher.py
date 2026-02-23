import os
import sys
import tempfile


# # Parsing library
import argparse

# Custom imports
from sources.PhotoDistributionGame import PhotoDistributionGame

from sources.utils.MyConfig import * 
from sources.utils.Reward import Reward

# Parsing

ERROR_DB_CODE = 3
ERROR_ASSETS_CODE = 4
ERROR_SERIAL_CODE = 5
ERROR_REWARDS_CODE = 6

## Instantiate the parser
parser = argparse.ArgumentParser(description=APPLICATION_NAME)

subparsers = parser.add_subparsers(dest='command', help='Available operations', title="Operations")

## Init operation parser

init_parser = subparsers.add_parser('init', help='Create a database file filled with all the images.')
init_parser.add_argument('--image', type=str, default=ASSETS_DIRECTORY,
					help='Path to an image or a directory of images.')
init_parser.add_argument('--serial', type=str, default=SERIALIZED_DIRECTORY,
					help='Path to the directory used to store compressed images.')
init_parser.add_argument('--db', type=str, default=DEFAULT_DB_PATH,
					help='Path to the database file.')

## Reset operation parser
reset_parser = subparsers.add_parser('reset', help='Reset the database as if no images was won.')
reset_parser.add_argument('--db', type=str, default=DEFAULT_DB_PATH,
					help='Path to the database file.')
## Play operation parser
play_parser = subparsers.add_parser('play', help='Play to the game of your choice and win images.')
play_parser.add_argument('--rewards', type=str, default=REWARDS_DIRECTORY,
					help='Path to the directory used to store obtained rewards.')
play_parser.add_argument('--serial', type=str, default=SERIALIZED_DIRECTORY,
					help='Path to the directory used to store compressed images.')
play_parser.add_argument('--db', type=str, default=DEFAULT_DB_PATH,
					help='Path to the database file.')
   
#>
# Ideas: Make a program for the grand parents that propose a new sliced photo 
# each days and once resolved, offer the this photo saved on their desktop.
# Needs: 
#   - a List of photos
#   - a Slice game
#   - a parameter page
#   - Changed parameters are applied on the next day challenge
#   - Fit the photo to the gale windows and lower resolution
#   - Obtained photos are in pretty high resolution once saved on desktop. 
#   - Obtained photos are stored on a dedicated folder the desktop.
#   - Photos cannot be acquired without playing (encryption).
#   - A photos is selected for each day, event if the previous day's photo wasn't won.


# Bonus:
#     Networking:
#        - Get time on a NTP server (cannot avant local time)
#        - Once local photos are expired get new photos from a server
#        - Secure this access with different tokens and folder for each family
#     Database:
#        - A BDD that save 
#  Could change the game played, the won photo is passed to the game in argument


# 
# > UTILS
#

def is_valid_dir_path(dirPath, param):
	"""Return 1 if the given path point to a valid directory.
		Return 2 if the given path point to a valid directory with <perm> permissions.
		Return 3 if the directory does not exist but is creatable.
		Return O if the directory does not exist and is not creatable

	Args:
		writable (bool): If True, check if the file is writable if it don't exist
	"""
	parent_dir = os.path.dirname(dirPath.rstrip(os.path.sep))
	# if no parent specified in path, use CWD 
	if (parent_dir == ""):
		parent_dir = "."
	if os.path.isdir(dirPath):
		try:
			with tempfile.TemporaryFile(dir=dirPath):
				return 2
		except (OSError, PermissionError):
			return 1
	elif os.path.isdir(parent_dir):
		if os.access(parent_dir, param):
			try:
			# Attempt to create a temporary directory inside the target path
				with tempfile.TemporaryDirectory(dir=parent_dir):
					return 3
			except (OSError, PermissionError):
				return 0
		else:
			print(f"> PATH: {dirPath}, PARENT: {parent_dir}, ACCESS: {os.access(parent_dir, os.W_OK)}")
			
	else:
		print("PARENT DONT EXIST")
		print(f"PATH: {dirPath}, PARENT: {parent_dir}, ACCESS: {os.access(parent_dir, os.W_OK)}")
	return 0


def is_valid_file_path(filePath, perm):
	""" Return 1 if the given path point to a valid file.
		Return 2 if the given path point to a valid file with <perm> permissions.
		Return 3 if the file does not exist but is creatable.
		Return 4 if the given path exist and don't point to a file.
		Return O if the file does not exist and is not creatable

	Args:
		filePath (str): The path to check.
	"""
	parent_dir = os.path.dirname(filePath)
	if (parent_dir == ""):
		parent_dir = "."
	if os.path.exists(filePath):
		if os.path.isfile(filePath):
			if os.access(filePath, os.R_OK and os.W_OK):
				return 2
			else:
				return 1
		else:
			return 4
	elif os.access(parent_dir, perm):
		try:
			with tempfile.TemporaryFile(dir=parent_dir):
				return 3
		except (OSError, PermissionError):
			return 0
	return 0



def is_valid_db_path(args, creatable=False):
	valid = is_valid_file_path(args.db, os.R_OK and os.W_OK)
	if (valid == 0):
		print(f"The database path ({args.db}) does not exist nor is creatable.")
	elif (valid == 1):
		print(f"The database path ({args.db}) miss read/write permissions.")
	elif (valid == 4):
		print(f"The database path ({args.db}) doesn't point to a file.")
	elif (valid == 3 and creatable):
		# Create database
		try:
			with open(args.db, 'a') as f:
				f.write('')
				print(f"PDG: (init) The database file was created at {args.db}).")
			return True
		except PermissionError:
			return False 
	elif (valid == 2):
		if (DEBUG_MODE):
			print(f"Debug: The database path {args.db} is valid.")
		return True
	else:
		print(f"BUG: Invalid 'valid' variable. ({valid})")
	return False

def is_valid_assets_path(args):
	if (args.command == "init"):
		# args.image
		print(f"ARGS.image = {args.image}")
		valid_file = is_valid_file_path(args.image, os.R_OK)
		if (valid_file == 2):
			if (DEBUG_MODE):
				print("Debug: The --image path is a readable file.")
			return True
		valid_dir = is_valid_dir_path(args.image, os.R_OK and os.X_OK)
		if (valid_dir == 2):
			if (DEBUG_MODE):
				print("Debug: The --image path is a Read-Execute directory.")
			return True
		elif (valid_dir == 1 or valid_dir == 3 or valid_dir == 0):
			print("PDG: The --image path is a not a valid directory.")
			if (valid_dir == 1):
				print("PDG: The --image path directory exist but lack permissions.")
				return False
		print("PDG: The --image path is not a valid file or directory.")
		return False
	else:
		# Play
		return True

def is_valid_serialized_directory(args):
	if os.path.isfile(args.serial):
		print(f"The serial path ({args.serial}) must be a directory, not a file.")
		return False
	valid = is_valid_dir_path(args.serial, os.R_OK and os.W_OK and os.X_OK)
	if valid == 0:
		print(f"The serial path ({args.serial}) must be a directory.")
		return False
	elif valid == 1:
		print(f"The serial directory ({args.serial})  is not writable.")
		return False
	elif valid == 2:
		if (DEBUG_MODE):
			print("Debug: The --serialized directory exist with correct permissions.")
		return True
	elif (valid == 3):
		if (args.command == "init"):
			os.mkdir(args.serial, mode=0o744)
			print("PDG: Init mode - The serial directory was created.")
			return True
		else:
			print(f"The serial directory ({args.serial}) does not exist.")
			return False
	else:
		return False


def is_valid_reward_directory(args):
	if os.path.isfile(args.rewards):
		print(f"The rewards path ({args.rewards}) must be a directory, not a file.")
		return False
	valid = is_valid_dir_path(args.rewards, os.R_OK and os.W_OK and os.X_OK)
	if valid == 0:
		print(f"The rewards path ({args.rewards}) must be a directory.")
		return False
	elif valid == 1:
		print(f"The rewards directory ({args.rewards}) is not writable.")
		return False
	elif valid == 2:
		if (DEBUG_MODE):
			print("Debug: The rewards directory exist with correct permissions.")
		return True
	elif (valid == 3):
		os.mkdir(args.rewards, mode=0o744)
		print("PDG: The rewards directory was created.")
		return True
	else:
		return False


if __name__ == "__main__":
	args = parser.parse_args()
	match args.command:
		case "init":
			print("---Mode Init selected--")
			if (not is_valid_db_path(args, creatable=True)):
				parser.exit(ERROR_DB_CODE, "Fatal: Invalid db path.")
			elif (not is_valid_assets_path(args)):
				parser.exit(ERROR_ASSETS_CODE, "Fatal: Invalid assets path.")
			elif (not is_valid_serialized_directory(args)):
				parser.exit(ERROR_SERIAL_CODE, "Fatal: Invalid serial directory.")
			PDG = PhotoDistributionGame(db_path=args.db, image=args.image, serial_dir=args.serial)
			PDG.create_database()

		case "play":
			print("---Mode Play selected--")
			if (not is_valid_db_path(args)):
				parser.exit(ERROR_DB_CODE, "Fatal: Invalid db path.")
			elif (not is_valid_serialized_directory(args)):
				parser.exit(ERROR_SERIAL_CODE, "Fatal: Invalid serial directory.")
			elif (not is_valid_reward_directory(args)):
				parser.exit(ERROR_REWARDS_CODE, "Fatal: Invalid rewards directory.")
			PDG = PhotoDistributionGame(db_path=args.db, serial_dir=args.serial, reward_dir=args.rewards)
			PDG.main_loop()

		case "reset":
			print("---Mode Reset selected--")
			if (not is_valid_db_path(args)):
				parser.exit(ERROR_DB_CODE, "Fatal: Invalid db path.")
			PDG = PhotoDistributionGame(db_path=args.db)
			print(f"Reseting database file ({args.db}).")
			PDG.reset_database()

		case _:
			print(f"BUG: Invalid command provided ({args.command})")

	print("---Exiting program--")


