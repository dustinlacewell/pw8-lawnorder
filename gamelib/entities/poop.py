import random
rand = random.Random()

import pygame

from gamelib import animation, soundsystem, states
from gamelib.constants import *
from gamelib.geometry import Vec2D
from gamelib.data import load_image

from lawnsegment import LawnSegment
from flyobj import FlyObj


class Poop(FlyObj):

    class StateStill(FlyObj.StateStill):
        def enter(self_, self):
            self.pickupable = True
            self.spr = self.ground_spr

        def update(_self, self,  dt, t):
            self.lifetime -= dt
            if self.lifetime <= 0:
                states.TheStateManager.cur_state.remove_entity(self)
            self.rect.center = self.pos

    class StateThrown(FlyObj.StateThrown):

        def collision_response(_self, self, other):
            if isinstance(other, LawnSegment):
                other.hurt(10)

    _state_still = StateStill()
    _state_thrown = StateThrown()

    def __init__(self, pos):
        super(FlyObj, self).__init__(pos, self._state_thrown)
        s= rand.randint(20, 40)
        img = load_image('poop_anim.png')
        img = pygame.transform.smoothscale(img, (s, s))
        self.spr = animation.TimedAnimation(self.pos, img, 2, 3, 'loop')
        self.rect = pygame.Rect(self.spr.rect)
        self.weight = s/40. + 1.5
        self.size = s
        self.pickupable = False
        self.accel.y = FALLSPEED
        self.accel.x = 0
        self.vel = Vec2D(0, 0)
        self.lifetime = POOPLIFETIME # 10 sec
        img = load_image('poopground.png')
        img = pygame.transform.scale(img, (s, s))
        self.ground_spr = animation.FrameAnimation(self.pos, img)
