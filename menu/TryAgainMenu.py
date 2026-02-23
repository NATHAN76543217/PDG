from sources.menu.Menu import Menu
from sources.utils.Button import Button
from sources.utils.MyConfig import *


class TryAgainMenu(Menu) :
	def __init__(self, pdg):
		super().__init__("Try Again", pdg) 

	def init_components(self):
		super().init_components()
		B1 = Button("Yes", 36, True, int(self.w / 4), 1 * int(self.h / 5), 2 * int(self.w / 4), int(self.h / 5))
		B2 = Button("No", 36, False, int(self.w / 4), 3 * int(self.h / 5), 2 * int(self.w / 4), int(self.h / 5))
		self.buttons = [B1, B2]

	def event_handling(self, event):
		match event.type:
			case pygame.VIDEORESIZE:
				super().event_handling(event)
			case pygame.KEYDOWN:
				match event.key:
					case pygame.K_ESCAPE:
						print("Try Again: ESCAPE key pressed, interpreted as 'No'.")
						self.running = False
						self.answer = False
					case _:
						super().event_handling(event)
			case _:
				# Un-overrided events are just passed to parent
				return super().event_handling(event)

	def renderComponents(self):
		self.blitText("Play Again", 50, (255, 0, 0), self.pdg.window.get_rect().midtop[0], int(self.pdg.window.get_size()[1] / 15) * 2)
		# # Remaining text
		remaining_rewards = self.pdg.db.nbAvailableRewards()
		if (self.w < 400 or self.h < 400):
			remaining_size = 20
		else:
			remaining_size = 30
		if remaining_rewards > 1:
			remaining_text = f"You still have {remaining_rewards} rewards to win."
		elif remaining_rewards == 1:
			remaining_text = f"You have only 1 remaining reward to win."
		else:
			print("BUG: Invalid negative value")
		# REVIEW remaining_rect.inflate_ip(0, -int(win_h / 5))
		self.blitText(remaining_text, remaining_size, (0, 100, 20), self.pdg.window.get_rect().midtop[0], 2 * int(self.h / 5) + int(self.h / 10))
