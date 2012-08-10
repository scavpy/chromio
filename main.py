#!/usr/bin/env python
"""
Chromio game

"""
import random
from functools import partial
from collections import deque
import shelve

import kivy
kivy.require('1.3.0')

from kivy.app import App
from kivy.properties import (ObjectProperty, StringProperty, NumericProperty, BooleanProperty)
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.label import Label
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

try:
    STATS = shelve.open("stats.shelve", "c")
except OSError:
    STATS = {} # can't save stats

class ColourButton(Button):
    index = NumericProperty()
    def __init__(self, **kw):
        Button.__init__(self, **kw)
        self.background_color=COLOURS[self.index]

class IconImage(Image):
    prefix = "button"
    index = NumericProperty()


class ChromioGrid(FloatLayout):
    filled = BooleanProperty()
    steps = NumericProperty()

    def __init__(self, gridradius=GRIDRADIUS, **kw):
        FloatLayout.__init__(self, **kw)
        self.gridradius = gridradius
        self.grid = hexgrid.HexagonGrid(gridradius)
        self.images = hexgrid.HexagonGrid(gridradius)
        self.randomise()
        self.filling = False
        self.filled = False

    def randomise(self):
        """ randomise the contents of the grid """
        scale = 0.5 / self.grid.maxradius
        maxcolour = len(COLOURS) - 1
        for i in range(len(self.grid)):
            c = self.grid[i] = random.randint(0, maxcolour)
            w = self.images[i]
            if w is None:
                w = IconImage(index=c, size_hint=(scale, scale))
                self.add_widget(w)
                self.images[i] = w
                wx, wy = hexagons.Spiral(i).centre()
                w.pos_hint = {"x":(wx - 0.5) * scale + 0.5,
                              "y":(wy - 0.5) * scale + 0.5}
            else:
                w.index = c
        self.filled = False
        self.steps = 0

    def resize(self, gridradius):
        """ resize the grid if necessary """
        if self.grid.maxradius != gridradius:
            self.grid = hexgrid.HexagonGrid(gridradius)
            for i in range(len(self.images)):
                w = self.images[i]
                if w is not None:
                    self.remove_widget(w)
            self.images = hexgrid.HexagonGrid(gridradius)
        self.randomise()
        self.gridradius = gridradius

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
        Factory.register("IconImage", cls=IconImage)
        self.content = root = BoxLayout(
            orientation="horizontal", padding=20, spacing=20)
        grid = ChromioGrid(GRIDRADIUS, size_hint=(0.6, 1))
        buttons = GridLayout(cols=2, size_hint=(0.4,1))
        root.add_widget(grid)
        root.add_widget(buttons)
        for i in range(6):
            b = ColourButton(index=i, text="{0}".format(i))
            buttons.add_widget(b)
            b.bind(on_press=grid.start_fill)
        rb = Button(text="Restart", font_size=20)
        buttons.add_widget(rb)
        sizer = Slider(min=4, max=16, value=GRIDRADIUS)
        buttons.add_widget(sizer)
        rb.bind(on_press=lambda x: grid.resize(int(round(sizer.value, 0))))
        grid.bind(filled=self.game_end_check, steps=self.steps_update)
        self.steplabel = Label(text="0", 
                               pos_hint={"x":-0.45, "y":0.45},
                               font_size=20)
        grid.add_widget(self.steplabel)
        return root

    def game_end_check(self, grid, filled):
        if filled:
            print "Filled in {0} steps!".format(grid.steps)
            key = "best{0}".format(grid.gridradius)
            best = STATS.get(key)
            if best is None or grid.steps < best:
                try:
                    STATS[key] = grid.steps
                except OSError:
                    pass # oh well, ignore
                self.steplabel.color = [0.5, 1.0, 0.5, 1.0]

    def steps_update(self, grid, steps):
        label = self.steplabel
        label.text = str(steps)
        key = "best{0}".format(grid.gridradius)
        best = STATS.get(key)
        if best is not None:
            if steps > best:
                label.color = [1.0, 0.5, 0.5, 1.0]
            else:
                label.color = [1.0, 1.0, 1.0, 1.0]

if __name__ in ('__android__', '__main__'):
    ChromioApp().run()
