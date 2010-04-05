#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: testbgd.py 203 2009-04-28 18:53:52Z dr0iddr0id $'

import os
import pygame
from pygame.locals import *
import states
import data
import math

from entities import Player, FlyObj
import gradients

class Bgd(object):

    def __init__(self):
        self.screen_rect = states.TheStateManager.screen.get_rect()
        self.img = gradients.vertical(self.screen_rect.size, (0, 255, 255, 255), (80, 100, 135, 255))

    def update(self, dt, t, *args, **kwargs):
        s = math.cos(t/10000. * 2 * math.pi)
        s1 = int(round(127 * s))
        self.img = gradients.vertical(self.screen_rect.size,  (0, s1 + 128, s1 + 128, 255), (0, 0, 128, 255))

    def render(self, screen, dt, t, *args, **kwargs):
        screen.blit(self.img, (0, 0))


#-------------------------------------------------------------------------------
class TestBgd(states.State):

    def __init__(self, *args, **kwargs):
        super(TestBgd, self).__init__(*args, **kwargs)

    def on_init(self, *args, **kwargs):
        self.bgd = Bgd()

    def update(self, dt, t):
        self.bgd.update(dt, t)

    def render(self, screen, dt, t, *args, **kwargs):
        screen.fill((0, 0, 0))
        self.bgd.render(screen, dt, t)

