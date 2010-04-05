from article import Article
from waterdrop import WaterDrop

from gamelib import states
from gamelib import animation
from gamelib.data import load_image, load_sound

from random import randint

class WateringCan(Article):

    class StateHeld(Article.StateHeld):

        def activate(self_, self, player, *args, **kwargs):
            if self.is_on:
                self.is_on = False
                self.spr = self.spr_normal
                self.sound.fadeout(100)
            else:
                self.is_on = True
                self.spr = self.spr_dispensing
                self.sound.play(loops=-1)
            self.spr.face = self.facing

        def leave(self_, self):
            super(WateringCan.StateHeld, self_).leave(self)
            self.is_on = False
            self.spr = self.spr_normal
            self.sound.fadeout(100)

        def update(self_, self, dt, t):
            super(WateringCan.StateHeld, self_).update(self, dt, t)
            self.spr.face = self.facing
            if self.is_on:
                self.sound.play(loops=-1)
                pos = self.pos
                pos.x += self.facing * 30
#                if t > self.next_drop:
#                    self.next_drop = t + randint(10, 120)
#                    states.TheStateManager.cur_state.add_entity(WaterDrop(pos, self.facing))
                for i in range(randint(0, 3)):
                    states.TheStateManager.cur_state.add_entity(WaterDrop(pos, self.facing))

    _state_held = StateHeld()

    def __init__(self, pos, *args, **kwargs):
        super(WateringCan, self).__init__(pos, *args, **kwargs)
        self.is_on = False
        img = load_image('watering_can.png')
        self.spr_normal = animation.TimedAnimation(self.pos, img, 1, 1)
        img = load_image('watering_can_dispensing.png')
        self.spr_dispensing = animation.TimedAnimation(self.pos, img, 1, 1)
        self.spr = self.spr_normal
        self.next_drop = 0

        self.sound = load_sound('water.wav')
        
