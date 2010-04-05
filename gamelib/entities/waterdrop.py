from flyobj import FlyObj
from statemachine import StateMachine
from lawnsegment import LawnSegment

from gamelib.constants import *
from gamelib.data import load_image
from gamelib import animation, states

from random import randint

class WaterDrop(FlyObj):

    class StateThrown(FlyObj.StateThrown):
        def update(self_, self, dt, t):
            if self.pos.x > FENCELEFT and self.pos.x < FENCERIGHT:
                if self.pos.y > FENCETOP:
                    self.vel.x *= FENCEBOUNCE # bounce from fence
                    self.pos.x += self.vel.x * FENCESPEED
            super(StateMachine, self).update(dt, t)
            ground_limit = GROUNDLIMIT - (self.size / 2.0)
            # Constrain to screen width
            self.pos.x = max(0, min(SCREENWIDTH, self.pos.x))
            self.spr.update(dt, t)
            self.spr.rect.center = self.pos
            self.rect.midbottom = self.pos

        def collision_response(self_, self, other):
            if isinstance(other, LawnSegment):
                if other.pos.x > FENCERIGHT and states.TheStateManager.cur_state.multiplayer == False:
                    other.heal(WATERDROPGRASSHEALINGAI)
                else:
                    other.heal(WATERDROPGRASSHEALING)
                states.TheStateManager.cur_state.remove_entity(self)

    _state_thrown = StateThrown()

    def __init__(self, pos, facing):
        super(WaterDrop, self).__init__(pos)
        self.vel.x = facing * randint(0, 100) * 0.0005
        self.vel.y = -randint(0, 20) * 0.001
        self.accel.y = FALLSPEED
        img = load_image('waterdrop.png')
        self.spr = animation.FrameAnimation(self.pos, img)
        self.rect.size = self.spr.rect.size
