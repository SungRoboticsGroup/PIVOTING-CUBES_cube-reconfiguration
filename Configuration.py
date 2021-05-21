# Config class
#
# has: Cubes
# can: flatten 2D configuration
#      find boundary of 2D configuration
#
# originally: 7/15/2014 by James Bern
# last modified: 9/9/2014 by Cynthia Sung
# On 8/20/2020, Daniel Feshbach began working with this file, adding this comment to do a test commit
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
import csv

class Configuration:
    """Configuration class"""

    BUFF = 3

    # INITIALIZATION
    def __init__(self, cubes, ispar = False, dodraw = False, dosave = False, saveprefix = ''):
        self.ispar = ispar

        # for drawing
        self.dodraw = dodraw
        self.drawing = None
        self.dosave = dosave
        self.save_prefix = saveprefix
        self.file = []

        # variables for parallel alg
        self.buff_timer = Configuration.BUFF
        self.nextcube_info = []
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
        self.extreme_of_slice = None

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
        self.slice_root = None

        self.rotating_cubes = []
        self.Nsteps = 0
    
    def init_configuration(self, init_config=None, israndom=False):
        if isinstance(init_config, str):
            # load config from file
            try:
                g = open(init_config, 'r')
                if (init_config[-4:]==".csv"):
                    init_file = csv.reader(g)
                    input_config = []
                    for line in init_file:
                        #print line
                        if len(line)>=3:
                            input_config.append((int(line[0]),int(line[1]),int(line[2])))
                    #print input_config
                elif (init_config[-7:]==".config"):
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
                MY = min([tup[1] for tup in init_config])
                self.dim = len(temp)
                
                if self.dim > 2:
                    MZ = min([tup[2] for tup in init_config])
                    self.config = set(Cube((tup[0]-MX,tup[1]-MY,tup[2]-MZ)) for tup in init_config)
                else:
                    self.config = set(Cube((tup[0]-MX,tup[1]-MY)) for tup in init_config)
        elif israndom:
            # random configuration
            self.init_configuration(self.randomConfig(init_config[0], init_config[1]), False)
        else:
            # default configuration
            config = set([(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (1, 0), (1, 3), (1, 6), (1, 9), (1, 12), (2, 0), (2, 3), (2, 6), (2, 9), (2, 12), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12), (4, 0), (4, 3), (4, 6), (4, 9), (4, 12), (5, 0), (5, 3), (5, 6), (5, 9), (5, 12), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (6, 11), (6, 12), (7, 0), (7, 3), (7, 6), (7, 9), (7, 12), (8, 0), (8, 3), (8, 6), (8, 9), (8, 12), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9), (9, 10), (9, 11), (9, 12), (10, 0), (10, 3), (10, 6), (10, 9), (10, 12), (11, 0), (11, 3), (11, 6), (11, 9), (11, 12), (12, 0), (12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10), (12, 11), (12, 12)])
            self.init_configuration(config, False)
            
        # Always need to run these
        self.config_size = len(self.config)
        self.last_cube = self.find_extreme_cube()

    #generates random configurations, throws them away if inadmissible
    def randomConfig(self, N = 10, dim = 2):
        tryAgain = True
        
        while tryAgain :
            print 'trying'
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

            testC = Configuration(config, self.ispar, self.dodraw, self.dosave);

            tryAgain = testC.verify_configuration()
            while tryAgain != None :
                if tryAgain[1] == 0 :
                    #connectivity problem
                    tryAgain = True
                    break
                else :
                    pos = tryAgain[0].pos
                    rule = tryAgain[1]
                    major = tryAgain[2]
                    
                    todo = random.choice([0,1])
                    
                    if todo == 0 or rule > 3:
                        # delete the cube
                        testC.config.remove(Cube(tryAgain[0]))
                    else :
                        if rule == 1 :
                            # add a cube in the direction of the rule break
                            testC.config.add(Cube(add_t(pos, major)))
                        elif rule == 2 :
                            # add a cube in the direction of the rule break
                            testC.config.add(Cube(add_t(pos, major)))
                        elif rule == 3 :
                            # add a cube in the direction of the rule break
                            testC.config.add(Cube(add_t(pos, major)))
                            testC.config.add(Cube(add_t(pos, sca_t(major, 2))))
                
                tryAgain = testC.verify_configuration()
                
            if tryAgain == None :
                tryAgain = False

        return testC.config

    def randomConfig2(self, N = 10, dim = 2) :
        tryAgain = True

        while tryAgain :
            # create block
            l = int(N ** (1 / float(dim)));

            if dim == 2 :
                config = [(int(i/l), i%l) for i in range(N)]
                neigh = [(c[0]+dx,c[1]+dy) for c in config for dx in [-1, 1] for dy in [-1, 1] if (c[0]+dx,c[1]+dy) not in config]
            else :
                config = [(int(i/(l*l)), int(i/l)%l, i%l) for i in range(N)]
                neigh = [(c[0]+dx,c[1]+dy,c[2]+dz) for c in config for dx in [-1, 1] for dy in [-1, 1] for dz in [-1, 1] if (c[0]+dx,c[1]+dy,c[2]+dz) not in config]

            # move blocks
            for _ in range(N*N) :
                posfrom = random.choice(range(len(config)))

                posto = random.choice(range(len(neigh)))

                ctemp = list(config)
                ctemp[posfrom] = neigh[posto]
                ctemp = Configuration(set(ctemp), self.ispar, self.dodraw, self.dosave)

                if ctemp.is_connected() == None :
                    config[posfrom] = neigh[posto];

                # update neighbors
                if dim == 2 :
                    neigh = [(c[0]+dx,c[1]+dy) for c in config for dx in [-1, 1] for dy in [-1, 1] if (c[0]+dx,c[1]+dy) not in config]
                else :
                    neigh = [(c[0]+dx,c[1]+dy,c[2]+dz) for c in config for dx in [-1, 1] for dy in [-1, 1] for dz in [-1, 1] if (c[0]+dx,c[1]+dy,c[2]+dz) not in config]

            testC = Configuration(set(config), self.ispar, self.dodraw, self.dosave);

            tryAgain = (testC.verify_configuration() != None)
                
        return set(config)
            

    # RECONFIGURATION ALGORITHM
    def flatten(self, branch=None, root = None):
        ''' 
        branch is the local branch being deconstructed by this call
        self is the whole configuration
        '''
        print("configuration size: "+str(len(self.config)))
        if branch:                  # If we're operating on a branch, 
            for c in branch.config:         # it should start out as a subset of the global configuration
                assert(c in self.config)
            print("branch size: "+str(len(branch.config)))

        self.slice_root = root
        self.Nsteps = 0
        
        if self.dodraw:
            self.init_draw()
        elif self.dosave :
            self.file = open(self.save_prefix + '_steps.record', 'w')
            self.file.write(str(self.dim))
            self.file.write('\n')
            self.file.write(str(self))
            self.file.write('\n')
        
        check_valid = self.verify_configuration()
        if check_valid != None:
            print("Configuration is invalid!")
            if self.dodraw:
                self.drawing.draw_configuration(self.config, [check_valid])
                while not self.drawing.check_draw_close(): pass
                self.close_draw()
            return False
        if branch:
            check_branch_valid = branch.verify_configuration()
            if check_branch_valid != None:
                print("Configuration is invalid!")
                if branch.dodraw:
                    branch.drawing.draw_configuration(branch.config, [check_branch_valid])
                    while not branch.drawing.check_draw_close(): pass
                    branch.close_draw()
                return False

        print("Configuration valid!")

        if self.dim == 2:
            self.extreme_of_slice = self.last_cube
            success = self.flatten2D()
        else:
            success = True
            if branch:
                V_S, G_S = branch.slice_graph()
            else:
                V_S, G_S = self.slice_graph()

            ########## LOOP OVER SLICES ##########
            while len(V_S)>0:              #used to be while nextslice :
                # Select slice to deconstruct, set slice.slice_root and slice.extreme_in_slice
                if branch:  # relies on branch.last_module having been set properly 
                            # (which branch_to_remove should have done when constructing branch)
                    slice, cid = branch.find_extreme_slice(V_S, G_S) 
                else:
                    slice, cid = self.find_extreme_slice(V_S, G_S)
                
                ########## MOVE CUBES IN SLICE TO THE GLOBAL TAIL    ##########
                ########## Pausing to remove branches as necessary   ##########
                for tcube in slice.slice_deconstruction_order():
                    assert(tcube in self.config)
                    # If there's an inner branch that has to be removed before tcube, remove it
                    next_branch = self.branch_to_remove(next_cube=tcube) 
                    if next_branch:
                        slice_ids = slice_ids_in(next_branch.config, V_S)
                        print("slice ids before branch removal = " + str(V_S.keys()))
                        print("next_branch slice ids: " + str(slice_ids))
                        print("next_branch: " + str(next_branch))
                        self.flatten(branch=next_branch)
                        for slice_id in slice_ids:
                            remove_slice(V_S, G_S, slice_id)
                        print("slice ids remaining after branch removal = " + str(V_S.keys()))
                    
                    # Move tcube to the global tail:
                    self.config.remove(tcube)
                    tpath = self.find_path(tcube.pos, add_t(self.last_cube.pos, (0,0,len(self.T_set)+1)))
                    tcube = self.rotate_cube_along_path(tcube, tpath)
                    if tcube == None :
                        done_relocate = False
                        nextslice = False
                        break
                    else :
                        self.config.add(tcube)
                        self.T_set.append(tcube) #it is now on the 3D tail
                ################################################################

                if self.dodraw:
                    #self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes, [self.slice_root])
                    self.drawing.wait(500)
                elif self.dosave:
                    self.file.write('Slice: ')
                    self.file.write(str(slice))
                    self.file.write('\n')
                
                # remove slice from slice graph V_S, G_S
                for i in G_S :
                    todelete = [c for c in G_S[i] if c[0]==cid]
                    for d in todelete :
                        G_S[i].remove(d)
                G_S.pop(cid)
                V_S.pop(cid)
            ########## END OF LOOP OVER SLICES ##########
            
        if self.dodraw:
            while not self.drawing.check_draw_close(): pass
        
            self.close_draw()
        elif self.dosave and not branch :
            self.file.close()
            
        return success

                
    
    def flatten2D(self):
        self.classify_slice_cubes()
        if self.dodraw:
            self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes, [self.slice_root])
            self.drawing.wait(500)

        done_relocate = False

        while not done_relocate:
            done_relocate = self.relocate_next_to_tail_2D()
            
            # update_configuration is actually what hangs the program
            # but we can't draw until we finish it.
            self.classify_slice_cubes()

            if self.dodraw:
                self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes, [self.slice_root])
                if self.drawing.check_draw_close():
                    break
                
        if done_relocate == None: # user quit middle of relocation
            done_relocate = False
        return done_relocate
    
    def relocate_next_to_tail_2D(self):
        do_next_step = True
        while do_next_step:
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
                self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, self.rotating_cubes, [self.slice_root])
                #self.drawing.wait(50)
                if self.drawing.check_draw_close():
                    return None
                
        return False

    def step_configuration(self):
        # Stage next_cube or next_P4 to run (if buff timer expended)
        # Wait on/decrement timer
        not_reclassify = True
        if (self.next_checkpoint==None and self.nextcube_info) or (self.rotating_cubes and self.rotating_cubes[-1].pos == self.next_checkpoint):
            # Stage cubes
            # Standard tail relocation
            if self.nextcube_info:
                # get next cube to move
                thecube = self.nextcube_info.pop(0)
                nc = thecube[0]   # cube id
                chk = thecube[1]  # checkpoint

                if  self.dim > 2 and (self.rotating_cubes and self.rotating_cubes[-1].pos == self.next_checkpoint):
                    not_reclassify = False
                
                if nc not in self.config :
                    print nc
                    assert nc in self.config
                self.rotating_cubes.append(nc)
                self.config.remove(nc)
                self.next_checkpoint = chk
                #print "CHK: ", self.next_checkpoint
            else:
                self.next_checkpoint = None
                not_reclassify = False

        # run the cubes
        # No more cubes to move. Just wait for everything that's moving to get to the tail
        if self.rotating_cubes:
            self.Nsteps = self.Nsteps + 1
            next_rotating_cubes = []
            for cube_r in self.rotating_cubes:
                if self.dosave and not self.dodraw :
                    self.file.write('['+str(cube_r)+', ')
                # Still running...
                if not (cube_r[1] == self.extreme_of_slice[1] and cube_r[0] > self.extreme_of_slice[0]):
                    newpos, rotneigh = self.rotate(cube_r, cube_r.dir)
                    cube_r.translate(sub_t(newpos,cube_r.pos))
                    next_rotating_cubes.append(cube_r)
                    if self.dosave and not self.dodraw :
                        self.file.write(str(cube_r)+', '+str(rotneigh)+', ')
                        self.file.write(str(cube_r.dir)+']')
                # Made it to the tail.
                else:
                    self.config.add(cube_r)
                    self.T_set.append(cube_r)
                    # do _not_ add to next_running_cubes
                    if self.dosave and not self.dodraw :
                        self.file.write(']')
            self.rotating_cubes = next_rotating_cubes
            if self.dosave and not self.dodraw :
                self.file.write('\n')
        elif not self.nextcube_info:
            #print ("We made it.")
            return None
        return not_reclassify

    def rotate_cube_along_path(self, tcube, tpath) :

        actpos = tcube.pos
        while tpath :
            if self.dosave and not self.dodraw :
                self.file.write('[Cube['+str(actpos)+'], ')

            newpos, rotaxis = tpath.pop()
            if actpos != newpos :
                print "theres a problem", actpos, newpos
            #else :
            #   print actpos, newpos
            actpos, rotneigh = self.rotate(actpos, rotaxis)
            self.Nsteps = self.Nsteps + 1

            if self.dodraw:
                self.drawing.draw_configuration(self.config, self.O_set, self.M_set, self.N_set, self.T_set, [Cube(actpos)], [self.slice_root])
                #self.drawing.wait(50)
                if self.drawing.check_draw_close():
                    return None
            elif self.dosave :
                self.file.write('Cube['+ str(actpos)+'], '+str(rotneigh)+', ')
                self.file.write(str(rotaxis)+']\n')
            
        if self.dosave and not self.dodraw :
            self.file.write('[Cube['+str(actpos)+'], ]\n')
        tcube.translate(sub_t(actpos,tcube.pos))
        return tcube
        
    # CHECK RULES FOR CONFIGURATIONS
    def verify_configuration(self):
        if self.config_size == 0:
            return None

        discon_cube = self.is_connected()
        if not discon_cube == None :
            #print "configuation disconnected"
            return (discon_cube.pos,0)

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
                            #print "configuration violated rule", i+1
                            return (c0, i+1, major, minor)
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

    def is_connected(self):
        # connectivity condition
        for c1 in self.config: break
        comp_c1 = self.find_component(c1,False)
        for c2 in self.config:
            if not c2 in comp_c1:
                return c2
            
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
            #    c6 c7
            # c4 c3 c2
            # c5 c0 c1  i ->
            # c9 c8
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
            d8 = sca_t(j, -1)
            d9 = add_t(sca_t(i, -1), sca_t(j, -1))

            # inelegant translate
            c1,c2,c3,c4,c5,c6,c7,c8,c9 = map(lambda di: (add_t(c0, di)),
                    (d1,d2,d3,d4,d5,d6,d7,d8,d9))
            if virtual:
                assert cube not in self.config

            # We use c1 as our pivot (fine since such a pivot must exist), so
            # Assume: c1 in config
            if not self.has_cube(c1):
                continue
            # Assume: c3 not in config; otherwise, c3 would be the pivot
            if self.has_cube(c3):
                continue
            # c5 not in config; otherwise cannot rotate
            if self.has_cube(c5):
                continue

            # Transfer Move
            if self.has_cube(c4):
                #if not virtual:
                assert not self.has_cube(c8) and not self.has_cube(c9)
                return (c5, c4)

            # Linear Move
            elif self.has_cube(c2):
                #if not virtual:
                assert not self.has_cube(c4) and not self.has_cube(c5)
                return (c3, c2)

            # Transfer Move
            elif self.has_cube(c6) or self.has_cube(c7) :
                assert not self.has_cube(c4) and not self.has_cube(c5)
                return (c3, c1)

            # Corner Move
            else:
                #if not virtual:
                assert (not self.has_cube(c4) and not self.has_cube(c5) and
                            not self.has_cube(c6) and not self.has_cube(c7))
                return (c2, c1)

        return (c0, ())

    def find_path(self, frompos, topos):
        # finds the shortest path from frompos to topos using BFS
        # returns the path in backwards order
        
        # BFS search
        print "from " + str(frompos) + " to " + str(topos)
        parents = {frompos: 0}
        nextcheck = [frompos]
        axesdict = self.search_dir()
        
        while nextcheck :
            nextpos = nextcheck.pop(0)

            if self.dim == 2 :
                rotaxis = set([(0,0,1),(0,0,-1)])
            else :
                rotaxis = set()
                # find neighbors
                neigh = self.find_neighbors(nextpos, False)

                # find axes of rotation
                for n in neigh :
                    neighdir = sub_t(n.pos, nextpos)
                    rotaxis.update(axesdict[neighdir])
                        
            # for each axis, find the new position
            for ra in rotaxis :
                c, _ = self.rotate(nextpos, ra, virtual=True)
                if c in parents :
                    continue
                parents[c] = (nextpos,ra)
                nextcheck.append(c)
                if c == topos :
                    break
            if topos in nextcheck :
                break

        # backtrack the path
        nextpos = topos
        path = []
        while nextpos != frompos :
            path.append(parents[nextpos])
            nextpos = parents[nextpos][0]

        #print path
        return path
            

    # CONFIGURATION ANALYSIS
    def find_extreme_cube(self, Mz = None, zDirection="+"):
        assert(zDirection in ["+", "-"])
        if len(self.config)==0:
            return None
        if self.dim > 2 :
            if Mz == None:
                if zDirection=="+":
                    Mz = max([c[2] for c in self.config])
                elif zDirection=="-":
                    Mz = min([c[2] for c in self.config])
            Mx = max([c[0] for c in self.config if c[2] == Mz])
            My = max([c[1] for c in self.config if c[2] == Mz and c[0] == Mx])

            return Cube((Mx, My, Mz))
        else:
            Mx = max([c[0] for c in self.config])
            My = max([c[1] for c in self.config if c[0] == Mx])

            return Cube((Mx, My))

     
    def slice_deconstruction_order(self):
        ''' 
        Returns a list of the cubes in the slice containing self.slice_root,
        in order of deconstruction.
        '''
        z = self.slice_root[2]
        slice_set = self.find_component(self.slice_root, is2D=True)
        assert(self.extreme_of_slice in slice_set)
        slice = Configuration(slice_set.copy(), self.ispar, self.dodraw, self.dosave)
        slice.slice_root = self.slice_root
        slice.extreme_of_slice = self.extreme_of_slice

        removed = []
        #Calculate N_set, pick next_cube from it

        while(len(slice.config)>0):
            slice.nextcube_info = None #have to reset so classify_slice_cubes will recalculate it
            slice.classify_slice_cubes(z) 
            if (len(slice.N_set)==0): #if N_set is empty
                # slice is a chain; choose extreme_of_slice
                removed.append(slice.extreme_of_slice)
                slice.remove(slice.extreme_of_slice)
                slice.extreme_of_slice = slice.find_extreme_cube()
            else:
                next_cube = slice.nextcube_info[0][0]
                assert(isinstance(next_cube, Cube))
                #print(next_cube)
                assert(next_cube in slice.config)
                #remove next_cube
                removed.append(next_cube) 
                slice.remove(next_cube)

        return removed

    def classify_slice_cubes(self, z = 0): #formerly classify_configuration
        '''
        Sets self.nextcube_info appropriately for the slice of self.slice_root 
        (which should be in the same slice as self.extreme_of_slice),
        unless the slice is already the chain from self.slice_root to self.extreme_of_slice
        '''
        # calculate O_set
        self.O_set = []
        expos = self.extreme_of_slice

        if self.dim > 2:
            virtual_cube = (expos[0]+1, expos[1], z)
        else:
            virtual_cube = (expos[0]+len(self.T_set)+1, expos[1])
        starting_location = virtual_cube
        virtual_cube, _ = self.rotate(virtual_cube, (0,0,-1), virtual=True)
        
        while virtual_cube != starting_location:
            assert not self.has_cube(virtual_cube)
            for neighbor in self.find_neighbors(virtual_cube,True):
                if neighbor not in self.O_set:
                    self.O_set.append(neighbor)
            virtual_cube, _ = self.rotate(virtual_cube, (0,0,-1), virtual=True)

        # FORNOW: convention, shows up in step_configuration
        # Basically, we don't want to look in the tail or at self.last_cube
        # for cubes to move
        if self.last_cube in self.O_set:
            self.O_set.remove(self.extreme_of_slice)
        for cube_t in self.T_set:
            if cube_t in self.O_set:
                self.O_set.remove(cube_t)

        # FORNOW: reverse list for algorithm
        self.O_set.reverse()

        # update M_set
        self.M_set = []
        for cube in self.O_set:
            if cube == self.slice_root or cube == self.extreme_of_slice :
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
                connectivity_condition = self.in_same_slice(cube_a, cube_b)
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

                if not self.nextcube_info:
                    # compute checkpoint
                    if self.ispar:
                        chk = cube.pos
                        for _ in xrange(Configuration.BUFF+3):
                            newchk, _ = self.rotate(chk, cube.dir)
                            if newchk[1] == self.extreme_of_slice[1]:
                                diff0 = newchk[0]-self.extreme_of_slice[0]-len(self.T_set)
                                if diff0 > 0:
                                    if diff0 <= len(self.rotating_cubes):
                                        chk = (newchk[0], chk[1])
                                    break
                            chk = newchk
                    else:
                        if self.dim == 2 :
                            chk = (self.extreme_of_slice[0]+len(self.T_set)+len(self.rotating_cubes)+1, self.extreme_of_slice[1])
                        else :
                            chk = (self.extreme_of_slice[0]+1, self.extreme_of_slice[1])

                    if self.dim > 2 :
                        chk = (chk[0], chk[1], z)
                    #print "NEXT NC:", cube
                    #print "NEXT CHECKPOINT:", chk
                    self.nextcube_info = [(cube,chk)]
            else:
                search_results = self.P_search(cube)
                P = search_results
                if search_results != None and not self.slice_root in P :
                    self.P_set.append(P)
                    if not self.nextcube_info:
                        # compute checkpoint
                        if self.ispar:
                            endTail = False
                            chk = cube.pos
                            for _ in xrange(Configuration.BUFF+3):
                                newchk, _ = self.rotate(chk, cube.dir)
                                if newchk[1] == self.extreme_of_slice[1]:
                                    diff0 = newchk[0]-self.extreme_of_slice[0]-len(self.T_set)
                                    if diff0 > 0:
                                        if diff0 <= len(self.rotating_cubes):
                                            chk = (newchk[0], chk[1])
                                        break
                                chk = newchk
                        else:
                            if self.dim == 2 :
                                chk = (self.extreme_of_slice[0]+len(self.T_set)+len(self.rotating_cubes)+1, self.extreme_of_slice[1])
                                endTail = True
                            else :
                                chk = (self.extreme_of_slice[0]+1, self.extreme_of_slice[1])
                                endTail = False

                        if self.dim > 2 :
                            chk = (chk[0], chk[1], z)
                        #print "NEXT P:", cube, self.extreme_of_slice
                        #print "NEXT CHECKPOINT:", chk
                        if self.dim > 2 :
                            self.nextcube_info = [(P[0],chk)]
                            #self.nextcube_info = [(P[i],add_t(chk,(i if endTail else 0,0,0))) for i in range(len(P))]
                        else :
                            self.nextcube_info = [(P[i],add_t(chk,(i if endTail else 0,0))) for i in range(len(P))]
        
    def check_cube_count(self):
        print("self.config_size: "+str(self.config_size))
        print("len(self.config): "+str(len(self.config)))
        print("len(self.rotating_cubes): "+str(len(self.rotating_cubes)))

        # check that we haven't done anything crazy
        assert len(self.config)+len(self.rotating_cubes) == self.config_size
        
    
    def find_extreme_slice(self, V_S, G_S):
        '''
        Implements slice and root selection.
        Returns a tuple containing:
            The selected slice, with its slice_root cube selected
            The graph index of the selected slice

        The approach is to select a globally extreme slice
        (excluding the one containing the last cube until
        that's the last slice left), since globally extreme 
        slices are on the outer boundary and are locally extreme.    
        '''
        comp = None

        zMax = max([c[2] for c in self.config])
        zMin = min([c[2] for c in self.config])

        print("Slices remaining: " + str([str(cid) for cid in V_S.keys()]))
        if len(V_S) == 1 :
            for cid in V_S.keys() : break
            comp = V_S[cid]
            comp.slice_root = self.last_cube
            comp.extreme_of_slice = self.last_cube
        else : 
            #find a globally extreme slice not containing self.last_cube
            for cid in V_S.keys():
                zHere = next(iter(V_S[cid].config))[2]
                if (zHere==zMin or zHere==zMax) and (not self.last_cube in V_S[cid].config):
                    comp = V_S[cid]
                    break
                '''
                if self.last_cube in V_S[cid].config:
                    continue
                elif len(G_S[cid]) == 1 :
                    # look for a slice with degree 1
                    comp = V_S[cid]
                    neighdir = G_S[cid][0][1] # direction of the slice
                    break
                else :
                    # or an extreme slice that does not disconnect the configuration
                    isextreme = True
                    neighdir = G_S[cid][0][1] # direction of neighbors
                    if any (G_S[cid][i][1] != neighdir for i in range(len(G_S[cid]))):
                        # not extreme
                        continue
                    
                    # test connectivity
                    ctemp = self.config.copy()
                    ctemp.difference_update(V_S[cid].config)

                    ctemp = Configuration(ctemp, self.ispar, self.dodraw, self.dosave)

                    if ctemp.is_connected() == None :
                        comp = V_S[cid]
                        break
                '''
            assert(comp != None) 

            ''' select root cube of comp: must '''
            without_slice = Configuration(self.config.copy(), self.ispar, self.dodraw, self.dosave)
            without_slice.remove(V_S[cid])
            for c in comp.config:
                up = (c[0],c[1],c[2]+1)
                down = (c[0],c[1],c[2]-1)
                ''' if c has a neighbor above or below it, 
                and that neighbor is connected to the last cube not through this slice,
                then the c is a suitable slice root'''
                if self.has_cube(up):
                    if without_slice.pair_connected(up, self.last_cube):
                        comp.slice_root = c
                    break
                if self.has_cube(down):
                    if without_slice.pair_connected(down, self.last_cube):
                        comp.slice_root = c
                    break

            comp.extreme_of_slice = comp.find_extreme_cube() 

        #print("Selected slice: " + str(comp))    
        return (comp, cid)
        

    def get_block_graph(self, G_S) :
        if not G_S :
            return G_S, G_S

        print "not implemented"
        return None
        
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
                neigh = [(i, j) for i in range(ncomp) for j in [-1,1] if
                         [ c for c in V_S[i].config if (Cz.has_cube((c[0],c[1],c[2]-j))) ] ]
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
    
    def remove(self, other):
        if isinstance(other, Cube):
            if other in self.config:
                self.config.remove(other)
        elif isinstance(other, tuple) and len(other)==3:
            self.config.remove(Cube(other))
        elif isinstance(other, set):
            self.config.difference_update(other)
        elif isinstance(other, Configuration):
            self.config.difference_update(other.config)
        else:
            print("unrecognized type for other in Configuration.remove(other)")
            assert(False)
    
    def branch_to_remove(self, next_cube):
        ''' Return the branch we need to remove (recurse flatten on)
        before removing next_cube (or None if we can remove 
        next_cube next), as a Configuration with branch.last_cube 
        set to the ground module of next_cube
        
        Pause condition: next_cube has a neighbor n in a branch, 
        AND the slice containing n is the only grounding slice of the 
        branch adjacent to what remains of the current slice 
        '''
        z_next = next_cube[2]
        above_next = (next_cube[0], next_cube[1], z_next+1)
        below_next = (next_cube[0], next_cube[1], z_next-1)
        assert(not (self.has_cube(above_next) and self.has_cube(below_next))) #because then then the current slice wouldn't be locally extreme
        if self.has_cube(above_next):
            neighbor_pos = above_next
            z_neighbor = z_next+1
        elif self.has_cube(below_next):
            neighbor_pos = below_next
            z_neighbor = z_next-1
        else: #if self.has_cube has no neighbor above or below, it's safe to remove
            return None
        
        # HACKY AND INEFFICIENT, at some point should rewrite using slice graph
        neighbor_cube = Cube(neighbor_pos)
        neighbor_slice = self.find_component(neighbor_cube, is2D=True)
        next_slice = self.find_component(next_cube, is2D=True)
        temp = Configuration(self.config.copy(), self.ispar, self.dodraw, self.dosave)
        # To check if neighbor_slice is the only grounding slice of a branch,
        # we can remove every module from next_slice adjacent to neighbor_slice,
        # then check if neighbor is connected to self.last_cube 
        for g in neighbor_slice: #called g because it might be a ground
            b = Cube((g[0],g[1],z_next)) #might be a base
            #remove the cube in neighbor_slice above or below
            if b in next_slice:
                temp.remove(b)
        if temp.pair_connected(neighbor_cube, self.last_cube):
            return None
        else:
            without_next_slice = Configuration(self.config.copy(), self.ispar, self.dodraw, self.dosave)
            without_next_slice.remove(next_slice)
            branch_set = without_next_slice.find_component(neighbor_cube, is2D=False)
            branch = Configuration(branch_set.copy(), self.ispar, self.dodraw, self.dosave)
            branch.last_cube = neighbor_cube
            return branch

        '''
        # Test if neighbor_cube is in a branch:
        next_slice = self.find_component(next_cube, is2D=True)
        without_next_slice = Configuration(self.config.copy(), self.ispar, self.dodraw, self.dosave)
        without_next_slice.remove(next_slice)
        neighbor_component = without_next_slice.find_component(neighbor_cube, is2D=False)
        if self.last_cube in neighbor_component: 
            return None #because neighbor_cube is not in a branch

        # Now we know neighbor_component is a branch, so we need to check if neighbor_cube is in its only grounding slice.
        # If neighbor_component is only one slice (neighbor_slice), this must be the only grounding slice

        # Otherwise if neighbor_component has multiple slices, neighbor_cube is its only grounding slice iff 
        neighbor_slice = self.find_component(neighbor_cube, is2D=True)
        global_without_neighbor_slice = Configuration(self.config.copy(), self.ispar, self.dodraw, self.dosave)
        global_without_neighbor_slice.remove(neighbor_slice)
        '''

        
        
        
                  



        
        


    
    def slice_neighbor_isbranch_dict(self, slice_id, V_S, G_S):
        '''
        Return a dictionary where:
            the keys are indices of slices adjacent to the slice indicated by this_slice_id
            the values are True if the adjacent slice is in a branch, False otherwise
        '''
        assert(slice_id in V_S.keys())

        ''' A branch of a Slice is a subconfiguration of 
        Configuration-Slice not connected to the last slice
        except through Slice '''
        without_slice = Configuration(self.config.copy(), self.ispar, self.dodraw, self.dosave)
        without_slice.remove(V_S[slice_id])

        neighbor_dict = {}
        for nid in G_S[slice_id]:
            neighborCube = next(iter(V_S[nid].config))
            is_connected_to_last = self.last_cube in without_slice.find_component(neighborCube, is2D=False)
            neighbor_dict[nid] = not is_connected_to_last
        return neighbor_dict

        


        '''
        # Identify the id of the slice condaining the last slice to be removed
        last_slice_id = None
        for cid in V_S.keys():
            if self.last_cube in V_S[cid].config:
                last_slice_id = cid
                break        
        assert(not last_slice_id == None) #if self.last_cube isn't in any slices, something is very wrong
        assert(last_slice_id != slice_id) #the last slice shouldn't be selected until it's the last one left


        remaining = Configuration(self.config.copy(), self.ispar, self.dodraw, self.dosave)
        remaining.remove(slice)
        
        branches = {}
        last_component = remaining.find_component(self.last_cube, is2D=False).copy()
        remaining.remove(last_component)
        while len(remaining.config)>0: #while remaining isn't empty
            cube = next(iter(remaining.config))
            component = remaining.find_component(cube, is2D=False)
        '''
            


            




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

            neighbors = [Cube((x+i, y+j, z+k)) for i in [-1,0,1] for j in [-1,0,1] for k in krange if
                self.has_cube((x+i, y+j, z+k)) and abs(i) + abs(j) + abs(k) == 1]

            clockwise_2box_coords = [((x+1,y,z),(x,y+1,z),(x+1,y+1,z)),
                                     ((x,y+1,z),(x-1,y,z),(x-1,y+1,z)),
                                     ((x-1,y,z),(x,y-1,z),(x-1,y-1,z)),
                                     ((x,y-1,z),(x+1,y,z),(x+1,y-1,z))]
        else:
            neighbors = [Cube((x+i, y+j)) for i in [-1,0,1] for j in [-1,0,1] if
                self.has_cube((x+i, y+j)) and abs(i) + abs(j) == 1]

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

    def in_same_slice(self, cube_a, cube_b):
        '''
        return True iff cube_a and cube_b are in the same slice
        '''
        return cube_b in self.find_component(cube_a, True)
    
    def pair_connected(self, cube_a, cube_b):
        '''
        return True iff there exists a path between cube_a
        and cube_b in configuration (in 3D)
        '''
        return cube_b in self.find_component(cube_a, False)

    def has_cube(self, pos):
        return Cube(pos) in self.config

    
    # VISUALIZATION AND PRINTING
    def init_draw(self):
        self.drawing = ConfigDraw(self.dim, self.dosave, self.save_prefix)

    def show(self):
        self.init_draw()

        self.drawing.draw_configuration(self.config,[],[],[],[],[],[],self.dosave)

        while not self.drawing.check_draw_close() :
            self.drawing.draw_configuration(self.config,[],[],[],[],[],[],False)

        self.close_draw()

    def close_draw(self):
        if not self.drawing == None:
            self.drawing.close()
    
    def __str__(self):
        return str( [ str(a) for a in self.config ] )

    def to_tuple(self):
        return [c.pos for c in self.config]

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

