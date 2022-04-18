from ursina import *
from ursina.shaders import fxaa_shader
from game_camera import GameCamera
from tiles import Tile
import tiles
from tile_colors import desolated_color
from ui import UI
from progress_circle import ProgressCircle
import UrsinaAchievements
from perlin_numpy import generate_perlin_noise_2d
import json
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

# Creating the window
app = Ursina(fullscreen=SETTINGS.video.fullscreen, vsync=SETTINGS.video.vsync, show_ursina_splash=False)
window.title = "ProjectRebirth"
window.icon = "assets/ProjectRebirthIcon.ico"
window.exit_button.visible = False
if SETTINGS.misc.show_FPS_counter is True:
	window.fps_counter.color = color.lime
	window.fps_counter.y += 0.015
else:
	window.fps_counter.visible = False
window.exit_button.disabled = True
window.exit_button.ignore_pause = True
application.development_mode = False

# Caps the framerate if wanted
if SETTINGS.video.framerate_limiter is not None:
	from panda3d.core import ClockObject
	globalClock.setMode(ClockObject.MLimited)
	globalClock.setFrameRate(SETTINGS.video.framerate_limiter)

# If set as so, enables FXAA
if SETTINGS.video.FXAA is True:
	camera.shader = fxaa_shader

# Loads the models if wanted
if SETTINGS.video.legacy_models is False:
	def load_textures():
		for model in ("water_can", "watertower", "windturbinepole", "windturbinetop"):
			load_model("assets/" + model)
	try:
		thread.start_new_thread(function=load_textures, args='')
	except Exception as e:
		print('error starting thread', e)

# Returns the correct sky color based off how many tiles were converted
skycolor = lambda converted_tiles: color.color(max(184, 231 - converted_tiles / 10), .69, 1)

# Displays the money left on the screen
money_text = Text(position=(-.48 * window.aspect_ratio, -.14 * window.aspect_ratio))

# Displays how much progress is required
completion_circle = ProgressCircle(
	thickness=30,
	completion_percentage=.5,
	radius=.1,
	outer_color=color.lime,
	position=(-.44 * window.aspect_ratio, -.22 * window.aspect_ratio)
)

# Creates the game's achievements
time_spent = 0
def achievementfx_play_the_game(): return time_spent > 3
UrsinaAchievements.create_achievement("Play the game.", achievementfx_play_the_game, "assets/ProjectRebirthIcon.png")
def achievementfx_infinite_power(): return len(tiles.POWER_GENERATORS) != 0
UrsinaAchievements.create_achievement("Infinite power !", achievementfx_infinite_power, "assets/windturbineicon.png")
def achievementfx_bubbles(): return len(tiles.WATER_PUMPS) != 0
UrsinaAchievements.create_achievement("Bubbles.", achievementfx_bubbles, "assets/bubbles_0.png")
def achievementfx_touch_grass(): return len(tiles.LAND_SANITIZERS) != 0
UrsinaAchievements.create_achievement("Touch grass !", achievementfx_touch_grass, "assets/water_can.png")
def achievementfx_the_rock(): return len(tiles.ROCKIFIERS) != 0
UrsinaAchievements.create_achievement("The rock.", achievementfx_the_rock, "assets/rockifier.png")
def achievementfx_the_drill(): return tiles.drill_used
UrsinaAchievements.create_achievement("We don't talk about the drill.", achievementfx_the_drill)
def achievementfx_monopoly(): return tiles.MONEY < min(tiles.SLOTS_MONEY_WORTH)
UrsinaAchievements.create_achievement("Monopoly : the failure.", achievementfx_monopoly, "assets/flying_money.png")
def achievementfx_rebirth(): return endgame_started
UrsinaAchievements.create_achievement("Rebirth.", achievementfx_rebirth, "assets/ProjectRebirthIcon.png", importance=3)


