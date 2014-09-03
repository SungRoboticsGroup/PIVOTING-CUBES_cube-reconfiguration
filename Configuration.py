# Config class
#
# has: Cubes
# can: rotate cubes
#
# originally: 7/15/2014 by James Bern
# last modified: 9/2/2014 by Cynthia Sung

from Cube import Cube
from ConfigDraw2D import ConfigDraw2D
from vector_op import *

import sys
import time

# loading configs
import pickle
from pprint import pprint

class Configuration:
    """Configuration class"""

    # INITIALIZATION
    def __init__(self, cubes, ispar = False, dodraw = False, dosave = False):
        self.ispar = ispar

        # the cubes
        self.cubes = set()

        # boundary
        self.O_set = []
        self.extreme = None  # UR extreme
        # mobile cubes
        self.M_set = []
        # nonsplitting cubes
        self.N_set = []
        # tail cubes
        self.T_set = []

        self.rotating_cubes = []

        # for drawing
        self.dodraw = dodraw
        self.drawing = None
        self.dump_png = dosave

        # initialize the configuration
        if cubes != None:
            self.init_configuration(cubes, False)
        else:
            self.init_configuration(None, False)
    
    def init_configuration(self, init_config=None, random=False):
        if isinstance(init_config, str):
            # load config from file
            try:
                g = open(init_config, 'r')
                input_config = pickle.load(g)
                self.init_configuration(input_config, False)
            except IOError:
                print "config file not found"
                return
        elif isinstance(init_config, list) or isinstance(init_config, set):
            # creates cubes from a set
            MX = min([tup[0] for tup in init_config])
            MY = max([tup[1] for tup in init_config])
            for temp in init_config:
                break
            self.dim = len(temp)
            
            if self.dim > 2:
                MZ = min([tup[2] for tup in init_config])
                self.config = set(Cube((tup[0]-MX,MY-tup[1],tup[2]-MZ)) for tup in init_config)
            else:
                self.config = set(Cube((tup[0]-MX,MY-tup[1])) for tup in init_config)
        elif random:
            # random configuration
            pass
        else:
            # default configuration
            config = set([(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (1, 0), (1, 3), (1, 6), (1, 9), (1, 12), (2, 0), (2, 3), (2, 6), (2, 9), (2, 12), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12), (4, 0), (4, 3), (4, 6), (4, 9), (4, 12), (5, 0), (5, 3), (5, 6), (5, 9), (5, 12), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (6, 11), (6, 12), (7, 0), (7, 3), (7, 6), (7, 9), (7, 12), (8, 0), (8, 3), (8, 6), (8, 9), (8, 12), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9), (9, 10), (9, 11), (9, 12), (10, 0), (10, 3), (10, 6), (10, 9), (10, 12), (11, 0), (11, 3), (11, 6), (11, 9), (11, 12), (12, 0), (12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10), (12, 11), (12, 12)])
            self.init_configuration(config, False)
            
        # Always need to run these
        self.config_size = len(self.config)
        self.extreme = self.find_extreme()

    # RECONFIGURATION ALGORITHM
    def reconfig(self):
        if self.dodraw:
            self.init_draw()
        if not self.verify_configuration():
            print("Configuration is invalid!")
            if self.dodraw:
                self.drawing.draw_configuration(self.config)
                while not self.drawing.check_draw_close():
                    pass
        else:
            print("Configuration valid!")

            self.classify_configuration()
            if self.dodraw:
                self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes)
                self.drawing.wait(1000)
                
            frame_i = 0
            while True:
                # FORNOW: frame_i only used by dump_png
                frame_i += 1
                if self.dodraw:
                    # key handling
                    if self.drawing.check_draw_close():
                        break
                if not self.relocate_next_to_tail():
                    break
                # update_configuration is actually what hangs the program
                # but we can't draw until we finish it.
                self.classify_configuration()

                if self.dodraw:
                    self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes)
                if self.dump_png:
                    pad = '0'*(4-len(str(frame_i)))
                    self.drawing.save('frame' + pad + str(frame_i) + '.png')
            
        if self.dodraw:
            self.close_draw()

    def relocate_next_to_tail(self):
        self.step_configuration()
        while self.rotating_cubes:
            if self.dodraw:
                if self.drawing.check_draw_close():
                    return False
                self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes)
            self.step_configuration()
        return True

    def step_configuration(self):
        if not self.rotating_cubes:
            # Grab next cube_n
            # Pythonic for "if len(N_set) != 0"
            if self.N_set:
                self.rotating_cubes = [self.N_set.pop()]
                # unnecessary, but clarifies intent
                self.N_set.append(self.rotating_cubes[0])
            # Search for P for a 3 Cube Escape
            else:
                # axes
                P_found = False
                P_major = None # the three cubes lie along this axis
                P_minor = None # connects filled cubes to empty outer free space
                for cube_m in self.M_set:
                    x, y = cube_m
                    U = (0,1); D = (0,-1); R = (1,0); L = (-1,0)
                    LR = (L,R); UD = (U,D);
                    search_dict = {U:LR, D:LR, R:UD, L:UD}
                    for (major, minors) in search_dict.iteritems():
                        for minor in minors:
                            broken = False
                            for i in xrange(3):
                                full = (x + i*major[0], y + i*major[1])
                                empty = (full[0] + minor[0], full[1] + minor[1])
                                if full not in config or empty in config:
                                    broken = True
                            if not broken:
                                P_found = True
                                (P_major, P_minor) = (major, minor)
                                self.rotating_cubes = [cube_m,
                                        (cube_m[0] + major[0], cube_m[1] + major[1]),
                                        (cube_m[0] + 2*major[0], cube_m[1] + 2*major[1])]
                                return
                # No more moves exist
                if not P_found:
                    for cube in self.config:
                        # horizontal line condition
                        if cube[1] != self.extreme[1]:
                            print "\nAlgorithm failed.\n"
                            pprint(config)
                            exit(1)
                    print "\nI think we are done.\n"
                    exit(0)

        else:
            # Standard tail relocation
            if len(self.rotating_cubes) == 1:
                cube_tr = self.rotating_cubes[0]
                # If not part of tail...
                if not (cube_tr[1] == self.extreme[1] and cube_tr[0] > self.extreme[0]):
                    self.config.remove(cube_tr)
                    newpos = self.rotate(cube_tr, cube_tr.dir)
                    cube_tr.translate(sub_t(newpos,cube_tr.pos))
                    # note: must remove and add cube to config because of hashing
                    self.config.add(cube_tr)
                    
                    # FORNOW: so the two overall operations (tr/3ce) are paralell
                    self.rotating_cubes = [cube_tr]
                else:
                    self.T_set.append(cube_tr)
                    self.rotating_cubes = []
            # 3 Cube Escape
            else:
                assert len(self.rotating_cubes) == 3
                moved_cube = False
                for i in range(3):
                    cube_3ce = self.rotating_cubes[i]
                    if cube_3ce[1] == self.extreme[1] and cube_3ce[0] > self.extreme[0]:
                        # sloppy
                        self.T_set.append(cube_3ce)
                        continue
                    else:
                        moved_cube = True
                        self.config.remove(cube_3ce)
                        newpos = rotate(cube_3ce, cube_3ce.dir)
                        cube_3ce.translate(sub_t(newpos, cube_3ce.pos))
                        # note: must remove and add cube to config because of hashing
                        self.config.add(cube_3ce)
                        # update rotating_cubes
                        self.rotating_cubes[i] = cube_3ce
                        break
                # If all three cubes part of tail...
                if not moved_cube:
                    self.rotating_cubes = []
    
    # CHECK RULES FOR CONFIGURATIONS
    def verify_configuration(self):
        # connectivity condition
        for c1 in self.config: break
        comp_c1 = self.find_component(c1)
        for c2 in self.config:
            assert c2 in comp_c1

        # check rules
        RULES = self.get_rules()
        
        for c0 in self.config:
            x = c0[0]
            y = c0[1]
            U = (0,1); D = (0,-1); R = (1,0); L = (-1,0);
            LR = (L,R); UD = (U,D);
            search_dict = {U:LR, D:LR, R:UD, L:UD}
            for (major, minors) in search_dict.iteritems():
                for minor in minors:
                    (M, m) = (major, minor)
                    # # derived cubes
                    # c5 c4 c3
                    # c0 c1 c2
                    c1 = add_t((x,y),M)
                    c2 = (x+2*M[0],y+2*M[1])
                    c3 = (x+2*M[0]+m[0],y+2*M[1]+m[1])
                    c4 = (x+M[0]+m[0],y+M[1]+m[1])
                    c5 = (x+m[0],y+m[1])
                    # (1)
                    assert not (c1 not in self.config and c2 in self.config)
                    # (2)
                    assert (not (c1 not in self.config and c4 in self.config and
                        c5 not in config))
                    # (3)
                    assert (not (c1 not in self.config and c2 not in self.config
                        and c3 in self.config and c4 not in self.config and
                        c5 not in self.config))
        return True

    def get_rules(self):
        if self.ispar:
            RULES = [((0,0,True),(1,0,False),(2,0,True)),
                     ((0,0,True),(1,0,False),(0,1,False),(1,1,True)),
                     ((0,0,True),(1,0,False),(2,0,False),(0,1,False),(1,1,False),(2,1,True))]
        else:

        return RULES
            
    # MOVE CUBE
    def rotate(self, cube, direction, virtual=False):
        # returns a tuple position
        # NOTE: Does not affect config
        # NOTE: virtual=True if cube is not in the configuration (turns off the assert statements)
        if isinstance(cube, Cube):
            c0 = cube.pos
        else:
            c0 = cube

        axis = 0
        posneg = direction[axis]
        while posneg == 0:
            axis = axis + 1
            posneg = direction[axis]
            
        assert abs(posneg) == 1
        
        c1_c3_wrapped_coords = [((0,0,+posneg),(0,+1,0)),
                                ((0,+1,0),(0,0,-posneg)),
                                ((0,0,-posneg),(0,-1,0)),
                                ((0,-1,0),(0,0,+posneg))]
        for (i, j) in c1_c3_wrapped_coords:
            # # derived cubes
            #    ^
            #    |
            #    j
            #
            # c7 c6
            # c2 c3 c4
            # c1 c0 c5  i ->
            i = circshift(i, -axis)
            j = circshift(j, -axis)
            if self.dim == 2:
                i = i[0:2]
                j = j[0:2]
            d1 = i
            d3 = j
            d2 = add_t(i, j)             #(c1[0]+c3[0], c1[1]+c3[1])
            d6 = sca_t(j, 2)             #(2*c3[0], 2*c3[1])
            d7 = add_t(i, sca_t(j, 2))   #(c1[0]+2*c3[0], c1[1]+2*c3[1])
            d5 = sca_t(i, -1)            #(-c1[0], -c1[1])
            d4 = add_t(j, sca_t(i, -1))  #(c3[0]-c1[0], c3[1]-c1[1])

            # inelegant translate
            c1,c2,c3,c4,c5,c6,c7 = map(lambda di: (add_t(c0, di)),
                    (d1,d2,d3,d4,d5,d6,d7))
            if virtual:
                assert cube not in self.config

            # We use c1 as our pivot (fine since such a pivot must exist), so
            # Assume: c1 in config
            if not self.has_cube(c1):
                continue
            # Assume: c3 not in config
            if self.has_cube(c3):
                continue

            # Transfer Move
            if self.has_cube(c4):
                if not virtual:
                    assert not self.has_cube(c6) and not self.has_cube(c7)
                return c5

            # Linear Move
            elif self.has_cube(c2):
                if not virtual:
                    assert not self.has_cube(c4) and not self.has_cube(c5)
                return c3

            # Corner Move
            else:
                if not virtual:
                    assert (not self.has_cube(c4) and not self.has_cube(c5) and
                            not self.has_cube(c6) and not self.has_cube(c7))
                return c2

        return c0


    # CONFIGURATION ANALYSIS
    def find_extreme(self):
        Mx = max([c[0] for c in self.config])
        My = max([c[1] for c in self.config if c[0] == Mx])
        if self.dim > 2:
            Mz = max([c[2] for c in self.config if c[0] == Mx and c[1] == My])
            return Cube((Mx, My, Mz))
        return Cube((Mx, My))

    def classify_configuration(self):
        # calculate O_set
        self.O_set = []
        expos = self.find_extreme()
        virtual_cube = (expos[0]+1, expos[1])
        starting_location = virtual_cube

        virtual_cube = self.rotate(virtual_cube, (0,0,-1), virtual=True)
        
        while virtual_cube != starting_location:
            assert not self.has_cube(virtual_cube)
            for neighbor in self.find_neighbors(virtual_cube):
                if neighbor not in self.O_set:
                    self.O_set.append(neighbor)
            virtual_cube = self.rotate(virtual_cube, (0,0,-1), virtual=True)

        # FORNOW: convention, shows up in step_configuration
        # Basically, we don't want to look in the tail
        # for cubes to move
        if self.extreme in self.O_set:
            self.O_set.remove(self.extreme)
        for cube_t in self.T_set:
            if cube_t in self.O_set:
                self.O_set.remove(cube_t)

        # FORNOW: reverse list for algorithm
        self.O_set.reverse()

        # update M_set
        self.M_set = []
        for cube in self.O_set:
            neighbors_condition = False
            connectivity_condition = False

            # neighbors_condition: enforce any one neighbor,
            # or two neighbors sharing a corner
            # NOTE: greater than zero neighbors is the job
            # of verify_configuration
            cube_neighbors = self.find_neighbors(cube)
            num_neighbors = len(cube_neighbors)
            num_x_neighbors = len([cube2 for cube2 in cube_neighbors
                    if cube2[1] == cube[1]])
            num_y_neighbors = len([cube2 for cube2 in cube_neighbors
                    if cube2[0] == cube[0]])
            if num_x_neighbors <= 1 and num_y_neighbors <= 1:
                neighbors_condition = True

            # connectivity_condition:
            # if one neighbor: True
            # if two neighbors: ensure there exists a path connecting the neighbors
            # but not containing the cube under examination
            if num_neighbors == 1:
                connectivity_condition = True
            elif num_neighbors == 2 and neighbors_condition:
                self.config.remove(cube)
                cube_a = cube_neighbors.pop()
                cube_b = cube_neighbors.pop()
                # restore cube_neighbors to keep things clean
                cube_neighbors = self.find_neighbors(cube)
                connectivity_condition = self.exists_path(cube_a, cube_b)
                self.config.add(cube)

            if neighbors_condition and connectivity_condition:
                self.M_set.append(cube)

        # update N_set
        self.N_set = []
        for cube in self.M_set:
            non_splitting = True
            x, y = cube

            clockwise_2box_coords = [((x+1,y),(x,y+1),(x+1,y+1)),
                                     ((x,y+1),(x-1,y),(x-1,y+1)),
                                     ((x-1,y),(x,y-1),(x-1,y-1)),
                                     ((x,y-1),(x+1,y),(x+1,y-1))]
            for (c_curr, c_next, c_corner) in clockwise_2box_coords:
                if (c_curr in self.config and c_next in self.config
                        and c_corner not in self.config):
                    non_splitting = False

            if non_splitting:
                self.N_set.append(cube)

        # check that we haven't done anything crazy
        assert len(self.config)+len(self.rotating_cubes) == self.config_size

    # IN CONFIGURATION CUBE ANALYSIS
    
    def find_component(self, cube_a):
        '''
        Return the component cube_a is part of as a set
        For connected configurations: all cubes should be
        part of one component
        '''
        # Run a simple breadth-first search
        marked_cubes = set([cube_a])
        prev_cubes = set([cube_a])
        next_cubes = set()
        old_len = -1
        while len(marked_cubes) != old_len:
            old_len = len(marked_cubes)
            for cube in prev_cubes:
                next_cubes.update(self.find_neighbors(cube))
            marked_cubes.update(next_cubes)
            prev_cubes = next_cubes.copy()
        return marked_cubes

    def find_neighbors(self,cube):
        x = cube[0]
        y = cube[1]
        if self.dim > 2:
            z = cube[3]
            neighbors = set([Cube((x+i, y+j, z+k)) for i in [-1,0,1] for j in [-1,0,1] for k in [-1,0,1] if
                self.has_cube((x+i, y+j, z+k)) and abs(i) + abs(j) + abs(k) == 1])
        else:
            neighbors = set([Cube((x+i, y+j)) for i in [-1,0,1] for j in [-1,0,1] if
                self.has_cube((x+i, y+j)) and abs(i) + abs(j) == 1])
        return neighbors

    def exists_path(self, cube_a, cube_b):
        '''
        return True iff there exists a path between cube_a
        and cube_b in configuration
        '''
        return cube_b in self.find_component(cube_a)

    def has_cube(self, pos):
        return Cube(pos) in self.config

    
    # VISUALIZATION AND PRINTING
    def init_draw(self):
        self.drawing = ConfigDraw2D()

    def close_draw(self):
        if not self.drawing == None:
            self.drawing.close()
    
    def __str__(self):
        return str( set( str(a) for a in self.config ) )

def main():
    #c = Configuration(None, False, True)
    #c = Configuration('MIT.config', False, True)
    #c.reconfig()
    c = Configuration([(0,0,0),(1,0,0),(0,0,1), (1,-1,0), (0,-1,0)], False, True)
    c.init_draw()
    c.drawing.draw_configuration(c.config)
    c.drawing.wait(500)
    print c.rotate((1,1,0), (0,0,1))
    print c.rotate((1,1,0), (0,0,-1))
    print c.rotate((1,1,0), (0,1,0))
    print c.rotate((1,1,0), (0,-1,0))
    print c.rotate((1,1,0), (1,0,0))
    print c.rotate((1,1,0), (-1,0,0))
    c.drawing.close()
    print c

if __name__ == '__main__': main()
