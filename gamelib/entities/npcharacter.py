from statemachine import StateMachine
from poop import Poop
from wateringcan import WateringCan
from bugs import LadyBug

import gamelib
from gamelib.geometry import Vec2D, sign
from gamelib.constants import *
from gamelib import animation, states
from gamelib.data import load_image
from gamelib.utility import *
from gamelib import soundsystem

import pygame
import random
rand = random.Random()
rint = random.randint


            
class NPCharacter(StateMachine):
    annoyances = [Poop, LadyBug]

    class StateThink(StateMachine.State):
        def enter(_self, self):
            self.set_vel(0, 0)
            if self.spr:
                self.spr.stop()
            self.run_time = 0.0
        def update(_self, self, dt, t):
            super(StateMachine, self).update(dt, t)
            self.run_time += dt
            if self.run_time >= AITHINKTIME:
                _self.makePlan(self)   
            self.spr.update(dt, t)  
            self.rect.midtop = self.pos  
            
        def render(self_, self, screen, dt, t):
            self.spr.render(screen, dt, t)
            
            
        
                
        def makePlan(_self, self):
            nextState = None
            self.report(msg="Planning for %s : %s " % (self._pickup, (self.target, self.targetkind, self.carrypos, self.carrykind)))
            if self._pickup:
                if not self.carrypos:
                    # Just picked up item
                    if self.carrykind in self.annoyances:
                        self.carrypos = self.get_throw_position()
                        self.change_state(self._state_carry)
                        return
                    elif self.carrykind == WateringCan:
                        if self.losing_bonus() >= 20 and self.app.lawn.right_avg() < 50:
                            self.change_state(self._state_water_pace)
                            return
                        else:
                            result = self.app.find_dirty(self.pos.x)
                            self.report("DIRTY SEARCH : %s" % str(result))
                            if result:
                                pos, hp = result
                                if pos <= FENCELEFT + AIWATERFLIPDIST:
                                    self.carrypos = pos + AIWATEROFFSET
                                    self.flipwater = True
                                else:
                                    self.carrypos = pos - AIWATEROFFSET
                                    self.flipwater = False
                            self.change_state(self._state_carry)
                            return
                    else:
                        self.carrypos = self.get_throw_position()
                        self.change_state(self._state_carry)
                        return
                elif self.carrypos:
                    # Has item and target destination
                    if self.carrykind in self.annoyances:
                        if self.carrypos == CARRYFLAG:
                            # Are we there?
                            self.carrypos = None
                            self.change_state(self._state_throw)
                            return
                        else:
                            self.change_state(self._state_carry)
                            return
                    elif self.carrykind == WateringCan:
                        if self.carrypos == CARRYFLAG:
                            # Are we there?
                            self.carrypos = None
                            self.change_state(self._state_water)
                            return
                        else:
                            # Not there yet
                            self.change_state(self._state_carry)
                            return 
                    else:
                        if self.carrypos == CARRYFLAG:
                            # Are we there?
                            self.carrypos = None
                            self.change_state(self._state_throw)
                            return
                        else:
                            self.change_state(self._state_carry)
                            return
                            
            else:
                self.target = self.targetkind = self.carrypos = self.carrykind = None
                self.check_bugs()
                roll = rint(0, 100)
                if roll - self.losing_bonus() < AIHANDLELOSINGCHANCE:
                    water = self.app.find_closest(self.pos.x, SCREENWIDTH / 2, WateringCan)
                    if water:
                        self.target = water[1]
                        self.targetkind = WateringCan
                        self.change_state(self._state_seek) 
                        return
                bug = self.app.find_closest(self.pos.x, SCREENWIDTH / 2, LadyBug)
                if bug and roll > AIHANDLEBUGCHANCE:
                    self.targetkind, self.target = bug
                    self.change_state(self._state_seek)
                    return
                mole = self.app.find_mole()
                if mole and roll < AIHANDLEMOLECHANCE:
                    if abs(mole.pos.x - self.pos.x) <= AIMOLESEEKDIST:
                        self.target = mole.pos.x
                        self.change_state(self._state_seek) 
                        return
                poop = self.app.find_closest(self.pos.x, SCREENWIDTH / 2, Poop)
                if poop and roll < AIHANDLEPOOPCHANCE:
                    self.targetkind, self.target = poop
                    self.change_state(self._state_seek) 
                    return
                
                        
            self.change_state(self._state_seek)
            return
                
    class StateWater(StateMachine.State):
        def enter(_self, self):
            if not isinstance(self._pickup, WateringCan):
                self.abort(msg="Not holding WateringCan")
                
            self.spr = self.spr_carry
            self.spr.stop()
            facing = 1
            if self.flipwater: facing = -1
            self.facing = self.spr.face = self._pickup.facing = facing
            self.flipwater = False
                
            self.run_time = 0.0
            self._pickup.activate(self)    
                
        def update(_self, self, dt, t):
            super(StateMachine, self).update(dt, t)
            
            self._pickup.pos.values = self.pos
            self._pickup.pos.y -= 35 + (self._pickup.rect.h / 2)
            self._pickup.facing = self.facing
            self.spr.update(dt, t)
            self.rect.midtop = self.pos
            
            self.run_time += dt
            if self.run_time >= AIWATERTIMEMAX:
                self.let_fall()
                self.done(msg="Watering for too long.")
            if self.run_time >= AIWATERTIMEMIN and have_luck(0.01):
                self.let_fall()
                self.done(msg="Done watering for now.")
                
            self.check_bugs()
            
        def render(self_, self, screen, dt, t):
            self.spr.render(screen, dt, t)
            
            
    class StatePace(StateMachine.State):
        def enter(_self, self):
            self.spr = self.spr_walk
            self.spr.play()
            if self.facing < 0:
                _self.walk_left(self)
            else:
                _self.walk_right(self)
            self.run_time = 0.0
                
        def walk_left(_self, self):
            self.facing = self.spr.face = -1
            self.set_vel(-0.1, 0)
            
        def walk_right(_self, self):
            self.facing = self.spr.face = 1
            self.set_vel(0.1, 0)
        
        def update(_self, self, dt, t):
            super(StateMachine, self).update(dt, t)
            # Boundries
            if self.pos.x > SCREENWIDTH:
                self.pos.x = SCREENWIDTH
                _self.walk_left(self)
            elif self.pos.x < FENCERIGHT:
                self.pos.x = FENCERIGHT
                _self.walk_right(self)
            self.run_time += dt
            if have_luck(0.05) and self.run_time >= AIPACETIME:
                self.done(msg="Done pacing for now.")
            self.spr.update(dt, t)
            self.rect.midtop = self.pos
            self.check_bugs()

        def render(self_, self, screen, dt, t):
            self.spr.render(screen, dt, t)
            
    class StateWaterPace(StateMachine.State):
        def enter(_self, self):
            if not isinstance(self._pickup, WateringCan):
                self.abort(msg="Can't water pace, not holding water can!")
            
            self.spr = self.spr_carry
            self.spr.play()
            if self.facing < 0:
                _self.walk_left(self)
            else:
                _self.walk_right(self)
            self._pickup.activate(self)
            self.run_time = 0.0
                
        def walk_left(_self, self):
            self.facing = self.spr.face = -1
            self.set_vel(-0.1, 0)
            
        def walk_right(_self, self):
            self.facing = self.spr.face = 1
            self.set_vel(0.1, 0)
        
        def update(_self, self, dt, t):
            super(StateMachine, self).update(dt, t)
            # Boundries
            if self.pos.x > SCREENWIDTH:
                self.pos.x = SCREENWIDTH
                _self.walk_left(self)
            elif self.pos.x < FENCERIGHT:
                self.pos.x = FENCERIGHT
                _self.walk_right(self)    
                
            self.run_time += dt
            if have_luck(0.05) and self.run_time >= AIPACETIME * 5:
                self.let_fall()
                self.done(msg="Done water pacing for now.")
            self.spr.update(dt, t)
            self.rect.midtop = self.pos
            
            if self._pickup:
                    self._pickup.pos.values = self.pos 
                    self._pickup.pos.y -= 35 + (self._pickup.rect.h / 2)
            self.check_bugs()
        def render(self_, self, screen, dt, t):
            self.spr.render(screen, dt, t)
            
    class StateThrow(StateMachine.State):
        def enter(_self, self):
            if not self._pickup:
                self.abort()
                return
            self.facing = self.spr.face = -1
            self.spr = self.spr_carry
            self.set_vel(0.0, 0.0)
            self._pickup_time = 0.0
            self.power = rand.randint(AITHROWMINIMUM, 10) / 10.0
            self.power = min(1.0, self.power)
            
        def update(_self, self, dt, t):
            super(StateMachine, self).update(dt, t)
            self._pickup_time += (dt * AITHROWADVANTAGE) / 1500.0
            self._pickup_time = min(1.0, self._pickup_time)
            self.calc_apex()
            if self._pickup_time >= self.power:
                item, pos = self._pickup, self.power
                self.throw()
                self.done(msg="Threw %s with %d power." % (item, pos))
                
            self.spr.update(dt, t)
            self.rect.midtop = self.pos
                
        def render(self_, self, screen, dt, t):
            self.spr.render(screen, dt, t)
            if self._pickup_time > 0.0:
                self.crosshair.render(screen, dt, t)
            
    class StateSeek(StateMachine.State):
        
        def walk_left(_self, self):
            self.facing = self.spr.face = -1
            self.set_vel(-0.1, 0)
            
        def walk_right(_self, self):
            self.facing = self.spr.face = 1
            self.set_vel(0.1, 0)
    
        def enter(_self, self):
            self.spr = self.spr_walk
            self.spr.play()
            if not self.target:
                item = self.app.find_closest(self.pos.x, SCREENWIDTH / 2, self.targetkind)
                if item:
                    self.target = item[1]
                    self.targetkind = item[0]
                    if gamelib.DEBUG: print "Seeking %s at %d" % (    self.targetkind, self.target)
                else:
                    self.abort()
            if self.target < self.pos.x:
                _self.walk_left(self)
            elif self.target > self.pos.x:
                _self.walk_right(self)
            else:
                pass # todo pickup
                    
        def update(_self, self, dt, t):
            super(StateMachine, self).update(dt, t)
            if abs(self.pos.x - self.target) <= 10:
                item = states.TheStateManager.cur_state.get_closest(self.pos.x, 100, self.targetkind)
                if item and item[0].__class__ == self.targetkind and item[0].pickupable:
                    self.pickup(item[0])
                    self.carrykind = self.targetkind
                    self.carrypos = None
                    self.target = None
                    self.targetkind = None
                    self.done(msg="Picked up %s at %d" % (self._pickup, self.pos.x))
                    return
                else:
                    self.abort()
                    return
            # Boundries
            if self.pos.x > SCREENWIDTH:
                self.pos.x = SCREENWIDTH
                self.abort(msg="Seeked %s off-screen at %d" % (self.targetkind, self.target))
                return
            elif self.pos.x < FENCERIGHT:
                self.pos.x = FENCERIGHT
                self.abort(msg="Seeked %s off-screen at %d" % (self.targetkind, self.target))
                return
            if self.target == None: self.abort(msg="Bumped into wall, where is target? Oh well."); return
            
            if self._pickup:
                self._pickup.pos.values = self.pos
            else:
                if self.targetkind not in [LadyBug]:
                    self.check_bugs()   
            self.spr.update(dt, t)
            self.rect.midtop = self.pos
                
        def render(self_, self, screen, dt, t):
                self.spr.render(screen, dt, t)
            
    class StateCarry(StateMachine.State):
            def enter(_self, self):
                self.spr = self.spr_carry
                self.spr.play()
                if not self.carrypos:
                    self.carrykind = None
                    self.done(msg="Had no where to carry to.")
                elif self.carrypos < self.pos.x:
                    _self.walk_left(self)
                elif self.carrypos > self.pos.x:
                    _self.walk_right(self)
                else:
                    pass # todo pickup
                    
            def walk_left(_self, self):
                self.facing = self.spr.face = -1
                self.set_vel(-0.1, 0)
                
            def walk_right(_self, self):
                self.facing = self.spr.face = 1
                self.set_vel(0.1, 0)
            
            def update(_self, self, dt, t):
                super(StateMachine, self).update(dt, t)
                # Boundries
                if self.pos.x > SCREENWIDTH - AICARRYBUFFER:
                    self.pos.x = SCREENWIDTH - AICARRYBUFFER
                    self.abort()
                    return
                elif self.pos.x < FENCELEFT + AICARRYBUFFER:
                    self.pos.x = FENCELEFT + AICARRYBUFFER
                    self.abort()
                    return
                    
                if self._pickup:
                    self._pickup.pos.values = self.pos 
                    self._pickup.pos.y -= 35 + (self._pickup.rect.h / 2)   
                    
                    if isinstance(self._pickup, WateringCan):
                        if self.check_bugs(): return
                    
                if abs(self.pos.x - self.carrypos) < AICARRYBUFFER:
                    self.carrypos = CARRYFLAG
                    self.done(msg="Carried %s to %d" % (self._pickup, self.pos.x))
                self.spr.update(dt, t)
                self.rect.midtop = self.pos

            def render(self_, self, screen, dt, t):
                self.spr.render(screen, dt, t)

            
    _state_think = StateThink()
    _state_pace = StatePace()
    _state_seek = StateSeek()
    _state_carry = StateCarry()
    _state_throw = StateThrow()
    _state_water = StateWater()
    _state_water_pace = StateWaterPace()
    
    _st_time = 0.0
    _st_limit = 5000
    _st_f_damaged = 0
    _st_f_otherhealed = 0
    
    def handle_event(self, event): pass
    
    def __init__(self):
        super(NPCharacter, self).__init__(Vec2D(SCREENWIDTH - 100, 355), self._state_think)
        self.app = states.TheStateManager.cur_state
        self.spr_walk = animation.TimedAnimation(self.pos, load_image('guy2walk_animnew.png'), 4, 5, 'loop')
        self.spr_carry = animation.TimedAnimation(self.pos, load_image('guy2walkhands_animnew.png'), 4, 30, 'loop')
        self.spr = self.spr_walk
        self.rect = pygame.Rect(self.spr.rect)
        self.rect.inflate_ip(-self.rect.w / 2, -self.rect.h / 2)
        self.pickupable = False
        self._st = StatsTracker()
        self._st_lasthealth = 0
        self.facing = 1
        self._pickup = None
        self._pickup_time = 0.0
        self.build_up_power = False
        self.target = None
        self.targetkind = None
        self.carrypos = None
        self.carrykind = None
        self.flipwater = False
        
        i = pygame.Surface((3,3))
        i.fill((255,0,0))
        self.crosshair = animation.FrameAnimation(self.pos.clone(), i)
   
    def check_bugs(self):
        mybugs = self.app.get_collection(self.pos.x, LadyBug)
        if len(mybugs) > 2:
            bug = self.app.find_closest(self.pos.x, SCREENWIDTH / 2, LadyBug)
            if bug:
                self.let_fall()
                self.targetkind , self.target = bug
                self.change_state(self._state_seek)
                return 1
        return 0
   
    def update(self, dt, t, *args, **kwargs):
        hp = self.app.lawn.right_score()
        if hp < self._st_lasthealth:
            self._st_f_damaged = 1
        self._st_lasthealth = hp
    
        self._st_time += dt
        if self._st_time >= self._st_limit:
            self._st_time = 0.0
            # Track damage we take
            if self._st_f_damaged  != 0:
                self._st.add_event('damaged',self._st_f_damaged)
                self._st_f_damaged = 0
            else:
                self._st.add_event('damaged', 0)
            # Track when the other player is healing    
            if self._st_f_otherhealed != 0:
                self._st.add_event('otherhealed', self._st_f_otherhealed)
                self._st_f_otherhealed = 0
            else:
                self._st.add_event('otherhealed', self._st_f_otherhealed)
                
            print "STATS: damaged - ", self._st.calc_average('damaged')
            print "STATS: otherhealed - ", self._st.calc_average('otherhealed')
        self.cur_state.update(self, dt, t, *args, **kwargs)
        dir = sign(self.vel.x)
        if dir:
            self.facing = dir
    def change_state(self, new_state):
        try:
            self.report("Entering %s %s" % (new_state, str((self._pickup, self.target, self.targetkind, self.carrypos, self.carrykind, self.flipwater))))
        except: pass
        super(NPCharacter, self).change_state(new_state)
    
    def report(self, msg):
        if gamelib.DEBUG: print "REPORT: %s" % msg
    
    def done(self, msg=None):
        if gamelib.DEBUG: print "DONE: %s" % msg
        self.change_state(self._state_think)
    
    def abort(self, msg=None):
        if gamelib.DEBUG: print "ABORTING %s" % msg
        self.let_fall()
        self.change_state(self._state_pace)
    
    def pickup(self, obj):
        if not self._pickup:
            self._pickup = obj
            obj.pickup()
            
    def let_fall(self):
        if self._pickup:
            self._pickup.throw()
            self._pickup = None
            self._pickup_time = 0.0 
            self.carrypos = None
            self.carrykind = None
            self.target = None
            self.targetkind = None 
            self.flipwater = False
            self.spr = self.spr_walk
            
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
            accel = Vec2D(0, 0.0005)
            oldpos = pos
            t = -vel.y/accel.y
            pos.x = pos.x + vel.x*t
            pos.y = pos.y + 0.5*t*t*accel.y + vel.y*t
            self.crosshair.pos.values = pos
            
    def get_throw_position(self):
        return rand.randint(AITHROWRANGECLOSE, AITHROWRANGEFAR)
        
    def losing_bonus(self):
        ls = self.app.lawn.left_score()
        rs = self.app.lawn.right_score()
        point_diff = ls - rs
        av_diff = ls / 10.0 - rs / 10.0
        
        if point_diff > AILOOSINGPOINTDIFF or av_diff > AILOOSINGAVGDIFF:
            print "LOSING BONUS : ", point_diff / 10 + av_diff
            if self.app.lawn.right_score() < 333:
                point_diff += 1000
            return point_diff / 10 + av_diff
        return False
            
    def throw(self):
        if self._pickup:
            if self.facing >= 0:
                dir = Vec2D(100.0, -160.0)
            else:
                dir = Vec2D(-100.0, -160.0)
            dir.normalize()
            self._pickup.vel.values = self._pickup_time * (dir / self._pickup.weight)
            self._pickup.throw()
            self.calc_apex()
            self._pickup = None
            self._pickup_time = 0.0

            soundsystem.grunt()
