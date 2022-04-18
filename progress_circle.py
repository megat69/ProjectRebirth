from ursina import *


class Circle(Mesh):
	def __init__(self, resolution=100, radius=1, completion_percentage=1.0, mode='line', **kwargs):
		origin = Entity()
		point = Entity(parent=origin)
		point.y = radius

		self.vertices = []
		for i in range(resolution):
			if i > resolution * completion_percentage: break
			origin.rotation_z -= 360 / resolution
			self.vertices.append(point.world_position)

		destroy(origin)
		super().__init__(vertices=self.vertices, mode=mode, **kwargs)


class ProgressCircle(Entity):
	def __init__(self, position, *args, outer_color=color.lime, inner_color=color.dark_gray, thickness=30,
	             completion_percentage=1.0, radius=.1, text="", **kwargs):
		super().__init__(
			parent=camera.ui,
			position=position,
			*args,
			**kwargs
		)
		self.inner_color = inner_color
		self.outer_color = outer_color
		self.thickness = thickness
		self.radius = radius
		self.completion_percentage = completion_percentage
		self.silent_inner_circle = Entity(
			parent=self,
			model=Circle(
				thickness=thickness,
				completion_percentage=1.0,
				radius=radius,
				mode="ngon"
			),
			color=inner_color
		)
		self.outer_circle = Entity(
			parent=self,
			model=Circle(
				thickness=thickness,
				completion_percentage=completion_percentage,
				radius=radius,
				mode="ngon"
			),
			color=outer_color
		)
		self.inner_circle = Entity(
			parent=self,
			model=Circle(
				thickness=thickness,
				completion_percentage=1.0,
				radius=radius - .03,
				mode="ngon"
			),
			color=inner_color
		)
		self.text = Text(parent=self, text=text, origin=(0, 0), scale=1.5)

	def set_completion_percentage(self, completion_percentage=1.0):
		if completion_percentage < 0.02:
			self.outer_circle.visible = False
		else:
			self.outer_circle.visible = True
			self.outer_circle.model = Circle(
				thickness=self.thickness,
				completion_percentage=completion_percentage,
				radius=self.radius,
				mode="ngon"
			)

	def set_text(self, text):
		self.text.text = text


if __name__ == '__main__':
	app = Ursina()
	e = ProgressCircle(position=(0, 0), thickness=20, completion_percentage=0.02, radius=.1, color=color.lime)
	app.run()