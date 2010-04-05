import pygame
from pygame.locals import *

import gamelib
from gamelib import states
from gamelib import animation
from gamelib.geometry import Vec2D, Entity, sign
from gamelib.utility import calculateGradient as calcG
from gamelib.data import load_image

from flyobj import FlyObj
from article import Article
from wateringcan import WateringCan

from gamelib import soundsystem

purple = (255, 0, 255)
red = (255, 0, 0)

class Player(Entity):

    def __init__(self):
        super(Player, self).__init__((100, 355))
        self.spr_carry = animation.TimedAnimation(self.pos, load_image('guywalkhands_animnew.png'), 4, 30, 'loop')
        self.spr_walk = animation.TimedAnimation(self.pos, load_image('guywalk_animnew.png'), 4, 5, 'loop')
        self.spr = self.spr_walk
        self.facing = 1 # 1: right -1: left
        d = sign(self.vel.x)
        if d:
            self.facing = d
        self.kdir = 0
        self.rect = pygame.Rect(self.spr.rect)
        self.rect.inflate_ip(-self.rect.w/2, -self.rect.h/2)
        self._pickup = None
        self._pickup_time = 0.0
        self.collider = None
        self.last_thrown = None
        self.build_up_power = False
        self.actionkey_walk_l = K_a
        self.actionkey_walk_r = K_d
        self.actionkey_pickup = K_s
        self.actionkey_throw = K_w
        self.side = -1 # left
        # crosshair
        img = pygame.Surface((3, 3))
        img.fill((255, 0, 0))
        self.crosshair = animation.FrameAnimation(self.pos.clone(), img)

    def update(self, dt, t):
        super(Player, self).update(dt, t)
        # bounderies
        if self.side == -1:
            if self.pos.x < 0:
                self.pos.x = 0
            elif self.pos.x > 380:
                self.pos.x = 380
        else:
            if self.pos.x > 800:
                self.pos.x = 800
            elif self.pos.x < 420:
                self.pos.x = 420
        # sprite
        self.spr.update(dt, t)
        # facing
        d = sign(self.vel.x)
        if d:
            self.facing = d
        # holding obj
        if self._pickup:
            self._pickup.pos.values = self.pos
            self._pickup.pos.y -= 35 + (self._pickup.rect.h / 2)
            self._pickup.facing = self.facing
        # power
        if self.build_up_power:
            self._pickup_time += dt / 1500.0
            self._pickup_time = min(1.0, self._pickup_time)
            self.calc_apex()
        self.rect.midbottom = self.spr.rect.midbottom
        self.crosshair.update(dt, t)

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key == self.actionkey_walk_l:
                self.kdir -= 1
            elif event.key == self.actionkey_walk_r:
                self.kdir += 1
            elif event.key == self.actionkey_pickup:
                #if self.collider:
                #    self.pickup(self.collider)
                #    self.collider = None
                #    if gamelib.DEBUG: print "*!*!*!*!*!*! CAUGHT %s *!*!*!*!*!" % self._pickup
                if self._pickup and not self.build_up_power:
                    self.let_fall()
                else:
                    item = states.TheStateManager.cur_state.get_closest(self.pos.x, self.rect.w)
                    if item:
                        self.pickup(item[0])
            elif event.key == self.actionkey_throw and self._pickup:
                if isinstance(self._pickup, Article):
                    self._pickup.activate(self)
                else:
                    self.build_up_power = True
        elif event.type == KEYUP:
            if event.key == self.actionkey_walk_l:
                self.kdir += 1
            elif event.key == self.actionkey_walk_r:
                self.kdir -= 1
            elif event.key == self.actionkey_throw:
                if not isinstance(self._pickup, Article):
                    soundsystem.grunt()
                    self.build_up_power = False
                    self.throw()
            #elif event.key == self.actionkey_pickup:
            #    if not self._pickup:
            #        item = states.TheStateManager.cur_state.get_closest(self.pos.x, self.rect.w)
            #        if item:
            #            self.pickup(item[0])

        self.set_vel(0.1*self.kdir, 0)
        if self.kdir != 0:
            self.facing = self.kdir
            self.spr.face = self.facing
            if self._pickup:
                self._pickup.spr.face = self.facing
            self.spr.play()
        else:
            self.spr.stop()


    def render(self, screen, dt, t):
        self.spr.render(screen, dt, t)
        if self.build_up_power:
            self.crosshair.render(screen, dt, t)

    def pickup(self, obj):
        if not self._pickup and obj.pickupable:
            self.spr = self.spr_carry
            self._pickup = obj
            obj.pickup()

    def let_fall(self):
        if self._pickup:
            self.spr = self.spr_walk
            self._pickup.throw() # just sets the state
            self.last_thrown = self._pickup
            self._pickup = None
            self._pickup_time = 0.0

    def throw(self):
        if self._pickup:
            self.spr = self.spr_walk
            self.spr.face = self.facing
            if gamelib.DEBUG: print self._pickup,  self._pickup.cur_state, self._pickup.pickupable
            if self.facing >= 0:
                dir = Vec2D(100.0, -160.0)
            else:
                dir = Vec2D(-100.0, -160.0)
            dir.normalize()
            self._pickup.vel.values = self._pickup_time * (dir / self._pickup.weight)
            self._pickup.throw() # just sets the state
            self.calc_apex()
            self.last_thrown = self._pickup
            self._pickup = None
            self._pickup_time = 0.0

    def collision_response(self, other):
        if isinstance(other.cur_state, FlyObj.StateThrown):
            self.collider = other

    def calc_apex(self):
        if self.facing >= 0:
            dir = Vec2D(100.0, -160.0)
        else:
            dir = Vec2D(-100.0, -160.0)
        dir.normalize()
        vel = self._pickup_time * (dir / self._pickup.weight)
        pos = self._pickup.pos.clone()
        # FIXME: The acceleration (gravity) should be handled better.
        # The original solution broke when I made birds throwable, but
        # of course the new solution of hard coding the value here isn't much
        # better. I don't think the original solution is very sensible either
        # though, because at the time of throwing, the throwable item naturally
        # isn't moving and has no acceleration.
        #accel = self._pickup.accel.clone()
        accel = Vec2D(0, 0.0005)
        oldpos = pos
     #   dt = 1
        t = -vel.y/accel.y
        pos.x = pos.x + vel.x*t
        pos.y = pos.y + 0.5*t*t*accel.y + vel.y*t
#        while oldpos.y >= pos.y:
 #           oldpos = pos.clone()
  #          vel += dt * accel
   #         pos += dt * vel
    #        dt += 1
        self.crosshair.pos.values = pos
#        self.crosshair.pos.x = pos.x
#        self.crosshair.pos.y = pos.y
