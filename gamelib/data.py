'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''

import os
import pygame
from pygame.image import load as _load

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, os.pardir, 'data'))

def filepath(filename):
    '''Determine the path to a file in the data directory.
    '''
    return os.path.join(data_dir, filename)

def load(filename, mode='rb'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    return open(os.path.join(data_dir, filename), mode)

def load_image(filename, colorkey=None, optimize=1):
    img = _load(filepath(filename))
    if colorkey:
        img.set_colorkey(colorkey)
    if optimize:
        if img.get_alpha():
            return img.convert_alpha()
        else:
            return img.convert()

# This is a pretty thin wrapper, but I figured it's nice for consistency,
# so that both images and sounds are loaded the same way.
# -Pekuja
def load_sound(filename):
    return pygame.mixer.Sound(filepath(os.path.join('sfx',filename)))

pygame.image.load = load_image

