from ursina import *
from random import randint


def text_popup(nbr: int, plus: bool = True) -> None:
	"""
	Creates a little text popup for the money counter at the bottom left of the screen,
	to keep track of what was gained or lost.
	:param nbr: An integer number.
	:param plus: Wether a plus should be displayed or a minus
	"""
	# Creates the actual textbox at the bottom left of the screen
	text = Text(("+" if plus else "-") + str(nbr), position=(-.48 * window.aspect_ratio + randint(-7, 7)/100,
	                                                         -.14 * window.aspect_ratio))
	# We animate the text's vertical position for a few instants
	text.animate_position((text.x, (-.14 + randint(0, 5)/100) * window.aspect_ratio), duration=.7, curve=curve.linear)
	# We animate the text's color to become transparent
	text.animate_color(color.rgb(255, 255, 255, 0), duration=.7, curve=curve.linear)

	# We destroy it after a second
	destroy(text, delay=1)