def slice_ids_in(subconfig, V_S):
    ids = []
    for slice_id, slice in V_S.items():
        cube_in_slice = next(iter(slice.config))
        if cube_in_slice in subconfig:
            ids.append(slice_id)
    return ids

def remove_slice(V_S, G_S, slice_id):
    # remove slice from slice graph V_S, G_S
    for i in G_S :
        todelete = [c for c in G_S[i] if c[0]==slice_id]
        for d in todelete :
            G_S[i].remove(d)
    G_S.pop(slice_id)
    V_S.pop(slice_id)
    return (V_S, G_S)

def main():
    testname = 'stalagmite_and_stalactite'
    #c = Configuration(testname+'.config', False, False, True, testname)
    #c = Configuration('inadmissible2D_rule1.config', False, True)
    #c = Configuration('bad.config', False, True)
    #c = Configuration('bug.config', True, False, True, 'bug_par')
    #c = Configuration('halfbug.config', True, False, True, 'halfbug_par')
    #c = Configuration('5.config', True, True, False, '')
    
    c = Configuration(testname+'.csv', ispar=False, dodraw=False, dosave=True, saveprefix=testname)
    #c.show()
    c.flatten()
    #c2 = Configuration([(-ctemp[1],-ctemp[0]) for ctemp in c.config],
    #                   True, False, True, '5_par')
    #print c.min, c.max
    #c.flatten2D()
    #c2 = Configuration([(0,0,0),(1,0,0),(2,0,0),(3,0,0),
    #                    (0,0,1),(3,0,1),
    #                    (0,0,2),(3,0,2),
    #                    (0,0,3),(1,0,3),(2,0,3),(3,0,3)],
    #                    False, False, True, '3Dsquare')
    #c2 = Configuration([(ctemp[0],ctemp[1]+i,ctemp[2]) for ctemp in c2.config for i in range(3)],
    #                   False, False, True, '3Dsquare2')
    #print c2.find_path((4,1,1),(0,0,-1))
    #c.show()
    #c2.flatten()

    #c3 = [(4, 3, 4), (1, 4, 4), (2, 2, 4), (7, 2, 3), (8, 0, 4), (9, 4, 1), (9, 2, 4), (8, 0, 3), (8, 3, 3), (0, 3, 4), (8, 0, 2), (13, 4, 1), (5, 2, 3), (11, 6, 1), (8, 3, 4), (7, 4, 3), (9, 1, 3), (7, 4, 4), (9, 1, 2), (9, 1, 5), (10, 7, 0), (9, 1, 4), (10, 7, 1), (12, 7, 1), (9, 4, 4), (13, 5, 1), (13, 2, 1), (3, 4, 4), (7, 3, 3), (3, 4, 6), (1, 3, 4), (3, 4, 5), (2, 3, 4), (1, 3, 3), (6, 3, 3), (8, 2, 3), (10, 2, 1), (5, 3, 4), (6, 2, 3), (11, 7, 1), (0, 4, 4), (6, 4, 4), (8, 2, 4), (11, 8, 1), (9, 2, 1), (11, 2, 1), (9, 2, 2), (10, 6, 1), (12, 2, 1), (10, 5, 1), (12, 6, 1), (10, 4, 1), (3, 3, 5), (14, 6, 1), (14, 5, 1), (6, 4, 3), (3, 3, 4), (2, 4, 5), (13, 3, 1), (5, 4, 3), (2, 4, 4), (0, 3, 3), (3, 3, 6), (10, 8, 1), (10, 8, 0), (9, 5, 1), (9, 3, 4), (13, 6, 1), (9, 0, 2), (4, 5, 4), (9, 3, 3), (15, 6, 1), (9, 0, 3), (5, 4, 4), (9, 3, 2), (4, 4, 6), (8, 4, 4), (9, 3, 1), (8, 1, 3), (4, 4, 5), (9, 2, 3), (5, 3, 3), (8, 1, 4), (4, 4, 4), (5, 2, 4), (10, 3, 1), (4, 4, 3), (9, 0, 4), (14, 4, 1)]
    #c3 = Configuration(c3, False, False, True, 'c3')

    #c4 = [(0,0,0),(0,1,0),(0,2,0),(0,3,0),(1,3,0),(2,3,0),(3,3,0),(3,2,0),(3,1,0),(3,0,0),(2,0,0),(1,0,0),
    #      (4,3,0),(5,3,0),(6,3,0),(6,2,0),(6,1,0),(6,0,0),(5,0,0),(4,0,0),
    #      (6,0,1),(5,0,1),(4,0,1),(3,0,1),(6,-1,1),(5,-1,1),(4,-1,1),(3,-1,1),
    #      (3,3,1),(2,3,1),(1,3,1),(0,3,1),(3,4,1),(2,4,1),(1,4,1),(0,4,1),
    #      (3,3,2),(2,3,2),(1,3,2),(0,3,2),(3,4,2),(2,4,2),(1,4,2),(0,4,2)]
    #c4 = Configuration([(c[1],c[0],c[2]) for c in c4], False, False, True, 'c4')
    
    #c = [(0,0,0),(1,0,0),(2,0,0),(3,0,0),
    #     (0,1,0),(3,1,0),
    #     (0,2,0),(3,2,0),
    #     (0,3,0),(1,3,0),(2,3,0),(3,3,0),
    #     (3,3,1)]
    #c = Configuration(c, False, True)
    #c4.show()
    #c2.flatten()

    print "done"

if __name__ == '__main__': main()
