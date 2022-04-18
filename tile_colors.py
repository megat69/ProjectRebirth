"""
Contains the random colors for each tile type.
"""
from ursina import *
from random import randint

desolated_color = lambda: color.color(36, .14, randint(90, 100) / 100)
river_blue = lambda: color.color(185, .89, randint(91, 100)/100)
tile_green = lambda: color.color(133, 1, randint(35, 50) / 100)
rock_color = lambda: color.color(0, 0, randint(41, 59)/100)
fertilized_color = lambda: color.color(46, 1, randint(33, 59)/100)
