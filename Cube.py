# Cube class
#
# has: (x,y,z) coordinates
# can: translate
#
# last modified: 9/2/2014 by Cynthia Sung

class Cube:
    """Cube class"""
    
    def __init__(self, pos):
        if isinstance(pos, Cube):
            self.pos = pos.pos
        else:
            self.pos = pos
        self.dim = len(self.pos)
        self.dir = (0,0,-1)
        
    def translate(self, toadd):
        self.pos = self.add(self.pos, toadd)
        
    def add(self, first, other = None):
        if other != None:
            if isinstance(other, Cube):
                return self.add(other.pos)
            elif isinstance(other, tuple):
                if len(other) < self.dim:
                    # pad other with zeros to be the same number of dimensions
                    other = tuple( other[i] if len(other)>i else 0 for i in range(self.dim) )
                return tuple( a_i+b_i for (a_i,b_i) in zip(first, other) )
            elif isinstance(other, int):
                return tuple( a_i+other for a_i in first )
        else:
            return Cube( self.add( self.pos, first ) )

    def __getitem__(self, idx):
        return self.pos[idx]

    def __add__(self, other):
        return self.add(other)

    def __radd__(self, other):
        return self.add(other)

    def __mul__(self, other):
        if isinstance(other, int):
            return Cube( tuple( a_i*other for a_i in self.pos ) )
        return other
    
    def __rmul__(self, other):
        if isinstance(other, int):
            return Cube( tuple( a_i*other for a_i in self.pos ) )
        return other

    def __eq__(self, other):
        return isinstance(other, Cube) and self.pos == other.pos

    def __ne__(self, other):
        return not isinstance(other, Cube) or not self.pos == other.pos

    def __str__(self):
        return "Cube[" + str(self.pos) + "]"
        
    def __hash__(self):
        return hash(self.pos)
