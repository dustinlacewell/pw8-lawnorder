import random
rand = random.Random()
randint = random.randint
choice = random.choice

import pygame
from pygame.locals import *
from gamelib import states

from gamelib.constants import * 
from gamelib import animation
from gamelib.geometry import Vec2D, Entity, sign
from gamelib.utility import have_luck
from gamelib.data import load_image

from gamelib.entities.statemachine import StateMachine

from gamelib import soundsystem

#-------------------------------------------------------------------------------

class FlyObj(StateMachine):
    class StateThrown(StateMachine.State):
        def enter(_self, self):
            self.accel = Vec2D(0, FALLSPEED) # because 0,0 is at the top
            self.pickupable = False
        def update(_self, self, dt, t, *args, **kwargs):
            if self.pos.x > FENCELEFT and self.pos.x < FENCERIGHT:
                if self.pos.y > FENCETOP:
                    self.vel.x *= FENCEBOUNCE # bounce from fence
                    self.pos.x += self.vel.x * FENCESPEED
            super(StateMachine, self).update(dt, t)
            ground_limit = GROUNDLIMIT - (self.size / 2.0)
            if self.pos.y >= ground_limit:
                self.pos.y = ground_limit
                self.vel.y *= GROUNDBOUNCEY
                self.vel.x *= GROUNDBOUNCEX
                self.change_state(self._state_still)
            # Constrain to screen width
            self.pos.x = max(0, min(SCREENWIDTH, self.pos.x))
            self.spr.update(dt, t)
            self.spr.rect.center = self.pos
            self.rect.center = self.pos

        def render(self_, self, screen, dt, t):
            self.spr.render(screen, dt, t)

    class StateHeld(StateMachine.State):
        def render(self_, self, screen, dt, t):
            self.spr.render(screen, dt, t)

        def update(self_, self, dt, t):
            self.spr.update(dt, t)
            self.rect.center = self.pos

    class StateStill(StateMachine.State):
        def enter(self_, self):
            self.pickupable = True

        def leave(self_, self):
            self.pickupable = False

        def render(self_, self, screen, dt, t):
            self.spr.render(screen, dt, t)

        def update(self_, self, dt, t):
            self.spr.update(dt, t)

    _state_still = StateStill()
    _state_held = StateHeld()
    _state_thrown = StateThrown()

    def __init__(self, pos):
        super(FlyObj, self).__init__(pos, self._state_thrown)
        s= rand.randint(10, 30)
        if s > 20:
            img = load_image('block.png')
        else:
            img = load_image('stone.png')
        
        self.spr = animation.FrameAnimation(self.pos, pygame.transform.smoothscale(img, (s, s)))
        self.rect = pygame.Rect(self.spr.rect)
        self.weight = s/40. + 1.5
        self.size = s

        self.pickupable = False

    def pickup(self):
        self.change_state(self._state_held)

    def throw(self):
        self.change_state(self._state_thrown)

    #def collision_response(self, other):
    #    pass
