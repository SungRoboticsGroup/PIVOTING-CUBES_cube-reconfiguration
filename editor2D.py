# Draw your own configuration to reconfigure
# Originally: James Bern 7/15
# Adapted from The Falling Rooms leveleditor.py by James Bern

# TODO: Verificiation

# Usage:
# -Left click adds
# -Right click deletes
# -c clears
# -q quits

import pygame
from pygame.locals import *
import sys
import pickle

WHITE = pygame.Color("white")
DARK_GREY = pygame.Color(20, 20, 20)
WHITE, DARK_GREY = DARK_GREY, WHITE

# n = num block lengths on one side of canvas
n = 64

# NOTE these variables only impact what the level editor looks like.
# b = block length in pixels
b = 10
s = n * b

# Room surface.
BACKGROUND = pygame.Surface((s, s))
BACKGROUND.fill(DARK_GREY)

# Block surfaces.
WHITE_RECT = pygame.Surface((b, b))
WHITE_RECT.fill(WHITE)

# VARIABLES
class State:
    dragging = False
    behavior = "adding" # / "removing"

class Config:
    def __init__(self):
        self.plan = {}
        for i in range(n):
            for j in range(n):
                self.plan[(i, j)] = False

    def add_remove(self, state, x_y_tup):
        if state == "adding":
            paint = True
        elif state == "removing":
            paint = False
        else:
            raise NotImplementedError

        # Determine square.
        x, y = x_y_tup
        i, j = (int(x / b), int(y / b))
        self.plan[(i, j)] = paint

def draw_config(config, screen):
    screen.blit(BACKGROUND, (0, 0))
    paint_squares = set([tup for tup in config.plan if config.plan[tup]])
    for square in paint_squares:
        i, j = square
        x, y = (i * b, j * b)
        screen.blit(WHITE_RECT, (x, y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((s, s))
    # New config...
    if len(sys.argv) == 1:
        config = Config()
    # Load up a saved config for further editing.
    else:
        assert len(sys.argv) == 2
        arg = sys.argv[1]
        try:
            g = open(arg, 'r')
            paint_squares = pickle.load(g)
            config = Config()
            for tup in paint_squares:
                config.plan[tup] = True
        except IOError:
            print "File not found, creating a blank config."
            config = Config()

    quit = False
    while not quit:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit = True

            # Disallow right clicking while left clicking and vice versa
            elif event.type == MOUSEBUTTONDOWN and not State.dragging:
                State.dragging = True
                if event.dict["button"] == 1:
                    State.behavior = "adding"
                else:
                    State.behavior = "removing"

            elif event.type == MOUSEBUTTONUP:
                State.dragging = False

            elif event.type == KEYDOWN:
                if event.key == K_c:
                    config = Config()
                elif event.key == K_q:
                    quit = True

        # Add or remove squares by dragging.
        if State.dragging:
            try:
                state = State.behavior
                x, y = ((event.dict["pos"][0], event.dict["pos"][1]))
                config.add_remove(state, (x, y))
            except:
                pass

        draw_config(config, screen)
        pygame.display.flip()

    # Save the config if desired
    text = None
    while text not in ['Y', 'y', 'N', 'n']:
        text = raw_input("Save config? (Y/N) >> ")
    if text in ['N', 'n']:
        return

    # ELSE save...
    name = raw_input("Input config file name. >> ")
    f = open("{}".format(name), 'w')
    pickle.dump(set([(tup[0],tup[1]) for tup in config.plan if config.plan[tup]]), f)
    f.close()
    return

if __name__ == "__main__": main()

