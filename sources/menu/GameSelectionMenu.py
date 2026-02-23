from sources.menu.Menu import Menu
from sources.games.TileGame import TileGame
from sources.utils.Button import Button
from sources.utils.MyConfig import *

class EmptySlot :
	name = "More games coming Soon"
	@staticmethod
	def valueHandler(x):
		return None

GameList = [TileGame, EmptySlot]

class GameSelectionMenu(Menu) :
	def __init__(self, pdg):
		super().__init__("Game Selection", pdg) 

	def init_components(self):
		super().init_components()

		nbGames = len(GameList)
		gameByRow = 2
		self.buttons = []
		for idx, game in enumerate(GameList):		
			self.buttons.append(Button(game.name, 19, game.valueHandler(game),  (idx % 2) * int(self.w / 2) + int(self.w / 12), 2 * int(self.h / 6), int(self.w / 3), int(self.h / 6)))

		self.buttons.append(Button("Quit", 36, False, int(self.w / 3), 10 * int(self.h / 15), int(self.w / 3), 2 * int(self.h / 15)))

	def event_handling(self, event):
		match event.type:
			case pygame.VIDEORESIZE:
				super().event_handling(event)
			case pygame.KEYDOWN:
				match event.key:
					case _:
						super().event_handling(event)
			case _:
				# Un-overrided events are just passed to parent
				return super().event_handling(event)

	def renderComponents(self):
		if (self.answer != None):
			self.running = False
		self.blitText("Select your game", 50, (255, 0, 0), self.pdg.window.get_rect().midtop[0], int(self.pdg.window.get_size()[1] / 15) * 2)
