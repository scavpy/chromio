# -*- encoding:utf-8 -*-
"""
  Hexagon Coords

 Provides conversion between different kinds of coordinates on a grid of hexagons.
 
 Hex Polar (ring, sector, number)
 ====================================
 The origin cell has coordinates (0,0,0) and is the sole cell in ring 0
 Ring R >= 1 has 6 sectors (0..5), each with R cells numbered 0..(R-1) anticlockwise
 from the corner along a side of the hexagonal ring of cells.
 
   Figure 1: Hexagonal Grid of Cells
 
         K J I
        L C B H
       M D @ A G
        N E F R
         O P Q
 
  In Figure 1, Ring 1 consists of cells A..F, with coords (1,0,0), (1,1,0) .. (1,5,0).
 
 
 Spiral (ordinal number)
 =======================
 A conversion from HexPolar coords to the ordinal number of the cells enumerated in a spiral
 from the origin cell (0) anticlockwise.  This can be used as an index into a linear array of cells.
 
  k = [ 3r(r - 1) + 1 ] + rs + n
 
 Hex Skew (u, v)
 ===============
 Coordinates expressed as integer multiples of vectors U = (1, 0) and V = (0.5, sin(60°))
"""

from math import sin, cos, pi
SIN60 = sin(pi / 3.0)

class HexPolar(object):
    __slots__ = ('ring', 'sector', 'number')
    def __init__(self, ring, sector, number):
        if ring < 0:
            raise ValueError("ring must be >= 0")
        if ring == 0 and (sector != 0):
            raise ValueError("if ring is 0, sector must be 0 also")
        if not (0 <= sector <= 5):
            raise ValueError("sector must be in range(6)")
        if number > 0 and number >= ring:
            raise ValueError("number must be less than ring")
        self.ring = ring
        self.sector = sector
        self.number = number

    def hexpolar(self):
        return self

    def spiral(self):
        ring = self.ring
        if ring:
            return Spiral(ring * (3 * (ring - 1) + self.sector) + self.number + 1)
        else:
            return Spiral(0)

    def hexskew(self):
        r = self.ring
        n = self.number
        s = self.sector
        if s == 0:
            return HexSkew(r - n, n)
        elif s == 1:
            return HexSkew(-n, r)
        elif s == 2:
            return HexSkew(-r, r - n)
        elif s == 3:
            return HexSkew(n - r, -n)
        elif s == 4:
            return HexSkew(n, -r)
        elif s == 5:
            return HexSkew(r, n - r)
        
    def neighbours(self):
        ring, sector, number = self.ring, self.sector, self.number
        if ring == 0:
            return [HexPolar(1, s, 0) for s in range(6)]
        elif number == 0: # at a corner, ring >= 1
            ring1 = (ring == 1) # a few special cases
            return [
                HexPolar(ring - 1, 0 if ring1 else sector,  0), # same corner, one ring in
                HexPolar(ring + 1, sector, 0), # same corner one ring out
                HexPolar(ring, (sector + 1) % 6 if ring1 else sector, 0 if ring1 else 1), # anticlockwise
                HexPolar(ring, (sector + 5) % 6, ring - 1), # clockwise
                HexPolar(ring + 1, sector, 1), # anticlockwise and out
                HexPolar(ring + 1, (sector + 5) % 6, ring), # clockwise and out
                ]
        else: # on a side, ring > 1, number > 1
            end = (number + 1 == ring)
            splus = (sector + 1) % 6 if end else sector
            return [
                HexPolar(ring, sector, number - 1), # clockwise
                HexPolar(ring, splus, (number + 1) % ring), # anticlockwise
                HexPolar(ring - 1, sector, number - 1), # clockwise and in
                HexPolar(ring - 1, splus, 0 if end else number), # one ring in
                HexPolar(ring + 1, sector, number), # one ring out
                HexPolar(ring + 1, sector, number + 1), # anticlockwise and out
                ]

    def centre(self):
        return self.hexskew().centre()

    @staticmethod
    def near(x, y):
        return HexSkew.near(x, y).hexpolar()


class Spiral(object):
    __slots__ = ('index',)
    
    def __init__(self, index):
        self.index = index

    def spiral(self):
        return self

    def hexpolar(self):
        r = 0
        i = self.index
        while 3 * r * (r + 1) + 1 <= i:
            r += 1
        if r:
            pos = i - (3 * r * (r - 1) + 1)
            return HexPolar(r, pos // r, pos % r)
        else:
            return HexPolar(0,0,0)

    def hexskew(self):
        return self.hexpolar().hexskew()

    def centre(self):
        return self.hexskew().centre()

    @staticmethod
    def near(x, y):
        return HexSkew.near(x, y).spiral()


class HexSkew(object):
    __slots__ = ('u', 'v')

    def __init__(self, u, v):
        self.u, self.v = u, v

    def spiral(self):
        return self.hexpolar().spiral()

    def hexskew(self):
        return self

    def hexpolar(self):
        u, v = self.u, self.v
        if u == 0:
            if v == 0:
                return HexPolar(0,0,0)
            elif v > 0:
                return HexPolar(v, 1, 0)
            else:
                return HexPolar(-v, 4, 0)
        elif u > 0:
            if v == 0:
                return HexPolar(u, 0, 0)
            elif v > 0:
                return HexPolar(u + v, 0, v)
            elif u >= abs(v):
                return HexPolar(u, 5, u + v)
            else:
                return HexPolar(-v, 4, u)
        else:
            if v == 0:
                return HexPolar(abs(u), 3, 0)
            elif v < 0:
                return HexPolar(-(u+v), 3, -v)
            elif v > abs(u):
                return HexPolar(v, 1, -u)
            else:
                return HexPolar(-u, 2, -u - v)

    def centre(self):
        v = self.v
        return self.u + v*0.5, v * SIN60

    @staticmethod
    def near(x, y):
        v = round(y / SIN60)
        u = round(x - 0.5*v)
        return HexSkew(u, v)
