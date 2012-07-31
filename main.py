#!/usr/bin/env python
"""
Chromio game

"""
import random
from functools import partial
from collections import deque

import kivy
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Canvas
from kivy.factory import Factory

import hexagons
import hexgrid

COLOURS = [(1, 0, 0, 1), (0.9, 0.8, 0, 1),
           (0.7, 1, 0, 1), (0.9, 0, 1, 1),
           (0, 0.6, 0.7, 1), (0.9, 0.9, 0.9, 1)]

GRIDRADIUS = 10

class ColourButton(Button):
    icon_source = StringProperty()
    def __init__(self, index, **kw):
        self.index = index
        src = "images/button{0}.png".format(index)
        Button.__init__(self, icon_source=src, background_color=COLOURS[index], **kw)

class ChromioGrid(object):
    def __init__(self, layout, gridradius=GRIDRADIUS):
        self.layout = layout # should be a FloatLayout
        self.grid = hexgrid.HexagonGrid(gridradius)
        self.images = hexgrid.HexagonGrid(gridradius)
        self.randomise()
        self.filling = False
        self.steps = 0
        self.filled = False

    def randomise(self):
        """ randomise the contents of the grid """
        cx, cy = self.layout.width / 2.0, self.layout.height / 2.0
        scale = cx / self.grid.maxradius
        maxcolour = len(COLOURS) - 1
        for i in range(len(self.grid)):
            c = self.grid[i] = random.randint(0, maxcolour)
            src = "images/button{0}.png".format(c)
            w = self.images[i]
            if w is None:
                w = Image(size_hint=(scale,scale))
                self.layout.add_widget(w)
                self.images[i] = w
            wx, wy = hexagons.Spiral(i).centre()
            w.pos_hint = {"x":(wx - 0.5) * scale + cx,
                          "y":(wy - 0.5) * scale + cy}
            w.source = src
        self.steps = 0
        self.filled = False

    def start_fill(self, butn):
        """ flood fill the grid with a specified index """
        if self.filling or self.filled:
            return
        index = butn.index
        current = self.grid[0]
        if current == index:
            return
        self.filling = True
        self.steps += 1
        agenda = deque([0]) # start at the centre
        seen = set()
        while agenda:
            this = agenda.popleft()
            if this in seen:
                continue
            nbrs = hexagons.Spiral(this).hexpolar().neighbours()
            seen.add(this)
            for n in nbrs:
                try:
                    if self.grid[n] == current:
                        agenda.append(n.spiral().index)
                except IndexError:
                    pass # off the edge
        src = "images/button{0}.png".format(index)
        for i in seen:
            self.grid[i] = index
            self.images[i].source = src
        self.filling = False
        self.filled = len(set(self.grid.contents)) == 1

class ChromioApp(App):
    def build(self):
        self.content = root = BoxLayout(
            orientation="horizontal", padding=20, spacing=20)
        hexpane = FloatLayout(size_hint=(0.6, 1))
        grid = ChromioGrid(hexpane)
        buttons = GridLayout(cols=2, size_hint=(0.4,1))
        root.add_widget(hexpane)
        root.add_widget(buttons)
        for i in range(6):
            b = ColourButton(i, text="{0}".format(i))
            buttons.add_widget(b)
            b.bind(on_press=grid.start_fill)
        return root

if __name__ in ('__android__', '__main__'):
    ChromioApp().run()
