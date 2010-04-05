import pygame
import gamelib
from lawnsegment import LawnSegment


class LawnManager(object):

    def __init__(self):
        self.segments = {'left': [], 'right': []}
        self.left_start = 20; self.right_start = 420;
        for i in range(10):
            self.segments['left'].append(LawnSegment((self.left_start + (40 * i), 395)))
            self.segments['right'].append(LawnSegment((self.right_start + (40 * i), 395)))
    def update(self, dt, t):
        for segment in self.segments['left']:
            segment.update(dt, t)
        for segment in self.segments['right']:
            segment.update(dt, t)
        #print self.left_score(), self.right_score()

    def render(self, screen, dt, t):
        for segment in self.segments['left']:
            segment.render(screen, dt, t)
            if gamelib.DEBUG:
                pygame.draw.rect(screen, (0, 0, 255), segment, 2)
        for segment in self.segments['right']:
            segment.render(screen, dt, t)
            if gamelib.DEBUG:
                pygame.draw.rect(screen, (0, 0, 255), segment, 2)
    
    def check_collisions(self, obj):
        idxs = obj.rect.collidelistall(self.segments['left'])
        if idxs:
            for o in idxs:
                obj.collision_response(self.segments['left'][o])
        
        idxs = obj.rect.collidelistall(self.segments['right'])
        if idxs:
            for o in idxs:
                obj.collision_response(self.segments['right'][o])

    def left_score(self):
        score = 0
        for seg in self.segments['left']:
            score += seg.hitpoints
        return score
        
    def left_avg(self):
        return self.left_score() / 10.0

    def right_score(self):
        score = 0
        for seg in self.segments['right']:
            score += seg.hitpoints
        return score

    def right_avg(self):
        return self.right_score() / 10.0

    def collision_response(self, other):
        pass

