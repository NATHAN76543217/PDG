from sources.utils.MyConfig import *
from sources.menu.Menu import Menu
from sources.utils.Button import Button

class GameClearMenu(Menu) :
	def __init__(self, pdg):
		super().__init__("Game Clear", pdg) 

	def init_components(self):
		super().init_components()
		quit_button = Button("Close the game.", 25, True, int(self.w / 4), 7 * int(self.h / 10), int(self.w / 2), int(self.h / 5))
		self.buttons = [quit_button]

	def event_handling(self, event):
		match event.type:
			# case pygame.KEYDOWN:
			# 	match event.key:
			# 		case pygame.K_ESCAPE:
			case _:
				# Un-overrided events are just passed to parent
				return super().event_handling(event)

	def renderComponents(self):
		# # Select font
		title_size = 50
		subtitle_size = 25
		thanks_size = 40
		if (self.w < 420 or self.h < 400):
			subtitle_size = 20
			thanks_size = 20
		# REVIEW look at the 'won' property instead of all rewards
		total_rewards = len(self.pdg.db.loaded_bdd["Rewards"])
		self.blitText("Game Complete !",  title_size, (205, 215, 130), self.pdg.window.get_rect().midtop[0], int(self.pdg.window.get_size()[1] / 15))
		self.blitText("You earned a total of " + str(total_rewards) + " photos.", subtitle_size, (30, 30, 30), self.pdg.window.get_rect().midtop[0], 3 * int(self.pdg.window.get_size()[1] / 15))
		thanks_texts = ["This game was offered to you", "by", f"{GIVER_NAME}", "   ", "Thanks you for playing !"]
		line = 1
		for idx, text in enumerate(thanks_texts) :
			line += 1
			self.blitText(text, thanks_size, (50, 60, 70), self.pdg.window.get_rect().midtop[0], int(self.pdg.window.get_size()[1] / 15) * line + 3 * int(self.pdg.window.get_size()[1] / 15))
		self.blitText("Game made by Nathan Lecaille (lecaille.nathan@outlook.fr)",  15, (20, 20, 20), self.pdg.window.get_rect().midtop[0], int(14.5 * int(self.pdg.window.get_size()[1] / 15)))
