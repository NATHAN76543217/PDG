from sources.utils.MyConfig import *

class Button:
	def __init__(self, name, text_size, value, x, y, w, h):
		self.name = name
		self.text_size = text_size
		self.value = value
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.rect = pygame.Rect((x, y, w, h))
		self.surface = pygame.Surface((w, h))
		self.color = (150, 150, 150)
		self.text_color = (0, 0, 0)
		self.surface.fill(self.color)
		button_font = pygame.font.SysFont(None, self.text_size)
		text = button_font.render(name, True, self.text_color)
		text_rect = text.get_rect(center=self.surface.get_rect().center, w=text.get_rect().w)
		self.surface.blit(text, text_rect)
