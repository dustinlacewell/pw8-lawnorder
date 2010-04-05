#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: states.py 413 2009-05-02 22:19:00Z dr0iddr0id $'


import os
import glob

import pygame
from pygame.locals import *
import data
import gamelib

import events

from constants import *
#-------------------------------------------------------------------------------

TheStateManager = None

#-------------------------------------------------------------------------------

class StateManager(object):

    def __init__(self, first_state, size=(SCREENWIDTH, SCREENHEIGHT), flags=None, framerate=FRAMERATE):
        global TheStateManager
        TheStateManager = self
        
        self._framerate = framerate
        self.time = 0
        
        pygame.init()
        pygame.display.set_caption("Law(n) & order")
        if flags:
            self.screen = pygame.display.set_mode(size, flags)
        else:
            self.screen = pygame.display.set_mode(size)
        
        self.clock = pygame.time.Clock()
        
        self._cur_state = first_state
        self._states = [first_state]
        self._cur_state.on_init()
        self._commands = [] # [(1,new),(2,None) ]  1 pop, 2 push
        self._running = True


    cur_state = property(lambda self: self._cur_state, doc='readonly')

    def run(self):
        clock_tick = self.clock.tick
        get_events = pygame.event.get
        flip = pygame.display.flip
        while self._states and self._running:
            dt = clock_tick(self._framerate)
            # filter high spikes
            dt = min(100, dt)
            self.time += dt
            cur_state = self._cur_state
            cur_state.handle_events(get_events())
            cur_state.update(dt, self.time)
            cur_state.render(self.screen, dt, self.time)
            flip()
            if self._commands:
                while self._commands:
                    cmd, new_state = self._commands.pop(0)
                    if cmd == 1: # pop
                        self._cur_state.on_exit()
                        self._states.pop(0)
                        if self._states:
                            self._cur_state = self._states[0]
                            self._cur_state.on_resume()
                    else: # push
                        self._cur_state.on_pause()
                        self._cur_state = new_state
                        self._cur_state.on_init()
                        self._states.insert(0, new_state)

    def push(self, new_state):
        self._commands.append((2, new_state))

    def pop(self):
        self._commands.append((1, None))

    def clear(self):
        while self._states:
            self.pop()

    def quit(self):
        self._running = False

#-------------------------------------------------------------------------------

class State(object):

    def __init__(self, *args, **kwargs):
        pass

    #-- state handling --#
    def on_init(self, *args, **kwargs):
        pass

    def on_exit(self, *args, **kwargs):
        pass

    def on_pause(self, *args, **kwargs):
        pass

    def on_resume(self, *args, **kwargs):
        pass

    #-- per frame updates --#
    def update(self, dt, t, *args, **kwargs):
        pass

    def handle_events(self, events, *args, **kwargs):
        for event in events:
            if KEYDOWN == event.type:
                if K_ESCAPE == event.key:
                    TheStateManager.pop()
                elif K_F3 == event.key:
                    self.take_screenshot()
            elif QUIT == event.type:
                TheStateManager.pop()

    def render(self, screen_surf, dt, t, *args, **kwargs):
        pass

    #-- util --#

    def take_screenshot(self):
        # screenshot_000.png
        ext = 'png'
        save_path = os.path.abspath(data.filepath(os.path.join(os.pardir,'screenshots')))
        query = os.path.join(save_path, '*.' + ext)
        image_names = glob.iglob(query)
        num = 0
        for image_name_full in image_names:
            image_name = os.path.split(image_name_full)[1]
            name, imgext = image_name.split('.')
            prefix, img_num = name.split('_')
            if int(img_num)>num:
                num = int(img_num)
        new_name = os.path.join(save_path,'screenschot_' + str(num + 1) + '.' + ext)
        if pygame.display.get_init():
            pygame.image.save(pygame.display.get_surface(), new_name)
            print 'saved screenshot at %s' %(new_name)

#-------------------------------------------------------------------------------

class GameOptions(object):
    is_multiplayer = False
    duration = 120 * 1000


#-------------------------------------------------------------------------------
class GameMain(StateManager):

    def __init__(self, first_state, size=(SCREENWIDTH, SCREENHEIGHT), flags=None, framerate=FRAMERATE):
        super(GameMain, self).__init__(first_state, size, flags, framerate)
        self.game_options = GameOptions()



if __name__ == '__main__':
    
    class TestState(State):
        def __init__(self, name='TestState'):
            super(TestState, self).__init__()
            self.name = name
            if gamelib.DEBUG: print '%s __init__' % self.name
        #-- state handling --#
        def on_init(self, *args, **kwargs):
            if gamelib.DEBUG: print '%s on_init' % self.name
        def on_exit(self, *args, **kwargs):
            if gamelib.DEBUG: print '%s on_exit' % self.name
        def on_pause(self, *args, **kwargs):
            if gamelib.DEBUG: print '%s on_pause' % self.name
        def on_resume(self, *args, **kwargs):
            if gamelib.DEBUG: print '%s on_resume' % self.name
        #-- per frame updates --#
        def update(self, *args, **kwargs):
            if gamelib.DEBUG: print '%s update' % self.name
        def handle_events(self, events, *args, **kwargs):
            if gamelib.DEBUG: print '%s handle_events' % self.name
            for event in events:
                if pygame.locals.KEYDOWN == event.type:
                    if K_n == event.key:
                        TheStateManager.push(TestState('NestedSTate'))
                    elif pygame.locals.K_b == event.key:
                        TheStateManager.pop()
                    elif K_ESCAPE == event.key:
                        TheStateManager.quit()
                    elif K_F3 == event.key:
                        self.take_screenshot()
        def render(self, *args, **kwargs):
            if gamelib.DEBUG: print '%s render' % self.name

    StateManager(TestState()).run()
