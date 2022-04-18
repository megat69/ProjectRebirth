from ursina import *


class GameCamera(Entity):
	"""
	Camera used in the game.
	"""
	def __init__(self, settings):
		camera.editor_position = camera.position
		super().__init__(name='game_camera', eternal=True)
		self.settings = settings

		self.rotation_speed = 200
		self.pan_speed = Vec2(5, 5)
		self.move_speed = 10
		self.zoom_speed = 1.25
		self.zoom_smoothing = 8
		self.rotate_around_mouse_hit = False
		self.controllable = True

		self.start_position = self.position
		self.perspective_fov = camera.fov
		self.orthographic_fov = camera.fov
		self.on_destroy = self.on_disable

		self.light = PointLight(position=camera.world_position)


	def on_enable(self):
		camera.org_parent = camera.parent
		camera.org_position = camera.position
		camera.org_rotation = camera.rotation
		camera.parent = self
		camera.position = camera.editor_position
		camera.rotation = (0, 0, 0)
		self.rotation = (45, -23, 0)
		self.target_z = camera.z

	def on_disable(self):
		camera.editor_position = camera.position
		camera.parent = camera.org_parent
		camera.position = camera.org_position
		camera.rotation = camera.org_rotation

	def update(self):
		if self.controllable is False: return None

		# Making the camera move at every keypress if middle mouse is not held, else moving from middle mouse
		if not mouse.middle:
			direction = Vec3(
				Vec3(0, 0, 1) * (
						held_keys[self.settings.bindings.forward] - held_keys[self.settings.bindings.backward]
				) + Vec3(1, 0, 0) * (
						held_keys[self.settings.bindings.right] - held_keys[self.settings.bindings.left]
				)
			).normalized() * time.dt * 4
		else:
			direction = Vec3(
				Vec3(0, 0, -1) * (
						mouse.velocity[1] * self.settings.controls.sensitivity[1]
				) + Vec3(-1, 0, 0) * (
						mouse.velocity[0] * self.settings.controls.sensitivity[0]
				)
			).normalized() * time.dt * 24

		# Adjusting the position based on the mouse movement
		self.position += direction

		# Adjusting the light position
		self.light.position = camera.world_position

	def input(self, key):
		# Increasing/decreasing the fov based off the scroll wheel, and clamping the value so it does not feel weird
		if key == "scroll up" and self.controllable:
			camera.fov = max(40, camera.fov - 2)
		if key == "scroll down" and self.controllable:
			camera.fov = min(80, camera.fov + 2)
