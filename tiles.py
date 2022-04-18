from ursina import *
from ursina.shaders import lit_with_shadows_shader
from random import randint
import json
from tile_colors import desolated_color, river_blue, tile_green, rock_color, fertilized_color
from text_popup_tool import text_popup
from effects import Pebble, Bubble, Grass, Dirt
from direct.stdpy import thread

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
# Contains the amount of converted tiles
CONVERTED_TILES = 0
MAX_CONVERTED_TILES = SETTINGS.misc.playable_area_size**2
TILES = []
MONEY = 500
SELECTED_SLOT = 0
"""
Slots :
0 - Power generator
1 - Land sanitizer
2 - Water pump
3 - Rockifier
4 - Drill
"""
SLOTS = ["Power Generator", "Land Sanitizer", "Water Pump", "Rockifier", "Drill (left)", "Drill (top)",
		 "Drill (right)", "Drill (bottom)"]
SLOTS_MONEY_WORTH = [50, 75, 75, 100, 150, 150, 150, 150]
POWER_GENERATORS = []
LAND_SANITIZERS = []
WATER_PUMPS = []
ROCKIFIERS = []
drill_used = False


def TILES_LUT(current_index, index):
	"""
	Returns the correct tile from the list depending on the index (seen below), or None if it doesn't exist.
	7 0 1
	6 X 2
	5 4 3
	"""
	final_index = None
	if index == 2:
		final_index = current_index + 1
	elif index == 6:
		final_index = current_index - 1
	elif index == 0:
		final_index = current_index - SETTINGS.misc.playable_area_size
	elif index == 1:
		final_index = current_index - (SETTINGS.misc.playable_area_size - 1)
	elif index == 7:
		final_index = current_index - (SETTINGS.misc.playable_area_size + 1)
	elif index == 4:
		final_index = current_index + SETTINGS.misc.playable_area_size
	elif index == 5:
		final_index = current_index + (SETTINGS.misc.playable_area_size - 1)
	elif index == 3:
		final_index = current_index + (SETTINGS.misc.playable_area_size + 1)

	if final_index >= len(TILES) or final_index < 0:
		return None
	else:
		return final_index


