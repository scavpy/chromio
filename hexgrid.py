"""

  An array-like object indexable by spiral or hex polar coordinates

"""

from hexagons import HexPolar, HexSkew, Spiral

class HexagonGrid(object):

    def __init__(self, maxradius):
        self.maxradius = maxradius
        length = HexPolar(maxradius+1, 0, 0).spiral().index
        self.contents = [None] * length
        
    def __len__(self):
        return len(self.contents)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.contents[index]
        else:
            return self.contents[index.spiral().index]

    def __setitem__(self, index, value):
        if isinstance(index, int):
            self.contents[index] = value
        else:
            self.contents[index.spiral().index] = value

    def fill(self, value):
        self.contents[:] = [value] * len(self.contents)


    def subgrid(self, at, radius=1, defval=None):
        """ extract a subgrid of cells centred on specified position """
        ret = HexagonGrid(radius)
        if isinstance(at, int):
            at = Spiral(at)
        shs = at.hexskew() # src centre position as vector
        for i in range(len(ret)):
            rel = Spiral(i).hexskew() # relative dest position as vector
            src = HexSkew(shs.u + rel.u, shs.v + rel.v) #abs src pos as vector
            index = src.spiral().index
            if index >= len(self):
                ret[i] = defval
            else:
                ret[i] = self[index]
        return ret
