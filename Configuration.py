# Config class
#
# has: Cubes
# can: flatten 2D configuration
#      find boundary of 2D configuration
#
# originally: 7/15/2014 by James Bern
# last modified: 9/9/2014 by Cynthia Sung
#
# TODO: add collision detection for parallel algorithm
#

from Cube import Cube
from ConfigDraw import ConfigDraw
from vector_op import *
import random

import sys
import time

# loading configs
import pickle
from pprint import pprint

class Configuration:
    """Configuration class"""

    BUFF = 3

    # INITIALIZATION
    def __init__(self, cubes, ispar = False, dodraw = False, dosave = False):
        self.ispar = ispar

        # for drawing
        self.dodraw = dodraw
        self.drawing = None
        self.dump_png = dosave
        self.frame_i = 0

        # variables for parallel alg
        self.buff_timer = Configuration.BUFF
        self.next_cube = []
        self.next_checkpoint = None

        # the cubes
        self.config = set()
        # initialize the configuration
        if isinstance(cubes, tuple):
            self.init_configuration(cubes, True)
        elif cubes != None:
            self.init_configuration(cubes, False)
        else:
            self.init_configuration(None, False)
        #self.orig_config = copy of self.config cubes
        self.extreme_Z = None

        self.min = [min([tup[i] for tup in self.config]) for i in range(self.dim)]
        self.max = [max([tup[i] for tup in self.config]) for i in range(self.dim)]

        # boundary
        self.O_set = []
        # mobile cubes
        self.M_set = []
        # nonsplitting cubes
        self.N_set = []
        self.P_list = []
        # tail cubes
        self.T_set = []
        self.root = None

        self.rotating_cubes = []
    
    def init_configuration(self, init_config=None, israndom=False):
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
            for temp in init_config: break
            if isinstance(temp, Cube):
                self.dim = temp.dim
                self.config = set(init_config)
            else:
                # creates cubes from a set
                MX = min([tup[0] for tup in init_config])
                MY = max([tup[1] for tup in init_config])
                self.dim = len(temp)
                
                if self.dim > 2:
                    MZ = min([tup[2] for tup in init_config])
                    self.config = set(Cube((tup[0]-MX,MY-tup[1],tup[2]-MZ)) for tup in init_config)
                else:
                    self.config = set(Cube((tup[0]-MX,MY-tup[1])) for tup in init_config)
        elif israndom:
            # random configuration
            self.init_configuration(self.randomConfig(init_config[0], init_config[1]), False)
        else:
            # default configuration
            config = set([(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (1, 0), (1, 3), (1, 6), (1, 9), (1, 12), (2, 0), (2, 3), (2, 6), (2, 9), (2, 12), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12), (4, 0), (4, 3), (4, 6), (4, 9), (4, 12), (5, 0), (5, 3), (5, 6), (5, 9), (5, 12), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (6, 11), (6, 12), (7, 0), (7, 3), (7, 6), (7, 9), (7, 12), (8, 0), (8, 3), (8, 6), (8, 9), (8, 12), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9), (9, 10), (9, 11), (9, 12), (10, 0), (10, 3), (10, 6), (10, 9), (10, 12), (11, 0), (11, 3), (11, 6), (11, 9), (11, 12), (12, 0), (12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10), (12, 11), (12, 12)])
            self.init_configuration(config, False)
            
        # Always need to run these
        self.config_size = len(self.config)
        self.extreme = self.find_extreme()

    def randomConfig(self, N = 10, dim = 2):
        tryAgain = True
        
        while tryAgain :
            # loop-erased random walk
            if dim == 2 :
                currentnode = (0,0)
                neighdir = {0: (0,1), 1:(1,0), 2:(0,-1), 3:(-1,0)}
            else :
                currentnode = (0,0,0)
                neighdir = {0: (0,1,0), 1:(1,0,0), 2:(0,-1,0), 3:(-1,0,0), 4:(0,0,1), 5:(0,0,-1)}

            config = set([currentnode])
            currN = 1
            
            while currN < N:
                newneigh = random.choice(range(len(neighdir)))
                neighnode = add_t(currentnode, neighdir[newneigh])
                if neighnode not in config :
                    config.add(neighnode)
                    currN = currN + 1
                currentnode = neighnode

            testC = Configuration(config, self.ispar, self.dodraw, self.dump_png);

            tryAgain = (testC.verify_configuration() != None)

        return config
            

    # RECONFIGURATION ALGORITHM
    def flatten(self, root = None):
        self.frame_i = 0
        self.root = root
        
        if self.dodraw:
            self.init_draw()

        #FIXME
        check_valid = self.verify_configuration()
        check_valid = None
        if check_valid != None:
            print("Configuration is invalid!")
            if self.dodraw:
                self.drawing.draw_configuration(self.config, [check_valid])
                while not self.drawing.check_draw_close(): pass
                self.close_draw()
            return

        print("Configuration valid!")

        if self.dim == 2:
            self.extreme_Z = self.extreme
            success = self.flatten2D()
        else:
            success = True
            V_S, G_S = self.slice_graph()
            block_comp, block_graph = self.get_block_graph(G_S)

            comp = self.find_extreme_slice(V_S, G_S, block_comp, block_graph)

            self.root = comp.root
            z = self.root[2]
            print self.root
            
            self.extreme_Z = self.find_extreme(z)
            self.classify_configuration(z)
            if self.dodraw:
                #self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes, [self.root])
                self.drawing.wait(500)
            
            done_relocate = False
            print self.extreme_Z
                
            while not done_relocate:
                done_relocate = self.relocate_next_to_tail_2D()

                # move to 3D extreme
                
                self.classify_configuration(z)

                if self.dodraw:
                    #self.drawing.draw_configuration(comp.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes, [self.root])
                    self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes, [self.root])
                    self.drawing.wait(1000)

                if done_relocate == None :
                    success = False
                    done_relocate = True
                    
            print self

        while not self.drawing.check_draw_close(): pass
        
        if self.dodraw:
            self.close_draw()
            
        return success
    
    def flatten2D(self):
        self.classify_configuration()
        if self.dodraw:
            self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes, [self.root])
            self.drawing.wait(500)

        done_relocate = False

        while not done_relocate:
            done_relocate = self.relocate_next_to_tail_2D()
            
            # update_configuration is actually what hangs the program
            # but we can't draw until we finish it.
            self.classify_configuration()

            if self.dodraw:
                self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes, [self.root])
                if self.drawing.check_draw_close():
                    break
                
        if done_relocate == None: # user quit middle of relocation
            done_relocate = False
        return done_relocate

    def relocate_next_to_tail_2D(self):
        do_next_step = True
        while do_next_step:
            self.frame_i += 1
            
            do_next_step = self.step_configuration()
            
            '''
            try:
                self.detect_collisions()
            except AssertionError, e:
                print "running cubes collide!"
                print e
                while not self.drawing.check_draw_close(): pass
                break
            '''
            
            if do_next_step == None:
                return True
            
            if self.dodraw:
                self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes, [self.root])
                if self.drawing.check_draw_close():
                    return None
                
            if self.dump_png:
                pad = '0'*(4-len(str(self.frame_i)))
                self.drawing.save('frame' + pad + str(self.frame_i) + '.png')

        return False

    def step_configuration(self):
        # Stage next_cube or next_P4 to run (if buff timer expended)
        # Wait on/decrement timer
        not_reclassify = True
        if (self.next_checkpoint==None and self.next_cube) or (self.rotating_cubes and self.rotating_cubes[-1].pos == self.next_checkpoint):
            # Stage cubes
            # Standard tail relocation
            if self.next_cube:
                # get next cube to move
                thecube = self.next_cube.pop(0)
                nc = thecube[0]   # cube id
                chk = thecube[1]  # checkpoint
                
                assert nc in self.config
                self.rotating_cubes.append(nc)
                self.config.remove(nc)
                self.next_checkpoint = chk
            else:
                self.next_checkpoint = None
                not_reclassify = False

        # run the cubes
        # No more cubes to move. Just wait for everything that's moving to get to the tail
        if self.rotating_cubes:
            next_rotating_cubes = []
            for cube_r in self.rotating_cubes:
                # Still running...
                if not (cube_r[1] == self.extreme_Z[1] and cube_r[0] > self.extreme_Z[0]):
                    newpos = self.rotate(cube_r, cube_r.dir)
                    cube_r.translate(sub_t(newpos,cube_r.pos))
                    next_rotating_cubes.append(cube_r)
                # Made it to the tail.
                else:
                    self.config.add(cube_r)
                    self.T_set.append(cube_r)
                    # do _not_ add to next_running_cubes
            self.rotating_cubes = next_rotating_cubes
        elif not self.next_cube:
            print ("We made it.")
            return None
        return not_reclassify
        
    # CHECK RULES FOR CONFIGURATIONS
    def verify_configuration(self):
        if self.config_size == 0:
            return None
        
        # connectivity condition
        for c1 in self.config: break
        comp_c1 = self.find_component(c1,False)
        for c2 in self.config:
            if not c2 in comp_c1:
                print "configuration disconnected"
                return c2.pos

        # check rules
        RULES = self.get_rules()
        search_dict = self.search_dir()

        for c0 in self.config:
            cpos = c0.pos

            # major axes and minor axes
            for (major, minors) in search_dict.iteritems():
                for minor in minors:
                    # check each rule
                    for i in range(len(RULES)):
                        r = RULES[i]
                        # if we broke a rule
                        if self.has_instance(r, cpos, major, minor):
                            print "configuration violated rule", i+1
                            return c0
        return None

    def has_instance(self, rule, pos, major, minor):
        failedTest = True
        for cond in rule:
            ci = add_t(add_t(pos, sca_t(major, cond[0])), sca_t(minor, cond[1]))
            if (self.has_cube(ci) != cond[2]):
                failedTest = False
                break
        return failedTest

    def P_search(self, m1):
        if isinstance(m1,Cube):
            m1 = m1.pos

        search_dict = self.search_dir()
        if self.ispar:
            Plen = 4
        else:
            Plen = 3
        P = self.P(Plen)

        for (major, minors) in search_dict.iteritems():
            for minor in minors:
                # we found an instance of P_i
                if self.has_instance(P, m1, major, minor):
                    P = [Cube(add_t(m1, sca_t(major, i))) for i in range(Plen)]
                    return P
        return None
            
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
    def find_extreme(self, Mz = None):
        if self.dim > 2 :
            if Mz == None :
                Mz = max([c[2] for c in self.config])
            Mx = max([c[0] for c in self.config if c[2] == Mz])
            My = max([c[1] for c in self.config if c[2] == Mz and c[0] == Mx])

            return Cube((Mx, My, Mz))
        else:
            Mx = max([c[0] for c in self.config])
            My = max([c[1] for c in self.config if c[0] == Mx])

            return Cube((Mx, My))

    def classify_configuration(self, z = 0):
        # calculate O_set
        self.O_set = []
        expos = self.find_extreme(z)

        if self.dim > 2:
            virtual_cube = (expos[0]+1, expos[1], z)
        else:
            virtual_cube = (expos[0]+1, expos[1])
        starting_location = virtual_cube

        virtual_cube = self.rotate(virtual_cube, (0,0,-1), virtual=True)
        
        while virtual_cube != starting_location:
            assert not self.has_cube(virtual_cube)
            for neighbor in self.find_neighbors(virtual_cube,True):
                if neighbor not in self.O_set:
                    self.O_set.append(neighbor)
            virtual_cube = self.rotate(virtual_cube, (0,0,-1), virtual=True)

        # FORNOW: convention, shows up in step_configuration
        # Basically, we don't want to look in the tail
        # for cubes to move
        if self.extreme in self.O_set:
            self.O_set.remove(self.extreme_Z)
        for cube_t in self.T_set:
            if cube_t in self.O_set:
                self.O_set.remove(cube_t)

        # FORNOW: reverse list for algorithm
        self.O_set.reverse()

        # update M_set
        self.M_set = []
        for cube in self.O_set:
            if cube == self.root or cube == self.extreme_Z :
                continue
            
            neighbors_condition = False
            connectivity_condition = False

            # neighbors_condition: enforce any one neighbor,
            # or two neighbors sharing a corner
            # NOTE: greater than zero neighbors is the job
            # of verify_configuration
            cube_neighbors = self.find_neighbors(cube,True)
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
                cube_neighbors = self.find_neighbors(cube,True)
                connectivity_condition = self.exists_path(cube_a, cube_b)
                self.config.add(cube)

            if neighbors_condition and connectivity_condition :
                self.M_set.append(cube)

        # update N_set
        self.N_set = []
        self.P_set = []
        for cube in self.M_set:
            splitting = False
            
            x = cube[0]
            y = cube[1]
            
            if self.dim > 2:
                z = cube[2]
                clockwise_2box_coords = [((x+1,y,z),(x,y+1,z),(x+1,y+1,z)),
                                         ((x,y+1,z),(x-1,y,z),(x-1,y+1,z)),
                                         ((x-1,y,z),(x,y-1,z),(x-1,y-1,z)),
                                         ((x,y-1,z),(x+1,y,z),(x+1,y-1,z))]
            else:
                clockwise_2box_coords = [((x+1,y),(x,y+1),(x+1,y+1)),
                                         ((x,y+1),(x-1,y),(x-1,y+1)),
                                         ((x-1,y),(x,y-1),(x-1,y-1)),
                                         ((x,y-1),(x+1,y),(x+1,y-1))]
            for (c_curr, c_next, c_corner) in clockwise_2box_coords:
                if (self.has_cube(c_curr) and self.has_cube(c_next)
                        and not self.has_cube(c_corner)):
                    splitting = True

            # FORNOW: sloppy in so many ways
            if not splitting:
                self.N_set.append(cube)

                if not self.next_cube:
                    # compute checkpoint
                    if self.ispar:
                        chk = cube.pos
                        for _ in xrange(Configuration.BUFF+3):
                            newchk = self.rotate(chk, cube.dir)
                            if newchk[1] == self.extreme_Z[1]:
                                diff0 = newchk[0]-self.extreme_Z[0]-len(self.T_set)
                                if diff0 > 0:
                                    if diff0 <= len(self.rotating_cubes):
                                        chk = (newchk[0], chk[1])
                                    break
                            chk = newchk
                    else:
                        chk = (self.extreme_Z[0]+len(self.T_set)+len(self.rotating_cubes)+1, self.extreme_Z[1])

                    if self.dim > 2 :
                        chk = (chk[0], chk[1], z)
                    print "NEXT NC:", cube
                    #print "NEXT CHECKPOINT:", chk
                    self.next_cube = [(cube,chk)]
            else:
                search_results = self.P_search(cube)
                P = search_results
                if search_results != None and not self.root in P :
                    self.P_set.append(P)
                    if not self.next_cube:
                        # compute checkpoint
                        if self.ispar:
                            endTail = False
                            chk = cube.pos
                            for _ in xrange(Configuration.BUFF+3):
                                newchk = self.rotate(chk, cube.dir)
                                if newchk[1] == self.extreme_Z[1]:
                                    diff0 = newchk[0]-self.extreme_Z[0]-len(self.T_set)
                                    if diff0 > 0:
                                        if diff0 <= len(self.rotating_cubes):
                                            chk = (newchk[0], chk[1])
                                        break
                                chk = newchk
                        else:
                            chk = (self.extreme_Z[0]+len(self.T_set)+len(self.rotating_cubes)+1, self.extreme_Z[1])
                            endTail = True

                        if self.dim > 2 :
                            chk = (chk[0], chk[1], z)
                        print "NEXT P:", cube
                        #print "NEXT CHECKPOINT:", chk
                        if self.dim > 2 :
                            self.next_cube = [(P[i],add_t(chk,(i if endTail else 0,0,z))) for i in range(len(P))]
                        else :
                            self.next_cube = [(P[i],add_t(chk,(i if endTail else 0,0))) for i in range(len(P))]
            

        # check that we haven't done anything crazy
        assert len(self.config)+len(self.rotating_cubes) == self.config_size

    def find_extreme_slice(self, V_S, G_S, V_B, G_B):
        comp = None
        ncomp = len(V_S)
        
        # look for a slice with degree 1
        for cid in range(ncomp):
            if len(G_S[cid]) == 1 and self.extreme not in V_S[c].config :
                comp = V_S[cid]
                neighdir = G_S[cid][0][1] # direction of the slice
                break
            
        if comp == None :
            # look for a locally extreme double-connected slice
            for bc in range(len(V_B)):
                if len(G_B[bc]==1) and (True not in [ self.extreme in V_S[cid] for cid in V_B[bc] ]):
                    for cid in V_B[bc] :
                        isextreme = True
                        neighdir = G_S[cid][0][1] # direction of the slice
                        for i in range(1,len(G_S[cid])) :
                            if G_S[cid][i][1] != neighdir :
                                isextreme = False
                                break
                        if isextreme :
                            comp = V_S[cid]
                            break
                    break


        # find point of connectivity for comp
        for c in comp.config:
            if self.has_cube((c[0],c[1],c[2]+neighdir)) :
                comp.root = c
                break
            
        return comp

    def get_block_graph(self, G_S) :
        if not G_S :
            return G_S, G_S

        ncomp = len(G_S)
        visited = [False for i in range(ncomp)]
        is_articulation_point = [False for i in range(ncomp)]
        parent = [-1 for i in range(ncomp)]
        depth = [sys.maxint for i in range(ncomp)]
        min_succ_depth = [sys.maxint for i in range(ncomp)]
        root = 0
        depth[0] = 0
        
        currvert = [0]
        while currvert :
            thisvert = currvert[-1]
            if not visited[thisvert] :
                # thisvert visited for the first time
                visited[thisvert] = True
                min_succ_depth[thisvert] = depth[thisvert]
            else :
                # child of x has been fully processed
                # continue next child
                pass
            
        return V_B, G_B

    def slice_graph(self):
        V_S = dict()
        G_S = dict()

        allcubes = self.config.copy()

        ncomp = 0
        while allcubes:
            cube = allcubes.pop()

            if self.dim > 2:
                z = cube[2]
            
            comp = self.find_component(cube,True)
            Cz = Configuration(comp)            
            allcubes = allcubes.difference(comp)

            if self.dim > 2:
                neigh = [(i, j) for i in range(ncomp) if
                         [ c for c in V_S[i].config for j in [-1,1] if (Cz.has_cube((c[0],c[1],c[2]+j))) ] ]
                for n in neigh:
                    i = n[0]; j = n[1]
                    G_S[i].append((ncomp,-j))
            else:
                neigh = []
                
            V_S[ncomp] = Cz
            G_S[ncomp] = neigh
            ncomp += 1
        return (V_S, G_S)

    def slice2D(self, z):
        return Configuration([c for c in self.config if c[2]==z])

    # IN CONFIGURATION CUBE ANALYSIS
    def find_component(self, cube_a, is2D):
        '''
        Return the 2D slice component cube_a is part of as a set
        For connected 2D configurations: all cubes should be
        part of one component

        Returns Cubes
        '''
        # Run a simple breadth-first search
        marked_cubes = set([cube_a])
        prev_cubes = set([cube_a])
        next_cubes = set()
        old_len = -1
        while len(marked_cubes) != old_len:
            old_len = len(marked_cubes)
            for cube in prev_cubes:
                next_cubes.update(self.find_neighbors(cube,is2D))
            marked_cubes.update(next_cubes)
            prev_cubes = next_cubes.copy()
        return marked_cubes

    def find_neighbors(self,cube, is2D):
        '''
        return a list of neighbors in the xy plane, in clockwise order if possible.
        e.g. for - y -
                 - c x
                 - - -
        the returned list should be [x, y]
        '''
        x = cube[0]
        y = cube[1]
        if self.dim > 2:
            z = cube[2]

            if is2D :
                krange = [0] # do not search for z neighbors
            else :
                krange = [-1,0,1]

            neighbors = set([Cube((x+i, y+j, z+k)) for i in [-1,0,1] for j in [-1,0,1] for k in krange if
                self.has_cube((x+i, y+j, z+k)) and abs(i) + abs(j) + abs(k) == 1])

            clockwise_2box_coords = [((x+1,y,z),(x,y+1,z),(x+1,y+1,z)),
                                     ((x,y+1,z),(x-1,y,z),(x-1,y+1,z)),
                                     ((x-1,y,z),(x,y-1,z),(x-1,y-1,z)),
                                     ((x,y-1,z),(x+1,y,z),(x+1,y-1,z))]
        else:
            neighbors = set([Cube((x+i, y+j)) for i in [-1,0,1] for j in [-1,0,1] if
                self.has_cube((x+i, y+j)) and abs(i) + abs(j) == 1])

            clockwise_2box_coords = [((x+1,y),(x,y+1),(x+1,y+1)),
                                     ((x,y+1),(x-1,y),(x-1,y+1)),
                                     ((x-1,y),(x,y-1),(x-1,y-1)),
                                     ((x,y-1),(x+1,y),(x+1,y-1))]

        # FORNOW: this is a hack
        if is2D :
            if len(neighbors) == 2:
                for (c_curr, c_next, _) in clockwise_2box_coords:
                    if (self.has_cube(c_curr) and self.has_cube(c_next)):
                        return [Cube(c_curr), Cube(c_next)]
        
        return neighbors

    def exists_path(self, cube_a, cube_b):
        '''
        return True iff there exists a path between cube_a
        and cube_b in configuration
        '''
        return cube_b in self.find_component(cube_a, True)

    def has_cube(self, pos):
        return Cube(pos) in self.config

    
    # VISUALIZATION AND PRINTING
    def init_draw(self):
        self.drawing = ConfigDraw(self.dim)

    def show(self):
        self.init_draw()

        self.drawing.draw_configuration(self.config)

        while not self.drawing.check_draw_close(): pass
        self.close_draw()

    def close_draw(self):
        if not self.drawing == None:
            self.drawing.close()
    
    def __str__(self):
        return str( set( str(a) for a in self.config ) )

    # CONSTANTS
    def get_rules(self):
        RULES = [((0,0,True),(1,0,False),(2,0,True)),
                    ((0,0,True),(1,0,False),(0,1,False),(1,1,True)),
                    ((0,0,True),(1,0,False),(2,0,False),(0,1,False),(1,1,False),(2,1,True))]
        if self.ispar:
            more_rules = [((0,0,True),(1,0,False),(2,0,False),(3,0,True)),
                          ((0,0,True),(1,0,False),(2,0,False),(0,1,False),(1,1,False),(2,1,False),(0,2,False),(1,2,False),(2,2,True)),
                          ((0,0,True),(1,0,False),(0,1,False),(1,1,False),(0,2,False),(1,2,False),(0,3,False),(1,3,True)),
                          ((0,0,True),(1,0,False),(2,0,False),(0,1,False),(1,1,False),(2,1,False),(0,2,False),(1,2,False),(2,2,False),(0,3,False),(1,3,False),(2,3,True))]
            RULES.extend(more_rules)
        return RULES

    def P(self, N):
        P = [(i,j,j%2==0) for i in range(N) for j in range(2)]
        return P

    def search_dir(self):
        if self.dim > 2:
            U = (0,0,1); D = (0,0,-1);
            R = (1,0,0); L = (-1,0,0);
            F = (0,1,0); B = (0,-1,0);
            LRFB = (L,R,F,B); UDFB = (U,D,F,B); UDLR = (U,D,L,R);
            search_dict = {U:LRFB, D:LRFB, R:UDFB, L:UDFB, F:UDLR, B:UDLR}
        else:
            U = (0,1); D = (0,-1);
            R = (1,0); L = (-1,0);
            LR = (L,R); UD = (U,D);
            search_dict = {U:LR, D:LR, R:UD, L:UD}
        return search_dict

