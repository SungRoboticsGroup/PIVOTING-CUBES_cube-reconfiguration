# ConfigDraw class
#
# draws a configuration of cubes
#
# originally: 7/15/2014 by James Bern
# last modified: 9/4/2014 by Cynthia Sung

# for drawing
import pygame
from pygame.locals import *
import os

class ConfigDraw:
    """ConfigDraw class"""

    # INITIALIZATION
    def __init__(self, dim, light=True):
        self.dim = dim
        
        self.clock = None
        self.screen = None
        self.light_variant = light
        
        self.init_pygame()

    def init_pygame(self):
        # os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(2500,100)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "{},{}".format(25,25)
        pygame.init()
        pygame.display.set_caption("2D Visualizer")
        # screen = pygame.display.set_mode([135*2,25*2])
        self.screen = pygame.display.set_mode([400,200])
        self.clock = pygame.time.Clock()

    # DRAWING
    def draw_configuration(self, config, O_set=[], M_set=[], N_set=[], T_set=[], rotating_cubes=[], root = []):
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
                self.draw_cube(cube, color)
            else:
                #print "WARNING: 3D cubes not implemented"
                self.draw_cube(cube, color)

        pygame.display.flip()

    
    def draw_cube(self, cube, color):
        c = 2*2*2
        N = 1
        (x, y) = (cube[0]+N, cube[1]+N)
        pygame.draw.rect(self.screen, color, [x*c, self.screen.get_size()[1]-c-y*c, c, c])

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