def update():
	# Checks achievements
	try:
		thread.start_new_thread(function=UrsinaAchievements.achievement_updates, args='')
	except Exception as e:
		print('error starting thread', e)

	# Adds the total time spent in app
	global time_spent
	time_spent += time.dt

	# Updates sky color
	sky.color = skycolor(tiles.CONVERTED_TILES)

	# Updates wallet text
	completion = round(tiles.CONVERTED_TILES/tiles.MAX_CONVERTED_TILES*100)
	completion_circle.set_completion_percentage(completion/100)
	completion_circle.set_text(f"{completion}%")
	completion_circle.text.color = color.rgb(int(255 * (1 - completion/100)), 255, int(255 * (1 - completion/100)))
	money_text.text = f"Money : {tiles.MONEY}"

	# Fetches if the amount of current converted tiles is over or equal to the maximum amount of convertible tiles
	# and ends the game if it is
	global endgame_started
	global game_won_camera_time
	if tiles.CONVERTED_TILES >= (tiles.MAX_CONVERTED_TILES - 15) and game_won_camera_time <= 4:
		if endgame_started is False:
			# Disables the camera and remembers that the end of the game started
			game_camera.controllable = False
			endgame_started = True
			game_camera.animate_position(game_camera.start_position if distance(game_camera, (0, 0, 0)) < 16 else \
				                             (-game_camera.x, game_camera.start_position[1], -game_camera.z),
			                             duration=8, curve=curve.linear)
			ui.visible = False
			ui.disable()

			# Undesolates and fills with water any remaining undesolated tile.
			for tile in terrain:
				tile.undesolate_land()
				tile.water_fill(norecursive=True)

			# Animates the end screen
			game_endscreen.animate_color(color.rgba(0, 0, 0, 185), duration=2, delay=1, curve=curve.out_cubic)
			game_endscreen_text.animate_color(color.rgba(100, 255, 100, 255), duration=2, delay=2, curve=curve.linear)
			game_endscreen_text.animate_scale(1.5, duration=5, delay=2.5, curve=curve.out_sine)
			invoke(application.pause, delay=8)

			# Shows the exit button again
			window.exit_button.disabled = False
			window.exit_button.visible = True
			if SETTINGS.misc.show_FPS_counter is True:
				window.fps_counter.y -= 0.015
			
		game_won_camera_time += time.dt
		camera.fov += 5 * time.dt



def input(key):
	# Getting the number inputs to select the slot
	try:
		key = int(key)
		tiles.SELECTED_SLOT = key - 1
	except ValueError:
		pass
	finally:
		key = str(key)


if __name__ == '__main__':
	# Adding the camera to the scene
	game_camera = GameCamera(SETTINGS)

	# Creating the UI
	ui = None
	def create_UI():
		global ui
		ui = UI()
	try:
		thread.start_new_thread(function=create_UI, args='')
	except Exception as e:
		print('error starting thread', e)

	# Creating the endscreen
	game_won_camera_time = 0
	game_endscreen = Entity(parent=camera.ui, model="quad", color=color.rgba(0, 0, 0, 0), scale=4)
	game_endscreen_text = Text("This land has reborn.", position=(0, 0), origin=(0, 0), color=color.rgba(255, 255, 255, 0))
	endgame_started = False

	# Generating a 32x32 terrain with random variation (noise) and random colors
	noise = generate_perlin_noise_2d((SETTINGS.misc.playable_area_size, SETTINGS.misc.playable_area_size), (2, 2))
	def calculate_height(x, z):
		# Calculates the height of the tile based off the noise map and its value
		val = noise[x + SETTINGS.misc.playable_area_size // 2][z + SETTINGS.misc.playable_area_size // 2]
		return_val = 0  # Initiated at 0, standard height
		if -0.06 < val < 0.06:  # River, one below
			return_val = -1
		elif val > 0.4:  # Cliff, one above
			return_val = 1
		return return_val
	terrain = [Tile(position=(x + .5, calculate_height(x, z), z + .5),
	                color=desolated_color(), noise_val=noise[x + SETTINGS.misc.playable_area_size // 2][z + SETTINGS.misc.playable_area_size // 2]) \
	           for x in range(-SETTINGS.misc.playable_area_size // 2, SETTINGS.misc.playable_area_size // 2) \
	           for z in range(-SETTINGS.misc.playable_area_size // 2, SETTINGS.misc.playable_area_size // 2)]
	for i in range(len(terrain)):
		terrain[i].index = i
	tiles.TILES = terrain

	# Creating the sky
	sky = Sky(color=skycolor(0), scale=999)

	# Running the app
	app.run()