def main():
    c = Configuration((10,3), False, True)
    print c.config_size
    #c = Configuration('small.config', False, True)
    #c = Configuration('pargrid.config', True, True)
    #print c.min, c.max
    #c.flatten2D()
    #c2 = Configuration([(0,0,0),(1,0,0),(0,-1,0),
    #                   (0,0,1),(2,0,1),
    #                   (0,0,2),(2,0,2),(3,0,2),
    #                   (0,0,3),(1,0,3),(1,1,3),(2,0,3),
    #                   (0,0,4),(-1,0,4),(1,1,4),(2,1,4)],
    #                  False, False)
    c2 = Configuration([(ctemp[0],ctemp[1]+1,i) for ctemp in c.config for i in range(3)],
                       False, True)
    print c
    c.show()
    c2.show()
    #c.flatten()
        
    #c.init_draw()
    #c.drawing.draw_configuration(c.config)
    #print c.verify_configuration()
    #c.drawing.wait(500)
    #print c.rotate((1,1,0), (0,0,1))
    #print c.rotate((1,1,0), (0,0,-1))
    #print c.rotate((1,1,0), (0,1,0))
    #print c.rotate((1,1,0), (0,-1,0))
    #print c.rotate((1,1,0), (1,0,0))
    #print c.rotate((1,1,0), (-1,0,0))
    #c.drawing.close()
    #print c

if __name__ == '__main__': main()
