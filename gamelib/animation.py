#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: animation.py 360 2009-05-02 08:52:32Z DLacewell $'

import events
import data

import pygame

class Drawable(pygame.sprite.DirtySprite):

    def __init__(self, *groups, **kwargs):
        super(Drawable, self).__init__(*groups)
        self.dirty = 2 # always, for the moment


class FrameAnimation(Drawable):

    def __init__(self, pos_vec2d, image, anim_len = 1, mode = 'once', *groups, **kwargs):
        super(FrameAnimation, self).__init__(*groups, **kwargs)

        self._frame_width = image.get_width() / anim_len

        self.anim_len = anim_len
        self.event_end = events.Event()

        # Animation modes
        if mode == 'loop':
            self.event_end += self.loop
        elif mode == 'pingpong':
            self.event_end += self.pingpong
        else: # default to once
            self.event_end += self.stop

        self._running = False
        self.image = image
        self.rect = pygame.Rect(0,0,self._frame_width,self.image.get_height())
        self.src_rect = pygame.Rect(self.rect)
        self.pos = pos_vec2d
        self.rect.center = self.pos
        self._cur_idx = 0

        # animation direction
        self._dir = +1
        # facing of images -1 left, 1 right
        self._face = 1

    def flip(self):
        self._face *= -1
        self.image = pygame.transform.flip(self.image, 1, 0)

    def _set_face(self, new_face):
        if self._face != new_face:
            self.flip()

    face = property(lambda self: self._face, _set_face)

    def update(self, dt, t, *args, **kwargs):
        self.rect.center = self.pos
        if self._running:
            self._cur_idx += self._dir
            if self._cur_idx >= self.anim_len or self._cur_idx < 0:
                self._cur_idx -= self._dir
                self.event_end()
            self.src_rect.x = self._frame_width * self._cur_idx

    def render(self, screen_surf, dt, t, *args, **kwargs):
        screen_surf.blit(self.image, self.rect, self.src_rect)

    def play(self):
        self._running = True
        self.src_rect.x = self._frame_width * self._cur_idx

    def stop(self):
        self.pause()
        self._cur_idx = 0

    def pause(self):
        self._running = False

    def is_running(self):
        return self._running

    def loop(self, *args, **kwargs):
        if self._dir > 0:
            self._cur_idx = 0
        else:
            self._cur_idx = self.anim_len - 1
        self.play()

    def pingpong(self, *args, **kwargs):
        self._dir = -self._dir
        if self.anim_len > 1:
            self._cur_idx += self._dir
        self.play()
        
class TimedAnimation(FrameAnimation):
    def __init__(self, pos_vec2d, image, anim_len, fps, mode = 'once', *groups, **kwargs):
        super(TimedAnimation, self).__init__(pos_vec2d, image, anim_len, mode, *groups, **kwargs)
        self._frame_dt = self._orig_frame_dt = 1000/fps
        self._last_update = 0
        self._current_time = 0

    def update(self, dt, t, *args, **kwargs):
        self.rect.center = self.pos
        self._current_time += dt
        if self._running:
            if self._current_time - self._last_update > self._frame_dt:
                self._last_update += self._frame_dt
                super(TimedAnimation, self).update(dt, t, *args, **kwargs)
        else:
            self._last_update += dt
            
    def set_fps(self, fps):
        self._frame_dt = 1000/fps
        
    def reset_fps(self):
        self._frame_dt = self._orig_frame_dt


    def play(self):
        # Don't reset the timing if we're already playing.
        # This way multiple calls to play won't slow the animation down.
        if not self._running:
            self._last_update = self._current_time
        super(TimedAnimation, self).play()

if __name__ == '__main__':
    import sys
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    ball_frames = pygame.image.load(data.filepath('strip.png')).convert()
 
    anim_test = None
    if len(sys.argv) == 4:
        anim_test = TimedAnimation([250, 400], data.load_image(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), 'loop')
    else:
        print 'usage animation.py myimage.png numframes, fps,'
   
    anim = FrameAnimation([100, 200], ball_frames, 20, 'loop')
    anim2 = TimedAnimation([250, 200], ball_frames, 20, 10, 'once')
    anim3 = TimedAnimation([400, 200], ball_frames, 20, 30, 'loop')
    anim4 = TimedAnimation([550, 200], ball_frames, 20, 30, 'pingpong')
 
    anim.play()
    anim2.play()
    anim3.play()
    anim4.play()
    if anim_test:
        anim_test.play()
 
    clock = pygame.time.Clock()
    current_time = pygame.time.get_ticks()
 
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                elif event.key == pygame.K_SPACE:
                    if anim.is_running():
                        anim.pause()
                        anim2.pause()
                        anim3.pause()
                        anim4.pause()
                    else:
                        anim.play()
                        anim2.play()
                        anim3.play()
                        anim4.play()
 
        screen.fill((255,255,255))
 
        anim.render(screen, 1000/30, current_time)
        anim2.render(screen, 1000/30, current_time)
        anim3.render(screen, 1000/30, current_time)
        anim4.render(screen, 1000/30, current_time)
        if anim_test:
            anim_test.render(screen, 1000/30, current_time)
 
        pygame.display.flip()
 
        anim.update(1000/30, current_time)
        anim2.update(1000/30, current_time)
        anim3.update(1000/30, current_time)
        anim4.update(1000/30, current_time)
        if anim_test:
            anim_test.update(1000/30, current_time)
 
        current_time += 1000/30
        clock.tick(30)
