import pickle
import base64
from io import BytesIO 
from PIL import Image as PIL_image
from PIL import ImageOps as PIL_Ops

from sources.utils.MyConfig import *

class Reward :
	def __init__(self, serial_path : str, original_path : str = "", image = None):
		self.serial_path = serial_path
		self.serial_name = os.path.basename(serial_path)
		self.original_path = original_path
		self.image = image
		self.original_image = image
		self._won = False

	def __str__(self):
		res = str("Reward: {")
		res += self.serial_name
		res += "}"
		res += " from '"
		res += self.original_path
		res += "' "
		if self.image == None:
			res += "(Empty)."
		else:
			res += "(Loaded)."
		return res

	def resetWon(self):
		self._won = False

	def won(self):
		self._won = True

	def isWon(self):
		return self._won
	
	def load_image(self):
		with open(self.serial_path, "rb") as file:
			loaded_reward = pickle.load(file)
			self.image = PIL_image.open(BytesIO(base64.b64decode(loaded_reward.image)))
			self.original_image = self.image.copy()
		return True

	def resize(self, new_w : int, new_h : int):
		if (self.image == None):
			return
		# if (DEBUG_MODE):
		# 	print("resize image to ", new_w, new_h)
		self.image = self.original_image.resize((new_w, new_h), resample=PIL_image.Resampling.LANCZOS)