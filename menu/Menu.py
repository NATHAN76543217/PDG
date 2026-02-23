from sources.utils.MyConfig import *

class Menu :
	def __init__(self, name, pdg):
		self.pdg = pdg
		self.answer = None
		self.backgroundColor = BACKGROUND_COLOR
		self.selected_button = 0
		self.buttons = []
		self.w = 0
		self.h = 0
		self.name = name
		pygame.display.set_caption("-- " + name + " --")
	
	def init_components(self):
		if (self.pdg.window == None):
			self.pdg.window = pygame.display.set_mode((WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT), pygame.RESIZABLE)
		self.w, self.h = self.pdg.window.get_size()

	def event_handling(self, event):
		match event.type:
			case pygame.QUIT:
				self.running = False

			case pygame.VIDEORESIZE:
				self.w, self.h = self.pdg.resize_screen([event.w, event.h]).get_size()
				self.init_components()
			case pygame.KEYDOWN:
				match event.key:
					case pygame.K_ESCAPE:
						if (DEBUG_MODE):
							print("Menu: ESCAPE key pressed, interpreted as 'No'.")
						self.answer = False
					case pygame.K_UP | pygame.K_RIGHT:
						if self.selected_button > 1:
							self.selected_button -= 1
						elif self.selected_button <= 1:
							self.selected_button = len(self.buttons)
					case pygame.K_DOWN| pygame.K_LEFT:
						if self.selected_button < len(self.buttons):
							self.selected_button += 1
						elif self.selected_button == len(self.buttons):
							self.selected_button = 1
					case (pygame.K_RETURN | pygame.K_KP_ENTER | pygame.K_SPACE):
						if self.selected_button == 0:
							if (len(self.buttons) > 0):
								self.selected_button = 1
						elif self.selected_button > 0:
							self.answer = self.buttons[self.selected_button - 1].value 
							if (DEBUG_MODE):
								print(f"Menu: Button <{self.buttons[self.selected_button - 1].name}> selected.({self.answer})")

			case pygame.MOUSEBUTTONDOWN:
				x, y = pygame.mouse.get_pos()
				for button in self.buttons:
					if (button.rect.collidepoint(x, y)):
						if (DEBUG_MODE):
							print(f"Menu: Button <{button.name}> clicked.")
						self.answer = button.value 

	def blitText(self, text, fontSize, textColor, centerX : int, centerY: int):
		"""Blit text centered on X at the Y y * h / 15 
		"""
		used_font = pygame.font.SysFont(None, fontSize)
		surface_text = used_font.render(text, True, textColor)
		text_rect = surface_text.get_rect(centerx=centerX, centery=centerY)
		self.pdg.window.blit(surface_text, text_rect)

	def renderComponents(self):
		"""Method to be overided by childs instances
		"""
		pass


	def render(self):
		print("Rendering menu:", self.name)
		self.running = True
		while self.running:
			for event in pygame.event.get():
				self.event_handling(event)

			# Render background
			self.pdg.window.fill(self.backgroundColor)

			# Components
			self.renderComponents()

			# # Buttons
			for index, button in enumerate(self.buttons):
				self.pdg.window.blit(button.surface, (button.x, button.y))
				# Highlight selected button
				if (self.selected_button > 0 and self.selected_button - 1 == index):
					pygame.draw.rect(self.pdg.window, (255, 0, 0), button.rect, 3)
				else:
					pygame.draw.rect(self.pdg.window, (160, 82, 45), button.rect, 3)
					
			# Update screen
			pygame.display.flip()
			pygame.time.Clock().tick(60)
			if self.answer != None:
				self.running = False

		return self.answer
