from vec2d import *

class Entity(object):

    def __init__(self, pos):
        self.pos = Vec2D(*pos)
        self.vel = Vec2D(0, 0)
        self.accel = Vec2D(0, 0)

    def set_vel(self, vx, vy):
        self.vel.x = vx
        self.vel.y = vy

    def update(self, dt, t, *args, **kwargs):
        self.vel += dt * self.accel
        self.pos += dt * self.vel

    def render(self, screen, dt, t, *args, **kwargs):
        pass