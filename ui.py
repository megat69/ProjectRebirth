from ursina import *
import tiles
import json
# Loading the settings
with open("settings.json", "r", encoding="utf-8") as settings_file:
	class SETTINGS:
		SETTINGS_AS_JSON = json.load(settings_file)

	def add_attrs_to_settings(cls, dictionary):
		for key, value in dictionary.items():
			if isinstance(value, dict):
				setattr(cls, key, SETTINGS())
				add_attrs_to_settings(getattr(cls, key), value)
			else:
				setattr(cls, key, value)
	add_attrs_to_settings(SETTINGS, SETTINGS.SETTINGS_AS_JSON)
	del add_attrs_to_settings

def _select_slot(slot:int):
	"""
	Selects a slot for the buildables in tiles.
	"""
	tiles.SELECTED_SLOT = slot
	# Makes it visible which button is selected.
	for i in range(4):
		UI._instance.buttons[4].buttons[i].color = color.light_gray
	if slot >= 4:
		UI._instance.caret.visible = False
		UI._instance.buttons[4].buttons[slot - 4].color = color.lime
	else:
		UI._instance.caret.visible = True
		UI._instance.caret.position = UI._instance.buttons[slot].position + Vec2(0,.5)

def _pass():
	pass

class UI(Entity):
	"""
	Contains all of the UI for the game
	"""
	_instance = None
	def __new__(cls, *args, **kwargs):
		if not isinstance(cls._instance, cls):
			cls._instance = Entity.__new__(cls, *args, **kwargs)
		return cls._instance

	def __init__(self):
		super().__init__(
			parent=camera.ui,
			model="quad",
			scale=(.75, .15),
			position=(0, -.5),
			origin=(0, -.5),
			color=color.black50
		)
		# Creating each button
		icons = ("windturbineicon", "water_can", "watertower", "rockifier")
		self.buttons = [
			Button(
				parent=self,
				position=(x, .5),
				scale=(.18, .7),
				origin=(0, 0),
				text=str(tiles.SLOTS_MONEY_WORTH[i]),
				text_origin=(.5, -.5),
				text_color=color.lime,
				radius=.2
			)\
			for i, x in enumerate((-.4, -.2, 0, .2, .4))
		]
		for i in range(len(icons)):
			self.buttons[i].icon = f"assets/{icons[i]}.png"
		# Assigning to the first 4 buttons to select the corresponding slot on click
		self.buttons[0].on_click = lambda: _select_slot(0)
		self.buttons[1].on_click = lambda: _select_slot(1)
		self.buttons[2].on_click = lambda: _select_slot(2)
		self.buttons[3].on_click = lambda: _select_slot(3)
		self.buttons[4].on_click = lambda: _pass()
		self.buttons[4].color = color.rgba(0, 0, 0, 0)
		self.buttons[4].highlight_color = self.buttons[4].color
		self.buttons[4].pressed_color = self.buttons[4].color
		# Creating the buttons for the rotating drill
		self.buttons[4].buttons = []
		for pos in ((-.35, 0), (0, .35), (.35, 0), (0, -.35)):
			self.buttons[4].buttons.append(
				Button(
					parent=self.buttons[4],
					position=pos,
					scale=.3,
					color=color.light_gray,
					highlight_color=color.lime
				)
			)
		self.buttons[4].buttons[0].on_click = lambda: _select_slot(4)
		self.buttons[4].buttons[1].on_click = lambda: _select_slot(5)
		self.buttons[4].buttons[2].on_click = lambda: _select_slot(6)
		self.buttons[4].buttons[3].on_click = lambda: _select_slot(7)

		# Creating a caret so we know which button is selected
		self.caret = Entity(
			parent=self, model="quad", position=self.buttons[0].position + Vec2(0,.5), scale=(.02, .1), color=color.lime
		)

	def update(self):
		# Putting the button price tag in red if it is too expensive or green if you can buy it
		for i in range(len(self.buttons)):
			if tiles.MONEY >= tiles.SLOTS_MONEY_WORTH[i]:
				self.buttons[i].text_color = color.lime
			else:
				self.buttons[i].text_color = color.red
