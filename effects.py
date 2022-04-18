"""
Contains the classes for the pebbles (desolated areas), bubbles (water), and grass (non-desolated land).
"""
from ursina import *
from random import randint
from tile_colors import rock_color, tile_green, fertilized_color


class Pebble(Entity):
	def __init__(self, position):
		super().__init__(position=position, model=None)
		# Placing a random number of pebbles in a random spot on top of the tile with a rock color
		self.pebbles = [
			Entity(
				parent=self,
				model="assets/tile",
				scale=(
					randint(2, 5) / 20,
					.02 + randint(1, 3) / 20,
					randint(2, 4) / 20
				),
				color=rock_color(),
				position=(
					randint(-3, 3) / 10,
					0,
					randint(-3, 3) / 10
				)
			) \
			for _ in range(randint(2, 3))
		]


class Bubble(Entity):
	def __init__(self, position):
		super().__init__(position=position, model="plane", texture="assets/bubbles_0.png")
		self.current_frame = 0
		self.change_frame()

	def change_frame(self):
		self.current_frame += 1
		if self.current_frame > 2: self.current_frame = 0
		self.texture = f"assets/bubbles_{self.current_frame}.png"
		invoke(self.change_frame, delay=.8 + randint(0, 1) / 10)


class Grass(Entity):
	def __init__(self, position):
		super().__init__(position=position, model=None)
		self.grass = [
			Entity(
				parent=self,
				model="assets/tile",
				scale=(
					randint(2, 5) / 20,
					.02 + randint(1, 3) / 20,
					randint(2, 4) / 20
				),
				color=tile_green(),
				position=(
					randint(-3, 3) / 10,
					0,
					randint(-3, 3) / 10
				)
			) \
			for _ in range(randint(2, 3))
		]

class Dirt(Entity):
	def __init__(self, position):
		super().__init__(position=position, model=None)
		self.grass = [
			Entity(
				parent=self,
				model="assets/tile",
				scale=(
					randint(2, 5) / 20,
					.02 + randint(1, 3) / 20,
					randint(2, 4) / 20
				),
				color=fertilized_color(),
				position=(
					randint(-3, 3) / 10,
					0,
					randint(-3, 3) / 10
				)
			) \
			for _ in range(randint(2, 3))
		]
