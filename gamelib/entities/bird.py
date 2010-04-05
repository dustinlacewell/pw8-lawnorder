from flyobj import FlyObj
from statemachine import StateMachine
from lawnsegment import LawnSegment
from poop import Poop

from gamelib.geometry import Vec2D, sign
from gamelib.constants import *
from gamelib import animation
from gamelib.data import load_image
from gamelib.utility import have_luck
from gamelib import states, soundsystem

import gamelib
import random
import pygame
from random import randint

class Bird(FlyObj):#(StateMachine):
    CLIPDIST = 80
    SPAWNDIST = 10

    class StateIdle(StateMachine.State):

        def update(_self, self, dt, t, *args, **kwargs):
            if have_luck(0.5):
                if have_luck(0.5):
                    self.pos.values = Vec2D(-BIRDSPAWNDIST, random.randint(20, 300))
                    self.vel.x = BIRDSPEED
                else:
                    self.pos.values = Vec2D(SCREENWIDTH + BIRDSPAWNDIST, random.randint(20, 300))
                    self.vel.x = -BIRDSPEED
                self.change_state(self._state_fly)

    class StateFly(StateMachine.State):

        def enter(_self, self):
            if self.pos.y > 320:
                self.change_state(self._state_revive)

        def checkScreenClipping(_self, self):
            if self.pos.x < -BIRDCLIPDIST:
                self.vel.x *= -1.0
                self.pos.x += 10
                self.spr = self.spr_fly_r
            elif self.pos.x > SCREENWIDTH + BIRDCLIPDIST:
                self.vel.x *= -1.0
                self.pos.x -= 10
                self.spr = self.spr_fly_l

        def update(_self, self, dt, t, *args, **kwargs):
            super(StateMachine, self).update(dt, t)
            _self.checkScreenClipping(self)
            if self.pos.x > 10 and self.pos.x < SCREENWIDTH - 10:
                if have_luck(BIRDPOOPCHANCE) and (self.pos.x < FENCELEFT - 40 or self.pos.x > FENCERIGHT + 40):
                    self.change_state(self._state_poop)
                
                elif have_luck(BIRDTURNCHANCE):
                    self.vel.x *= -1
                    if sign(self.vel.x)>0:
                        self.spr = self.spr_fly_r
                    else:
                        self.spr = self.spr_fly_l
                    self.spr.play()
                if self.vel.y:
                    if have_luck(BIRDSTOPCHANCE) and self.pos.y < 350:
                        self.accel.y = 0
                        self.vel.y = 0
                    if self.pos.y < 0:
                        self.pos.y = 10
                        self.accel.y = 0
                        self.vel.y = 0
            self.spr.update(dt, t)
            self.rect.center = self.pos

        def render(_self, self, screen, dt, t, *args, **kwargs):
            self.spr.render(screen, dt, t)

        def collision_response(_self, self, other):
            
            if not isinstance(other, Bird):
                if isinstance(other, FlyObj) and self.pos.y < 350:
                    if gamelib.DEBUG: print "------------------", other.cur_state
                    if isinstance(other.cur_state, FlyObj.StateThrown):
                        if gamelib.DEBUG: print ")))))))))))))))))))) BIRD COLLISION ((((((((((((((((("
                        self.change_state(self._state_fall)
                        
    class StateRevive(StateMachine.State):
        def enter(_self, self):
            self.vel.y = BIRDRISESPEED
            self.vel.x = BIRDFLYSPEED * self.facing
            self.pos.y = 390
            self.accel.y = 0
            self.target = randint(40, 320)
            
            self.rect.center = self.pos
            if self.facing == 1:
                self.spr = self.spr_fly_r
            else:
                self.spr = self.spr_fly_l
            self.spr.update(0, 0)
            self.spr.play()
            
        def update(_self, self, dt, t, *args, **kwargs):
            if gamelib.DEBUG: print self.vel.y
            super(StateMachine, self).update(dt, t)
            self.spr.update(dt, t)
            self.rect.center = self.pos
            
            if self.pos.y < self.target:
                self.change_state(self._state_fly)
            
        def render(_self, self, screen, dt, t, *args, **kwargs):
            self.spr.render(screen, dt, t)
            
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
            
        def collision_response(_self, self, other):
            if isinstance(other, LawnSegment) and other not in self.collided:
                other.hurt(BIRDGRASSDAMAGE)
                self.collided.append(other)


    class StateFall(StateMachine.State):

        def enter(_self, self):
            self.spr.stop()
            self.rect.center = self.spr.rect.center
            self.vel.x = 0
            self.accel.y = FALLSPEED 

        def update(_self, self, dt, t, *args, **kwargs):
            super(StateMachine, self).update(dt, t)
            ground_limit = GROUNDLIMIT - (self.size / 2.0)
            if self.pos.y >= ground_limit:
                self.pos.y = ground_limit
                self.accel.y = 0
                self.vel.y = 0
                if have_luck(BIRDREVIVECHANCE):
                    self.change_state(self._state_revive)
                else:
                    # changed from _state_still.
                    # makes birds unthrowable again
                    self.change_state(self._state_idle)
            self.spr.update(dt, t)
            self.rect.center = self.pos
            
        def collision_response(_self, self, other):
            if isinstance(other, LawnSegment) and other not in self.collided:
                other.hurt(BIRDGRASSDAMAGE)
                self.collided.append(other)

        def render(_self, self, screen, dt, t, *args, **kwargs):
            self.spr.render(screen, dt, t)

    class StatePoop(StateMachine.State):
        def update(_self, self, dt, t, *args, **kwargs):
            super(StateMachine, self).update(dt, t)
            if not self.enter_time:
                self.enter_time = t
            duration = 500.0
            if t - self.enter_time > duration:
                self.change_state(self._state_fly)
            self.spr.rect.center = self.pos

        def render(_self, self, screen, dt, t, *args, **kwargs):
            self.spr.render(screen, dt, t)

        def enter(_self, self):
            states.TheStateManager.cur_state.add_entity(Poop(self.pos + Vec2D(-20, 0)*self.facing))
            self.spr = self.poop_spr
            self.spr.face = self.facing
            self.enter_time = None
            self.rect.center = self.spr.rect.center
            soundsystem.poop()

        def leave(_self, self):
            if self.facing == 1:
                self.spr = self.spr_fly_r
            else:
                self.spr = self.spr_fly_l

    _state_fly = StateFly(Vec2D(20, 0))
    _state_idle = StateIdle()
    _state_fall = StateFall()
    _state_poop = StatePoop()
    _state_revive = StateRevive()
    _state_thrown = StateThrown()

    def __init__(self, *args, **kwargs):
        super(Bird, self).__init__(Vec2D(
            random.randint(-BIRDSPAWNDIST,SCREENWIDTH + BIRDSPAWNDIST),
            random.randint(40, 320)))
        self.spr_fly_r = animation.TimedAnimation(self.pos, load_image('bird/right_fly.png'), 2, 3, 'loop')

        self.spr_fly_l = animation.TimedAnimation(self.pos, load_image('bird/left_fly.png'), 2, 3, 'loop')
        
        self.vel.y = 0
        self.accel.y = 0
        self.size = 20

        # What's this? We already have randomization of the position
        # at the top of this function.
        #self.pos.y = randint(40, 320)
        if randint(0, 1):
        #    self.pos.x = SCREENWIDTH + BIRDCLIPDIST
            self.vel.x = -BIRDFLYSPEED
            self.spr = self.spr_fly_l
        else:
        #    self.pos.x = -BIRDCLIPDIST
            self.vel.x = BIRDFLYSPEED
            self.spr = self.spr_fly_r
        
        self.rect = pygame.Rect(0, 0, self.spr.rect.w/2, self.spr.rect.h/2)
        self.rect.center = self.pos
        self.spr.update(0, 0)
        self.spr.play()
            
        self.collided = []
        
        self.change_state(self._state_fly)
        self.poop_spr = animation.TimedAnimation(self.pos,  load_image('bird/poop.png'), 1, 1)

