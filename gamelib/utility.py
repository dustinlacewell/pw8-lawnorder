import math
from random import randint, random, choice

import pygame
from pygame.locals import *

import states, animation, gradients, data

def have_luck(probability=0.5):
    return random() <= probability
# this function makes a sin-function unsymmetrical, so that the day can be longer than the night
# balance=0 means equal durations, positive values make the sin-function positive most of the time
def nightday(t, balance):
    return balance+t-balance*t*t
    

class StatsTracker(object):
    MAXSTATS = 100
    def __init__(self):
        self._stats = {}
        
    def add_event(self, name, value):
        if name in self._stats.keys():
            if len(self._stats[name]) == self.MAXSTATS:
                self._stats[name].pop()
            self._stats[name].insert(0, value)
        else:
            self._stats[name] = [value]
            
    def calc_average(self, name):
        if name not in self._stats.keys():
            return 0.0
        if isinstance(self._stats[name][0], type(1)) or isinstance(self._stats[name][0], type(1.0)):
            total = 0
            for val in self._stats[name]:
                total += val
            return total / len(self._stats[name])
            
            
if __name__ == "__main__":

    st = StatsTracker()
    for i in range(300):
        st.add_event('integer', randint(0, 100))
        st.add_event('boolean', choice((0.0, 1.0)))
    print "Average integers(100) over 300: %d" % st.integer
    print "Average booleans(2) over 300: %.2f" % float(st.boolean)    


def calculateGradient(colorA, colorB, dist):
    """
    calculateGradient - Computes RGB triplet on the gradient between
    colorA and colorB with the provided distance.

    dist is a float between 0.0 and 1.0
    """
    dist = min(1.0, max(0.0, dist))

    red = ( colorA[0] + (colorB[0] - colorA[0]) * dist )
    red = min(255, max(0, red))

    green = ( colorA[1] + (colorB[1] - colorA[1]) * dist )
    green = min(255, max(0, green))

    blue = ( colorA[2] + (colorB[2] - colorA[2]) * dist )
    blue = min(255, max(0, blue))
#    print (red, green, blue)
    return (red, green, blue)

class Bgd(object):

    def __init__(self):
        self.screen_rect = states.TheStateManager.screen.get_rect()
        self.img = gradients.vertical(self.screen_rect.size, (0, 255, 255, 255), (80, 100, 135, 255))

        # Sun
        sunimg = pygame.transform.scale2x(pygame.image.load(data.filepath('sun.png'))).convert_alpha()
        self.sun = self.spr = animation.FrameAnimation((0, 0), sunimg)
        self.sun_radius = self.screen_rect.h * 0.8

        # Moon
        moonimg = pygame.image.load(data.filepath('moon.png')).convert_alpha()
        self.moon =  animation.FrameAnimation((0, 0), moonimg)
        self.moon_radius = self.screen_rect.h * 0.8

        # Generate starfield
        self.stars = pygame.Surface(self.screen_rect.size).convert()
        self.stars.fill((0, 255, 0))
        self.stars.set_alpha(None)
        self.stars.set_colorkey((0, 255, 0))
        self.stars.lock()
        for i in range(80):
            x = randint(0, self.screen_rect.width)
            y = randint(0, self.screen_rect.height)
            self.stars.set_at((x,y), (255,255,255))
        self.stars.unlock()

        self.night = pygame.Surface(self.screen_rect.size).convert()
        self.night.fill((0, 0, 0))
        self.night.set_alpha(None)
        self.night.set_colorkey(None)
        self.night.set_alpha(0)


        self.math_time = -0.25

    def update(self, dt, t, *args, **kwargs):
        # sky
        fullcircletime = 3*60*1000.0 # three minutes per round
        startingtime=0.25 # starting point as the fraction of a full circle (which equals one)
        self.math_time += dt/fullcircletime
        dayratio=0.3
        s = nightday(math.cos((self.math_time+startingtime) * 2 * math.pi), dayratio)
        s1 = int(round(127 * s))
        self.img = gradients.vertical(self.screen_rect.size,  (0, s1 + 128, s1 + 128, 255), (0, 0, 128+s1/4, 255))
        # sun
        offx, offy = self.sun.image.get_size()
        x = self.screen_rect.centerx - offx/2 + dayratio*3.8 * self.sun_radius * math.sin((self.math_time+startingtime) * 2 * math.pi)
        y = self.screen_rect.h - offy/2 - self.sun_radius * nightday(math.cos((self.math_time+startingtime) * 2 * math.pi),dayratio)
        self.sun.pos = (x, y)
        # moon
        offx, offy = self.moon.image.get_size()
        x = self.screen_rect.centerx - offx/2 + dayratio*3.8 * self.moon_radius * math.sin((self.math_time+startingtime) * 2 * math.pi + math.pi)
        y = self.screen_rect.h - offy/2 - self.sun_radius * nightday(math.cos((self.math_time+startingtime) * 2 * math.pi + math.pi),dayratio)
        self.moon.pos = (x, y)
        # stars
        self.stars.set_alpha(160*nightday(math.sin((self.math_time+startingtime) * 2 * math.pi+ math.pi * 1.5),dayratio)+84 )
        # night
        alpha = 40 + 40 * nightday(math.sin((self.math_time+startingtime) * 2 * math.pi + math.pi * 1.5), dayratio)
        self.night.set_alpha(alpha, pygame.RLEACCEL)

    def render(self, screen, dt, t, *args, **kwargs):
        screen.blit(self.img, (0, 0))
        screen.blit(self.stars, (0, 0))
        screen.blit(self.sun.image, self.sun.pos)
        screen.blit(self.moon.image, self.moon.pos)

    def render_night(self, screen, dt, t):
        screen.blit(self.night, (0, 0))