class Tile(Button):
	def __init__(self, noise_val, **kwargs):
		super().__init__(parent=scene, model="assets/tile", **kwargs)
		self.index = -1
		self.desolated = True
		self.is_rock = False
		self.is_river = False
		self.with_structure = False
		if SETTINGS.misc.hard_mode is True:
			self.fertilized = False
		"""self.wireframe_model = Entity(parent=self, model=Mesh(
			vertices = (
				Vec3(-.5, .5, .5),
				Vec3(-.5, -.5, .5),
				Vec3(-.5, .5, -.5),
				Vec3(-.5, -.5, -.5),
				Vec3(.5, .5, .5),
				Vec3(.5, .5, -.5),
				Vec3(.5, -.5, -.5)
			),
			triangles = (
				(0, 4, 5, 2),
				(3, 2, 5, 6),
				(3, 2, 5, 6)
			),
			mode='line',
			thickness=4
		), color=color.lime, visible=False, disabled=True)"""

		# Changes to rock if the noise value is between two specific numbers
		if 0.2 < noise_val < 0.25 and randint(1, 5) >= 3:
			self.is_rock = True
			self.desolated = False
			self.color = rock_color()
			# Removing one desolated tile because we cannot convert this one
			global MAX_CONVERTED_TILES
			MAX_CONVERTED_TILES -= 1

		# Changes to river if the noise value is between two specific numbers
		if -0.06 < noise_val < 0.06:
			self.is_river = True

		# Randomly places a pebble if the tile is not a river
		if self.is_river is False and SETTINGS.video.pebbles is True and randint(1, 5) == 5:
			self.pebble = Pebble(self.position + (0, .5, 0))


	def on_mouse_enter(self):
		if SETTINGS.video.enable_model_prerendering is False or self.hovered is False\
			or self.with_structure is True: return None

		# Prerenders the model on top of the tile
		self.prerendered_model = None

		# Loads the closest generator distance
		closest_generator = 100
		distance_required = 100
		for generator in POWER_GENERATORS:
			if distance(generator, self) < closest_generator:
				closest_generator = distance(generator, self)

		if SELECTED_SLOT == 0 and self.is_rock is True:
			try:
				self.prerendered_model = PowerGenerator((self.x, self.y + 1, self.z), True)
				if SETTINGS.video.legacy_models is False:
					self.prerendered_model._turbine_top.color = color.white33
			except AttributeError:
				pass
		elif SELECTED_SLOT == 1 and self.is_river is False\
				and self.is_rock is False:
			distance_required = 6
			self.prerendered_model = LandSanitizer((self.x, self.y + 1, self.z), True)
		elif SELECTED_SLOT == 2 and self.is_river is True:
			distance_required = 6
			self.prerendered_model = WaterPump(self.position + Vec3(0, 1, 0), True)
		elif SELECTED_SLOT == 3 and self.is_river is True\
				and self.desolated is False:
			distance_required = 10
			self.prerendered_model = Rockifier((self.x, self.y + 1, self.z), True)

		if self.prerendered_model is not None:
			self.prerendered_model.color = color.white33 if closest_generator <= distance_required else color.rgba(255, 0, 0, 100)

	def on_mouse_exit(self):
		if SETTINGS.video.enable_model_prerendering is False: return None
		destroy(self.prerendered_model)
		self.prerendered_model = None


	def on_click(self):
		# If a structure has already been built there, we just cancel the function
		if self.with_structure is True: return None

		def _buyout(slot:int, structure_creation:bool=True):
			global MONEY
			MONEY -= SLOTS_MONEY_WORTH[slot]
			text_popup(SLOTS_MONEY_WORTH[slot], False)
			if structure_creation:
				self.with_structure = True
				if SETTINGS.video.enable_model_prerendering and self.prerendered_model is not None:
					self.prerendered_model.visible = False


		global MONEY
		# If on rock, and enough money is available, generates a power generator
		if self.is_rock and SELECTED_SLOT == 0 and MONEY >= SLOTS_MONEY_WORTH[0]:
			_buyout(0)
			POWER_GENERATORS.append(PowerGenerator(self.world_position + (0, 1, 0), not SETTINGS.video.enable_animations))

		# If either the land sanitizer or the water pump are selected
		if self.is_rock is False and SELECTED_SLOT > 0:
			# We fetch the distance towards the closest power generator
			closest_generator = 100
			for generator in POWER_GENERATORS:
				if distance(generator, self) < closest_generator:
					closest_generator = distance(generator, self)

			# If the distance between the structure and the nearest generator is below 6, we can build it
			if closest_generator <= 6:
				# If we are not on river
				if self.is_river is False and SELECTED_SLOT == 1 and MONEY >= SLOTS_MONEY_WORTH[1]:
					_buyout(1)
					LAND_SANITIZERS.append(LandSanitizer(self.world_position + (0, 1, 0), not SETTINGS.video.enable_animations))
					try:
						thread.start_new_thread(function=self.undesolate_land, args='')
					except Exception as e:
						print('error starting thread', e)
					# Runs through all tiles, and if they are close enough to the building, they get undesolated
					for tile in TILES:
						if distance(self, tile) < 4:
							invoke(tile.undesolate_land, delay=randint(1, 8)/10)
				elif self.is_river is True and SELECTED_SLOT == 2 and MONEY >= SLOTS_MONEY_WORTH[2]:
					_buyout(2)
					WATER_PUMPS.append(WaterPump(self.world_position + (0, 2 if self.world_y == -1 else 1, 0), not SETTINGS.video.enable_animations))
					self.water_fill(force=self.world_y != -1)

			if closest_generator <= 10:
				if self.is_river is True and self.world_y == 0 and SELECTED_SLOT == 3 and\
						MONEY >= SLOTS_MONEY_WORTH[3]:
					_buyout(3)
					ROCKIFIERS.append(Rockifier(self.world_position + (0, 1, 0), not SETTINGS.video.enable_animations))
					self.rockify()
					# Turns all nearby water tiles into rocks
					for i in range(8):
						tile = TILES_LUT(self.index, i)
						if tile is not None:
							invoke(TILES[tile].rockify, delay=randint(10, 20)/100)

				if self.is_river is False and SELECTED_SLOT in (4, 5, 6, 7) and MONEY >= SLOTS_MONEY_WORTH[SELECTED_SLOT]:
					_buyout(4, False)
					global drill_used
					drill_used = True
					# Carves in line
					if SELECTED_SLOT == 4:
						self.carve(0)
					elif SELECTED_SLOT == 5:
						self.carve(2)
					elif SELECTED_SLOT == 6:
						self.carve(4)
					elif SELECTED_SLOT == 7:
						self.carve(6)
					# Also decimates eveything in a 3x3 area
					for tile in TILES:
						if distance(self, tile) < 2:
							invoke(tile.desolate_land, delay=randint(1, 8)/10)


	def undesolate_land(self, can_fill_water=False):
		if self.desolated is True:
			global MONEY
			if self.is_river is False:
				if SETTINGS.misc.hard_mode is False or self.fertilized is True:
					gain = randint(4, 8)
					MONEY += gain
					text_popup(gain)
					self.color = tile_green()
					self.desolated = False
					global CONVERTED_TILES
					CONVERTED_TILES += 1
					self.shader = lit_with_shadows_shader
					if hasattr(self, "dirt"): destroy(self.dirt)
					# Sometimes adding grass
					if SETTINGS.video.grass is True and randint(0, 2) >= 1:
						self.grass = Grass(self.position + (0, .5, 0))
				elif SETTINGS.misc.hard_mode is True and self.fertilized is False:
					gain = randint(1, 2)
					MONEY += gain
					text_popup(gain)
					self.color = fertilized_color()
					self.fertilized = True
					self.shader = lit_with_shadows_shader
					# Sometimes adding dirt
					if SETTINGS.video.grass is True and randint(0, 2) >= 1:
						self.dirt = Dirt(self.position + (0, .5, 0))
				# Making a bounce animation if animations are enabled
				if SETTINGS.video.enable_animations is True:
					self.scale_y += .2
					self.animate_scale((self.scale_x, self.scale_y - 0.2, self.scale_z), duration=.3, curve=curve.out_bounce)
			else:
				if can_fill_water is True:
					self.water_fill()

			# Removing pebble if needed
			if hasattr(self, "pebble"):
				destroy(self.pebble)


	def desolate_land(self):
		if self.is_river is False and self.is_rock is False \
				and self.desolated is False and self.with_structure is False:
			self.desolated = True
			global CONVERTED_TILES
			CONVERTED_TILES -= 1
			self.animate_color(desolated_color())
			self.shader = None
			if hasattr(self, "grass"): destroy(self.grass)


	def water_fill(self, depth=0, force=False, norecursive=False):
		"""
		Fills the river with water IF the tile is a river tile.
		"""
		if depth < 6:
			if self.is_river and (force is True or (SETTINGS.video.reduce_water_effects is False or
								  (self.y == -1 and SETTINGS.video.reduce_water_effects is True))):
				self.y = 0
				self.color = river_blue()
				if self.desolated is True:
					self.desolated = False
					global CONVERTED_TILES
					CONVERTED_TILES += 1
					global MONEY
					gain = randint(4, 8)
					MONEY += gain
					text_popup(gain)
					# Adding the filling animation if animations are enabled
					if SETTINGS.video.enable_animations is True:
						self.scale_y = .1
						self.animate_scale((self.scale_x, 1, self.scale_z), duration=.3, curve=curve.out_expo)
					# Adding the bubble if wanted
					if SETTINGS.video.water_bubbles is True:
						self.bubble = Bubble(self.position + (0, .55, 0))
						# Turning on the visibility only after the animation is finished if the animations are enabled
						if SETTINGS.video.enable_animations is True:
							self.bubble.color = color.rgba(255, 255, 255, 0)
							self.bubble.animate_color(color.rgba(255, 255, 255, 255), duration=.3)

				# Looks up all the neighbouring river tiles to water them
				if norecursive: return None
				def invoke_water_fills():
					for i in range(8):
						tile = TILES_LUT(self.index, i)
						if tile is not None:
							invoke(TILES[tile].water_fill, depth=depth+1, force=force, delay=0.1)
				try:
					thread.start_new_thread(function=invoke_water_fills, args='')
				except Exception as e:
					print('error starting thread', e)
			else:
				if norecursive is False:
					invoke(self.undesolate_land, can_fill_water=True, delay=0.1)


	def rockify(self):
		if self.is_river is True and self.y == 0:
			self.animate_color(rock_color(), duration=.2)
			self.is_river = False
			self.is_rock = True

			if hasattr(self, "bubble"):
				destroy(self.bubble)

	def carve(self, direction, depth=0):
		"""
		Turns the current tile into an empty river tile.
		If one of the neighbouring tiles is a river tile, it will fill this tile as well.
		"""
		global CONVERTED_TILES
		if self.with_structure: return False  # If there's a structure on this tile, we can't destroy it, thus we stop and return False
		if self.is_river: return None  # No change if it is already a river tile
		self.is_river = True
		self.is_rock = False
		if hasattr(self, "pebble"):
			destroy(self.pebble)
		if hasattr(self, "grass"):
			destroy(self.grass)

		# Checks neighbouring tiles for water
		is_water_neighbouring = False
		for tile in range(0, 7, 2):
			if tile is not None and TILES[tile].is_river and TILES[tile].desolated is False:
				is_water_neighbouring = True
				break

		# If there is neighbouring water, we just turn the current tile into a watery river tile
		if is_water_neighbouring:
			if self.desolated is True:
				self.desolated = False
				CONVERTED_TILES += 1
			# We turn the color to a water blue
			self.water_fill(norecursive=True, force=True)
		# Otherwise, it is just a desolated river tile
		else:
			if self.desolated is False:
				self.desolated = True
				CONVERTED_TILES -= 1
			# We lower it by one
			self.animate_position((self.x, -1, self.z), duration=.3)
			# We change its color to a desolated color
			self.animate_color(desolated_color())

		# Resetting the shader because it bugs for whatever reason
		self.shader = None
		# If the depth is not over 8 and if we could find the next tile in the right direction, we carve it as well
		if depth <= 8 and TILES_LUT(self.index, direction) is not None:
			invoke(TILES[TILES_LUT(self.index, direction)].carve, direction, depth+1, delay=.1)




