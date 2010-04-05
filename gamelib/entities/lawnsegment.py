from gamelib.geometry import Entity
from random import randint
from gamelib import animation
from gamelib.data import load_image

class LawnSegment(Entity):
    HEALTHY, ANNOYED, HURT, DAMAGED, DEAD = range(5)
    MAXHEALTH = 100
    LIMITS = [80, 60, 30]
    def __init__(self, pos):
        super(LawnSegment, self).__init__(pos)
        # Setup sprites for state
        self.type = randint(1,3)
        self.frames = []
        for t in ['healthy%d.png', 'annoyed%d.png', 
                   'hurt%d.png', 'damaged%d.png', 'dead%d.png']:
            self.frames.append(animation.FrameAnimation(self.pos,
                load_image('grass/' + (t % self.type))))
        self.hurt_icon = animation.TimedAnimation(self.pos,
            load_image('grass/hurt_icon.png'), 10, 10, mode = 'once')
        self.heal_icon = animation.TimedAnimation(self.pos,
            load_image('grass/heal_icon.png'), 6, 10, mode = 'once')
                 
        self.state =  self.HEALTHY
        self.hitpoints = self.MAXHEALTH
        self.image = self.frames[self.state]
        self.rect = self.image.rect
        
    def hurt(self, amount):
        self.hitpoints -= amount
        self.hitpoints = max(0, self.hitpoints)
        if self.hitpoints > 0:
            self.hurt_icon.play()

    def heal(self, ammount):
        self.hitpoints += ammount
        self.hitpoints = min(self.MAXHEALTH, self.hitpoints)
        if self.hitpoints < self.MAXHEALTH:
            self.heal_icon.play()

    def updateState(self):
        if self.hitpoints > self.LIMITS[0]:
            self.state = self.HEALTHY
        elif self.hitpoints <= self.LIMITS[0] and self.hitpoints > self.LIMITS[1]:
            self.state = self.ANNOYED
        elif self.hitpoints <= self.LIMITS[1] and self.hitpoints > self.LIMITS[2]:
            self.state = self.HURT
        elif self.hitpoints <= self.LIMITS[2] and self.hitpoints > 0:
            self.state = self.DAMAGED
        else:
            self.state = self.DEAD

    def update(self, dt, t):
        # Taking all our damages and heals in account what state are we in now?
        self.updateState()
        # Whatever state we're in, update that state's sprite
        self.image = self.frames[self.state]
        self.rect = self.image.rect
        self.image.update(dt, t)
        self.hurt_icon.update(dt, t)
        self.heal_icon.update(dt, t)
        if self.state == self.HEALTHY: pass
        elif self.state == self.ANNOYED: pass
        elif self.state == self.HURT: pass
        elif self.state == self.DAMAGED: pass
        elif self.state == self.DEAD: pass

    def render(self, screen, dt, t):
        self.frames[self.state].render(screen, dt, t)
        if self.hurt_icon.is_running():
            self.hurt_icon.render(screen, dt, t)
        if self.heal_icon.is_running():
            self.heal_icon.render(screen, dt, t)


    def collision_response(self, other):
        pass
