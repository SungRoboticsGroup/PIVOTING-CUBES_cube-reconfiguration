# ConfigDraw class
#
# draws a configuration of cubes
# 3D graphics taken from petercollingridge tutorial
#
# originally: 7/15/2014 by James Bern
# last modified: 9/4/2014 by Cynthia Sung

# for drawing
import pygame
from pygame.locals import *
from vector_op import *
import os
import math

class ConfigDraw:
    """ConfigDraw class"""

    key_to_function = {
        pygame.K_LEFT:   (lambda x: x.rotateAll(1,  0.1)),
        pygame.K_RIGHT:  (lambda x: x.rotateAll(1, -0.1)),
        pygame.K_DOWN:   (lambda x: x.rotateAll(0,  0.1)),
        pygame.K_UP:     (lambda x: x.rotateAll(0, -0.1))
        }


    # INITIALIZATION
    def __init__(self, dim, dosave=False, prefix='', light=True):
        self.dim = dim
        
        self.clock = None
        self.screen = None
        self.dump_png = dosave
        self.prefix = prefix
        
        self.light_variant = light
        
        self.init_pygame()

        self.cubeVerts3D = [[[-.5,-.5,-.5],[-.5, .5,-.5],[ .5, .5,-.5],[ .5,-.5,-.5]],
                            [[-.5,-.5,-.5],[-.5, .5,-.5],[-.5, .5, .5],[-.5,-.5, .5]],
                            [[-.5,-.5,-.5],[ .5,-.5,-.5],[ .5,-.5, .5],[-.5,-.5, .5]],
                            [[ .5,-.5,-.5],[ .5, .5,-.5],[ .5, .5, .5],[ .5,-.5, .5]],
                            [[-.5, .5,-.5],[ .5, .5,-.5],[ .5, .5, .5],[-.5, .5, .5]],
                            [[-.5,-.5, .5],[-.5, .5, .5],[ .5, .5, .5],[ .5,-.5, .5]]]
        self.unit = [[1,0,0],[0,-1,0],[0, 0, -1]];
        self.rotateAll(0, .4)
        self.rotateAll(1, .4)
        
        self.c = 8.

        self.frame_i = 0;

    def init_pygame(self):
        # os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(2500,100)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(25,25)
        pygame.init()
        pygame.display.set_caption("2D Visualizer")
        # screen = pygame.display.set_mode([135*2,25*2])
        self.screen = pygame.display.set_mode([400,200])
        self.clock = pygame.time.Clock()

    # DRAWING
    def draw_configuration(self, config, O_set=[], M_set=[], N_set=[], T_set=[], rotating_cubes=[], root = [], dosave = None):
        f = 1
        if self.light_variant:
            f = 2

        DEFAULT = (153,102,204)
        BOUNDARY = (0,191,255)
        EXTREME = (255/f,159/f,0/f)
        MOBILE = (133,187,101)
        MOBILE_NON_SPLITTING = (0,255,0)
        ROTATING = (255/f,85/f,163/f)
        WHITE = (255,255,255)
        BLACK = (0,0,0)

        if self.light_variant:
            self.screen.fill(WHITE)
        else:
            self.screen.fill(BLACK)

        extremeX = max([c[0] for c in config])

        # NOTE: precendence order
        for cube in config.union(set(rotating_cubes)):
            color = DEFAULT

            if cube in N_set:
                color = MOBILE_NON_SPLITTING
            elif cube in M_set:
                color = MOBILE
            elif cube in O_set:
                color = BOUNDARY

            if cube in rotating_cubes:
                color = ROTATING
            elif cube in T_set:
                color = EXTREME

            if cube in root:
                color = EXTREME

            if self.dim == 2:
                self.draw_cube(cube, color, extremeX)
            else:
                self.draw_cube3D(cube, color)

        pygame.display.flip()

        if (dosave==None and self.dump_png) or dosave==True:
            pad = '0'*(4-len(str(self.frame_i)))
            self.save('./images/' + self.prefix + 'frame' + pad + str(self.frame_i) + '.png')
            self.frame_i = self.frame_i+1

    
    def draw_cube(self, cube, color, extremeX):
        N = 1
        (x, y) = (cube[0]+N, cube[1]+N)
        if self.dim > 2 :
            x = x + (extremeX+1)*cube[2]
        pygame.draw.rect(self.screen, color, [x*self.c, self.screen.get_size()[1]-self.c-y*self.c, self.c, self.c])

    def draw_cube3D(self, cube, color):
        N = 4
        x = cube[0]*self.unit[0][0]+cube[1]*self.unit[1][0]+cube[2]*self.unit[2][0] + N
        y = cube[0]*self.unit[0][1]+cube[1]*self.unit[1][1]+cube[2]*self.unit[2][1]
        y = self.screen.get_size()[1]/self.c + y - N
        for thisverts in self.cubeVerts3D :
            pygame.draw.polygon(self.screen, color,
                                [((x+v[0])*self.c,(y+v[1])*self.c) for v in thisverts],
                                0)
            pygame.draw.polygon(self.screen, (0,0,0),
                                [((x+v[0])*self.c,(y+v[1])*self.c) for v in thisverts],
                                1)

    def wait(self, timer):
        pygame.time.wait(timer)

    # SAVING
    def save(self, fname):
        pygame.image.save(pygame.display.get_surface(), fname)

    # CLOSING
    def close(self):
        pygame.quit()

    def check_draw_close(self):
        # key handling
        for event in pygame.event.get():
            if (event.type == QUIT or
                (event.type == KEYDOWN and event.key == K_q)):
                return True
            elif event.type == pygame.KEYDOWN:
                    if event.key in ConfigDraw.key_to_function:
                        ConfigDraw.key_to_function[event.key](self)

    # 3D stuff
    def rotateAll(self, axis, radians):
        """ Rotate all wireframe about their centre, along a given axis by a given angle. """

        idx1 = (axis+1)%3
        idx2 = (axis+2)%3

        for i in range(len(self.cubeVerts3D)) :
            for j in range(4) :
                v = self.cubeVerts3D[i][j]
                
                v1 = v[idx1]
                v2 = v[idx2]
                d = math.hypot(v1, v2)
                theta = math.atan2(v1, v2) + radians

                self.cubeVerts3D[i][j][idx1] = d * math.sin(theta)
                self.cubeVerts3D[i][j][idx2] = d * math.cos(theta)

        for i in range(3) :
            v1 = self.unit[i][idx1]
            v2 = self.unit[i][idx2]
            d = math.hypot(v1, v2)
            theta = math.atan2(v1, v2) + radians

            self.unit[i][idx1] = d * math.sin(theta)
            self.unit[i][idx2] = d * math.cos(theta)        