class PowerGenerator(Entity):
	"""
	Generates power in an 8x8 area around it.
	"""
	def __init__(self, position, disable_animation:bool=False):
		self.disable_animation = disable_animation
		if SETTINGS.video.legacy_models:
			scale = (.5, 2, .5)
			super().__init__(
				position=position + (0, 3 if self.disable_animation is False else 0, 0),
				model="cube",
				scale=(.8, 2.5, .8) if self.disable_animation is False else scale
			)
		else:
			position = position + (0, -1, 0)
			scale = .1
			super().__init__(
				position=position + (0, 3 if self.disable_animation is False else 0, 0),
				model="assets/windturbinepole",
				scale=.12 if self.disable_animation is False else scale,
				rotation=(0, 180, 0)
			)
			self._turbine_top = Entity(parent=self, position=(0, 23.5, 0), model="assets/windturbinetop")

		if self.disable_animation is False:
			self.animate_position(position, duration=.2, curve=curve.in_sine)
			self.animate_scale(scale, duration=.25, curve=curve.out_back)
		
	def update(self):
		if self.disable_animation is False:
			if SETTINGS.video.legacy_models:
				self.rotation_y += 25 * time.dt
			else:
				self._turbine_top.rotation_z += 25 * time.dt


class LandSanitizer(Entity):
	"""
	Sanitizes a 6x6 area around it.
	"""
	def __init__(self, position, disable_animation:bool=False):
		self.disable_animation = disable_animation
		if SETTINGS.video.legacy_models:
			super().__init__(position=position, model="cube", scale=0, color=color.green)
			if self.disable_animation is False:
				self.animate_scale((.75, 1, .75), duration=.4, curve=curve.out_back)
			self._going_up = 0
		else:
			super().__init__(position=position + (0, -.15, 0), model="assets/water_can",
							 scale=0 if self.disable_animation is False else .2, color=color.azure)
			self._going_up = 2
			if self.disable_animation is False:
				self.animate_scale(.2, duration=.2, curve=curve.out_back)
		
	def update(self):
		if self.disable_animation is False:
			self._going_up += time.dt
			if self._going_up < 2:
				self.y -= .2 * time.dt
				if SETTINGS.video.legacy_models is False:
					self.rotation_z -= 45 * time.dt
			elif self._going_up < 4:
				self.y += .2 * time.dt
				if SETTINGS.video.legacy_models is False:
					self.rotation_z += 45 * time.dt
			else:
				self._going_up = 0


