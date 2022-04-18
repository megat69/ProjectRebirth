# ProjectRebirth
My take at a recreation of the Steam Demo of Terra Nil by Free Lives, using the Ursina engine in Python.

## Download
Either clone this repository or download the latest release. Beware, the release version is a build for the Windows operating system, it is not designed for Linux nor Mac, those operating systems require the source version.

After that, install the Ursina engine Python library. I recommend using pip : `pip install ursina`

## Running
Simply run `main.py` (`python main.py` after selecting the right directory)

## Gameplay
You start on a desolated piece of land, and this is your task to fill it with life again.

You can move the camera around by holding the middle mouse button or the WASD keys by default, and zoom in/out using the scroll wheel.

Each building type is accessible in the hotbar at the bottom of the screen, and has a cost in money, money that you can track at the bottom left of the screen. You earn money by sanitizing the land.

You can track the progression of the rebirth of the island at the bottom left corner of the screen, symbolized by a percentage.

Each map is procedurally generated at the start of each game.

**Building system :**

Every building has its purpose and cannot be placed everywhere.
- The ***Power Generator***, as its name indicates, generates power for all the other buildings to function. It is the cheapest building, at 50 Money. It can only be placed on rocks.
- The ***Land Sanitizer*** will sanitize the land around it, making you earn money. In hard mode, you'll have to use two of those to actually sanitize a piece of land. It costs 75 Money.
- The ***Water Pump*** will raise the water level in rivers and sanitizes the land around the water for only 75 Money. It can only be placed in rivers.
- The ***Rockifier*** will turn all the neighbouring water tiles into rocks, so that you can place a *Power Generator* next to it. It requries less energy, so you can place it further away from a *Power Generator* than the other buildings. It must be placed on a water tile to function. It costs 100 Money.
- The ***Drill*** is a last resort building. It will carve a river in the direction you specified (left, right, top, or bottom) for 150 Money. If you ever find yourself in a situation where a piece of land is isolated without any rocks or rivers, you might need it in order to win the game.

## Settings
All the settings are stored in a JSON file, following a JSON format : `settings.json`.

The settings and their possible values are listed here :
- **Video** : The "performance" section
	- `fullscreen` (bool) : Whether the game should be launched in fullscreen mode. `True` by default.
	- `vsync` (bool) : Whether to enable Vsync or not. `False` by default.
	- `fov` (int) : The default FOV. The higher it is, the laggier it gets. Default : 60.
	- `framerate_limiter` (int/null) : Whether to cap the framerate and if so, to how much. If set to `null`, no framerate cap will be made. If set to an integer, the framerate will be capped to that number. `null` by default.
	- `reduce_water_effects` (bool) : Don't change that once. Unless you've got yourself a Threadripper at 5.2 GHz. Performance impact : extreme. `True` by default.
	- `FXAA` (bool) : Whether to enable or not the FXAA fast antialiasing. Performance impact : low. `False` by default.
	- `legacy_models` (bool) : Enable the use of older models, based on cubes. Good idea if you're REALLY running a potato PC. Performance impact : low/mid. `False` by default.
	- `water_bubbles` (bool) : Bubbly water :D ! Enable fancy-looking water. Performance impact : low. `True` by default.
	- `grass` (bool) : Enable fancy-looking grass ! Performance impact : mid. `True` by default.
	- `pebbles` (bool) : Enable fancy-looking pebbles over rocks or desolated land ! Performance impact : mid. `True` by default.
	- `enable_model_prerendering` (bool) : Lets the game tell you which building type is selected and whether you can place it. I don't see the point of changing it, but one more setting is cool, isn't it ? Performance impact : None. `True` by default.
	- `enable_animations` (bool) : Whether to enable animations in-game. Performance impact : low/mid. `True` by default.
- **Controls** :
	- `sensitivity` (list\[int]) : The vertical and horizontal sensitivity of your mouse. `[90, 90]` by default.
- **Bindings** : The keybinds you want to use.
	- `forward` (str) : The key to move forward. `w` by default.
	- `backward` (str) : The key to move backward. `s` by default.
	- `left` (str) : The key to move left. `a` by default.
	- `right` (str) : The key to move right. `d` by default.
- **Misc** : Other settings
	- `show_FPS_counter` (bool) : Whether to show the FPS counter at the top-right corner of the screen. So you can see how much I need to optimize this.
	- `playable_area_size` (int) : The size of the map. **MUST** be a multiple of 2. Performance impact : high. Default : `32`.
	- `hard_mode` (bool) : Whether to enable hard mode. `True` by default.

