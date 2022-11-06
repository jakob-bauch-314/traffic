
import pygame
import math
import random

class edge():
    def __init__(self, content):
        self.content = content

class node():
    def __init__(self, edges, content):
        self.edges = edges
        self.content = content

class tree():
    def __init__(self, nodes):
        self.nodes = nodes


class vehicle():
    def __init__(self, position, length, start, path):
        self.positon = position
        self.length = length
        self.start = start
        self.path = path

    def draw(self):
        pass

    def update(self):
        pass

class street():

    def __init__(self, startx, starty, endx, endy):
        self.startx = startx
        self.starty = starty
        self.endx = endx
        self.endy = endy
        self.length = math.sqrt(math.pow(endx - startx, 2) + math.pow(endy - starty, 2))

    def draw(self):
        pass

class crossing():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        pass