class WaterPump(Entity):
	"""
	Pumps water into a river.
	"""
	def __init__(self, position, disable_animation:bool=False):
		self.disable_animation = disable_animation
		if SETTINGS.video.legacy_models:
			super().__init__(position=position - (0, 0.2, 0), model="cube", scale=(.75, 1, .75))
			self.childA = Entity(position=self.position - (0.4, -.2, 0), model="cube", scale=.25,
								 color=color.red if self.disable_animation is False else color.white33)
			self.childB = Entity(position=self.position + (0.4, -.2, 0), model="cube", scale=.25,
								 color=color.red if self.disable_animation is False else color.white33)
			if self.disable_animation is False:
				self.childA.animate_color(color.blue, delay=.8, duration=.4)
				self.childB.animate_color(color.blue, delay=.8, duration=.4)
		else:
			super().__init__(position=position - (0, 0.4, 0) - (0, 5 if self.disable_animation is False else 0, 0),
							 model="assets/watertower", scale=2.6, color=color.rgb(128, 69, 11))
			if self.disable_animation is False:
				self.animate_position(self.position + (0, 5, 0), duration=.8, curve=curve.out_back)



class Rockifier(Entity):
	"""
	Rockifies all neighbouring water tiles.
	"""
	def __init__(self, position, disable_animation:bool=False):
		super().__init__(position=position, model="cube", scale=(.75, 1, .75), color=rock_color())
		if disable_animation is False:
			self.animate_y(.25, duration=.3)
