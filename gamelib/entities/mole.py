from flyobj import FlyObj
from statemachine import StateMachine
from lawnsegment import LawnSegment
from player import Player
from npcharacter import NPCharacter

from gamelib.constants import *
from gamelib.geometry import Vec2D, sign
from gamelib import animation
from gamelib.data import load_image
from gamelib.utility import have_luck


import random
from random import randint
import pygame
import gamelib

class Mole(FlyObj):#(StateMachine):
    CLIPDIST = 80
    SPAWNDIST = 10

    class StateWalk(StateMachine.State):

        def enter(_self, self):
            self.vel.y = 0
            self.accel.y = 0
            self.pos.y = randint(460, 480)
            if randint(0, 1):
                self.pos.x = SCREENWIDTH + MOLECLIPDIST
                self.vel.x = -MOLEWALKSPEED
                self.spr = self.spr_walk_l
            else:
                self.pos.x = -MOLECLIPDIST
                self.vel.x = MOLEWALKSPEED
                self.spr = self.spr_walk_r
            
            self.rect.center = self.pos
            self.spr.update(0, 0)
            self.spr.play()
            
            self.collided = []

        def checkScreenClipping(_self, self):
            if self.pos.x < -MOLECLIPDIST:
                self.vel.x *= -1.0
                self.pos.x += 10
                self.spr = self.spr_walk_r
            elif self.pos.x > SCREENWIDTH + MOLECLIPDIST:
                self.vel.x *= -1.0
                self.pos.x -= 10
                self.spr = self.spr_walk_l
                

        def update(_self, self, dt, t, *args, **kwargs):
            super(StateMachine, self).update(dt, t)
            
            _self.checkScreenClipping(self)
            if self.pos.x > 10 and self.pos.x < SCREENWIDTH - 10:
                if have_luck(MOLECLIMBCHANCE):
                    self.change_state(self._state_walk_u)
                    return
                elif have_luck(MOLEDIRCHGCHANCE):
                    self.vel.x *= -1.0
                    if sign(self.vel.x)>0:
                        self.spr = self.spr_walk_r
                    else:
                        self.spr = self.spr_walk_l
                    self.spr.play()
            
        
            self.spr.update(dt, t)
            self.rect.center = self.pos

        def render(_self, self, screen, dt, t, *args, **kwargs):
            self.spr.render(screen, dt, t)
            
            
    class StateClimb(StateMachine.State):
        def enter(_self, self):
            self.vel.x = 0
            self.vel.y = -MOLECLIMBSPEED
            self.spr = self.spr_walk_u
            self.spr.play()
            self.rect.center = self.pos
            self.spr.update(0, 0)
            
            self.close_to_lawn = False
            
        def checkLawnCollision(_self, self):
            if self.close_to_lawn == False:
                if self.pos.y < MOLELAWNPROXIMITY:
                    self.close_to_lawn = True
        
        def update(_self, self, dt, t, *arg, **kwargs):
            super(StateMachine, self).update(dt, t)
            self.spr.update(dt, t)
            self.rect.center = self.pos
            
            _self.checkLawnCollision(self)
                    
        def render(_self, self, screen, dt, t, *args, **kwargs):
            if not self.close_to_lawn:
                self.spr.render(screen, dt, t)
            
        def collision_response(_self, self, other):
                self.change_state(self._state_pop_up)
                
    class StatePopup(StateMachine.State):
        def enter(_self, self):
            self.vel.x = self.vel.y = 0
            self.pos.y = MOLEPOPUPHEIGHT
            self.spr = self.spr_pop_up
            self.spr.play()
            self.rect.center = self.pos
            self.spr.update(0, 0)
            self.touched = False


        def update(_self, self, dt, t, *arg, **kwargs):
            super(StateMachine, self).update(dt, t)
            self.spr.update(dt, t)
            self.rect.center = self.pos
            if have_luck(MOLEDESCENDCHANCE) or self.touched:
                self.change_state(self._state_walk_d)
            
        def render(_self, self, screen, dt, t, *args, **kwargs):
            self.spr.render(screen, dt, t)
            
        def collision_response(_self, self, other):
            if isinstance(other, Player) or isinstance(other, NPCharacter):
                if gamelib.DEBUG: print "!*!*!" * 10,  self.collided
                self.collided = []
                self.touched = True
                #self.change_state(self._state_walk_d)
                return
            elif isinstance(other, LawnSegment) and other not in self.collided and not self.touched:
                self.collided.append(other)
            
            
    class StateDescend(StateMachine.State):
        def enter(_self, self):
            self.vel.x = 0
            self.vel.y = MOLECLIMBSPEED
            self.pos.y = MOLELAWNPROXIMITY
            self.spr = self.spr_walk_d
            self.spr.play()
            self.rect.center = self.pos
            self.spr.update(0, 0)
            
            
            for grass in self.collided:
                grass.hurt(randint(MOLEDAMAGELOW, MOLEDAMAGEHIGH))
            
        def update(_self, self, dt, t, *arg, **kwargs):
            super(StateMachine, self).update(dt, t)
            
            if self.pos.y > MOLEDESCENDDEPTH and have_luck(MOLEDESCENDDEPTH):
                self.change_state(self._state_walk_h)
            
            self.spr.update(dt, t)
            self.rect.center = self.pos
            
        def render(_self, self, screen, dt, t, *args, **kwargs):
            self.spr.render(screen, dt, t)
            
                                 
            


    _state_walk_h = StateWalk()
    _state_walk_u = StateClimb()
    _state_walk_d = StateDescend()
    _state_pop_up = StatePopup()


    def __init__(self, *args, **kwargs):
        super(Mole, self).__init__(Vec2D(-20, random.randint(460, 480)))
        
       
        self.spr_walk_r = animation.TimedAnimation(self.pos, load_image('mole/walk_right.png'), 2, 6, 'loop')
        self.spr_walk_l = animation.TimedAnimation(self.pos, load_image('mole/walk_left.png'), 2, 6, 'loop')
        self.spr_walk_u = animation.TimedAnimation(self.pos, load_image('mole/walk_up.png'), 2, 6, 'loop')
        self.spr_walk_d = animation.TimedAnimation(self.pos, load_image('mole/walk_down.png'), 2, 6, 'loop')
        self.spr_pop_up = animation.TimedAnimation(self.pos, load_image('mole/pop_up.png'), 2, 1.5, 'loop')
        self.spr = self.spr_walk_r
        self.collided = []
        self.rect = pygame.Rect(0, 0, self.spr.rect.w/2, self.spr.rect.h/2)
        self.change_state(self._state_walk_h)
        
