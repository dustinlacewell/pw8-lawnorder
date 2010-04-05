#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: bugs.py 388 2009-05-02 16:28:48Z dr0iddr0id $'

from random import randint
from random import normalvariate
from random import choice

import pygame

from flyobj import FlyObj
from lawnsegment import LawnSegment
from gamelib.geometry import Vec2D
from gamelib.geometry import sign
from gamelib.utility import have_luck
from gamelib import animation
from gamelib import data
import bird
from gamelib import soundsystem
from bird import Bird
from gamelib.constants import *
from gamelib import states

class LadyBug(FlyObj):

## [01:56]	ldlework: he appears on screen and doesn't do anything but walk around. 
## If you hit him with a FlyObj he flips over or something. then you can pick up 
## him and throw him. When he lands on some grass, he sticks there and eats the 
## grass, until you throw another fly obj at him.

    class StateFly(FlyObj.State):
#        def enter_takeoff(self_, self):
#            self.pos.y -= 15
#            self.rect.center = self.pos
#            if self.facing > 0:
#                self.vel.values = Vec2D(0, -0.08).rotated(randint(5, 80))
#            else:
#                self.vel.values = Vec2D(0, -0.08).rotated(randint(-80, 5))
#            self.spr = self.spr_fly
#            self.spr.face = self.facing
#
#        def update(_self, self, dt, t, *args, **kwargs):
#            self.pos += dt * self.vel
#            self.spr.face = self.facing
#            self.spr.update(dt, t)
#            self.vel.rotate(normalvariate(0, 15))
#            self.rect.center = self.pos
#            # if get off screen, die
#            if self.pos.x > SCREENWIDTH + 10 or self.pos.x < 0 -10 or self.pos.y < 0 -10:
#                self._count -= 1
#                states.TheStateManager.cur_state.remove_entity(self)


        def enter_takeoff(self_, self):
            self.pos.y -= 15
            self.rect.center = self.pos
            self.spr = self.spr_fly
            self.spr.face = self.facing
            speed = -0.08 + randint(0,20) * 0.001
            if self.pos.x > FENCEMIDDLE:
                self.vel.values = Vec2D(0, speed).rotated(randint(-5, 50))
            else:
                self.vel.values = Vec2D(0, speed).rotated(randint(-50, 5))
            self.steam = randint(500, 1000)

        def leave(self_, self):
            self.vel.y = 0

        def update(_self, self, dt, t, *args, **kwargs):
            # steam
            if self.steam < 0:
                self.steam = 0
                self.vel.y = 0
                self.accel.y = 0.0005
                #self.change_state(self._state_thrown)
            elif self.steam == 0:
                self.vel += dt * self.accel
            else:
                self.steam -= dt * 0.25
            self.vel.rotate(normalvariate(0, 4))
            self.pos += dt * self.vel
            self.spr.face = self.facing
            self.spr.update(dt, t)
            self.rect.center = self.pos
            # if get off screen, die
            if self.pos.x > SCREENWIDTH + 10 or self.pos.x < 0 -10 or self.pos.y < 0 -10:
                self._count -= 1
                states.TheStateManager.cur_state.remove_entity(self)

        def render(_self, self, screen, dt, t, *args, **kwargs):
            self.spr.render(screen, dt, t)

        def collision_response(_self, self, other):
            if isinstance(other, LawnSegment):
                self.change_state(self._state_idle)
            elif isinstance(other, FlyObj) and not isinstance(other, Bird) and \
                                                    not isinstance(other, LadyBug):
                self.change_state(self._state_thrown)

    class StateIdle(FlyObj.StateStill):
        def enter(self_, self):
            super(LadyBug.StateIdle, self_).enter(self)
            self.spr = self.spr_idle
            self.spr.face = self.facing
            self.spr.play()

        def update(self_, self, dt, t):
            if self.pos.y > GROUNDLIMIT - self.rect.h / 2:
                self.pos.y = GROUNDLIMIT - self.rect.h / 2
                self.vel.y = 0
            super(LadyBug.StateIdle, self_).update(self, dt, t)
            if have_luck(0.05):
                self.spr.play()
            x = randint(0, 100)
            if x < 30:
                self._state_fly.enter_takeoff(self)
                self.change_state(self._state_fly)
            elif x < 50:
                self.change_state(self._state_eat)
            elif x < 70:
                self.change_state(self._state_walk)

    class StateEat(FlyObj.StateStill):
        def enter(self_, self):
            super(LadyBug.StateEat, self_).enter(self)
            self.spr = self.spr_eat
            self.spr.face = self.facing
            self.spr.play()
            self.lawnsegments = []

            soundsystem.eat()

        def enter_takeoff(self_, self):
            pass

        def update(self_, self, dt, t):
            super(LadyBug.StateEat, self_).update(self, dt, t)
            self.rect.center = self.pos
            if have_luck(0.01):
                self.change_state(self._state_idle)
            if t > self.eat_next_time:
                self.eat_next_time = t + randint(100, 1000)
                if self.lawnsegments:
                    seg = choice(self.lawnsegments)
                    seg.hurt(6)
                    soundsystem.eat()
                    if seg.pos.x - self.pos.x < 0:
                        self.facing = -1
                    else:
                        self.facing = 1
                self.spr.face = self.facing
        
        def collision_response(self_, self, other):
            if isinstance(other, LawnSegment):
                if other not in self.lawnsegments:
                    self.lawnsegments.append(other)

    class StateWalk(FlyObj.StateStill):
        def enter(self_, self):
            super(LadyBug.StateWalk, self_).enter(self)
            self.spr = self.spr_walk
            self.spr.play()
            self.vel.x = choice((-1, 1)) * 0.01
            self.facing = sign(self.vel.x)
            self.spr.face = self.facing
        
        def update(self_, self, dt, t):
            if self.facing == 1:
                if self.pos.x > FENCELEFT - self.rect.w and self.pos.x <= FENCEMIDDLE:
                    self.vel.x = -1 * abs(self.vel.x)
            else:
                if self.pos.x < FENCERIGHT + self.rect.w and self.pos.x >= FENCEMIDDLE:
                    self.vel.x = -1 * abs(self.vel.x)
            self.pos += dt * self.vel
            super(LadyBug.StateWalk, self_).update(self, dt, t)
            self.spr.face = self.facing
            self.rect.center = self.pos
            if have_luck(0.01):
                self.change_state(self._state_idle)
            # stop walking if reaching target location
            if self.pos.x > SCREENWIDTH + 10:
                states.TheStateManager.cur_state.remove_entity(self)
                self._count -= 1
            if self.pos.x < 0 - 10:
                states.TheStateManager.cur_state.remove_entity(self)
                self._count -= 1

    class StateThrown2(FlyObj.StateThrown):
        def enter(self_, self):
            self.spr = self.spr_walk
            super(LadyBug.StateThrown, self_).enter(self)
            self.spr_walk.image = pygame.transform.flip(self.spr_walk.image, 0, 1)
            self.spr.play()
        def leave(self_, self):
            super(LadyBug.StateThrown, self_).leave(self)
            self.spr_walk.image = pygame.transform.flip(self.spr_walk.image, 0, 1)
            self.spr.stop()

    _state_fly = StateFly()
    _state_idle = StateIdle()
    _state_still = _state_idle
    _state_eat = StateEat()
    _state_walk = StateWalk()
    _count = 0

    def __init__(self):
        super(LadyBug, self).__init__(Vec2D(0, 0))
        
        self._state_thrown = LadyBug.StateThrown2()
        
        self.spr_walk = animation.TimedAnimation(self.pos, data.load_image('ladybRwalk_anim.png'), 2, 2, 'loop')
        self.spr_eat = animation.TimedAnimation(self.pos, data.load_image('ladybugReat_anim.png'), 2, 2, 'loop')
        self.spr_idle = animation.TimedAnimation(self.pos, data.load_image('ladybugblink_anim.png'), 2, 2)
        self.spr_fly = animation.TimedAnimation(self.pos, data.load_image('ladybRfly_anim.png'), 2, 10, 'loop')
        self.spr_fly.play()
        if have_luck(0.5):
            self.pos.x = -5
            self.vel.x = 0.08
        else:
            self.pos.x = 800 + 5
            self.vel.x = -0.1
        self.vel.y = 0.008
        self.pos.y = randint(150, 350)
        self._count += 1
        
        self.spr = self.spr_fly
        
        self.rect = self.spr.rect
        self.size = self.rect.h / 2
        self.eat_next_time = 0
        self.spr.face = self.facing
        self._walk_target = 0
        self.lawnsegments = []
        self.steam = randint(400, 800)
        self.change_state(self._state_fly)

#-------------------------------------------------------------------------------

class Carterpilar(LadyBug):

    def __init__(self):
        super(Carterpilar, self).__init__()
        self._state_fly = self._state_eat
        self.spr_walk = animation.TimedAnimation(self.pos, data.load_image('legpalwalk_animsmall.png'), 2, 2, 'loop')
        self.spr_eat = animation.TimedAnimation(self.pos, data.load_image('legpaleat_animsmall.png'), 2, 2, 'loop')
        self.spr_idle = animation.TimedAnimation(self.pos, data.load_image('legpalwalk_animsmall.png'), 1, 1)
        self.spr_fly = self.spr_eat
        self.spr = self.spr_eat
        self.pos.x = randint(10, 800)
        self.change_state(self._state_thrown)

