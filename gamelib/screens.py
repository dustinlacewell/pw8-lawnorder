#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: screens.py 422 2009-05-02 23:44:45Z pekuja $'
from random import randint


import pygame
from pygame.locals import *
import states
import data
import gui
import utility, animation
import string
import gamelib

from constants import *
from geometry import Entity
from geometry import Vec2D
from entities import *
import data


sky = None

class SplashScreen(states.State):
    def __init__(self, *args, **kwargs):
        super(SplashScreen, self).__init__(*args, **kwargs)

    def on_init(self, *args, **kwargs):
        global sky
        if not sky:
            sky = utility.Bgd()
        self.sky = sky

        self.scenery = pygame.image.load(data.filepath('lawn1.png'))
        self.splashorig = pygame.image.load(data.filepath('splash.png'))
        self.splash = pygame.image.load(data.filepath('splash.png'))
        
        self.fadeTime = SPLASHTIME
        self.fadeElapsed = None
        
    def handle_events(self, events, *args, **kwargs):
        for event in events:
            if event.type == MOUSEBUTTONDOWN or event.type == KEYDOWN:
                if event.type == KEYDOWN and event.key == K_F3:
                    self.take_screenshot()
                else:
                    if self.fadeElapsed == None:
                        self.fadeElapsed = 0.0

    def update(self, dt, t):
        self.sky.update(dt, t)
        if self.fadeElapsed != None:
            self.fadeElapsed += dt
            self.splash = pygame.transform.rotozoom(self.splashorig,
                SPLASHROT*self.fadeElapsed, 1 - (SPLASHSCALE* self.fadeElapsed))
            
        if self.fadeElapsed >= self.fadeTime:
            states.TheStateManager.pop()
            states.TheStateManager.push(MainMenu())
        
    def render(self, screen, dt, t, *args, **kwargs):
        self.sky.render(screen, dt, t)
        screen.blit(self.scenery, (0, 0))
        x = screen.get_rect().centerx  - (self.splash.get_width() / 2.0)
        y = screen.get_rect().centery  - (self.splash.get_height() / 2.0)
        screen.blit(self.splash, (x, y))

#-------------------------------------------------------------------------------
class Splash2(states.State):

    def on_init(self):
        self.splash = pygame.image.load(data.filepath('law_and_order.png'))
        self.snd = data.load_sound(data.filepath('sfx/intro.wav')).play()
        self.played = False
        self.pos = Vec2D(400, -50)
        self.accel = Vec2D(0, 0.0025)
        self.vel = Vec2D(0, 0)
        self.run_time = 0.0
        self.target_time = 900.0

    def update(self, dt, t):
        self.run_time += dt
        if self.run_time >= self.target_time:
            ground = 450
            if self.pos.y >= ground:
                self.vel *= -0.2
                self.pos.y = ground
            self.vel += dt * self.accel
            self.pos += dt * self.vel
                
            #self.pos.y = ground #- randint(0, 20)

    def render(self, screen, dt, t):
        screen.fill((0, 0, 0))
        rect = self.splash.get_rect()
        rect.midbottom = self.pos
        screen.blit(self.splash, rect)

    def handle_events(self, events, *args, **kwargs):
        for event in events:
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                states.TheStateManager.pop()
                states.TheStateManager.push(MainMenu())
            elif event.type == QUIT:
                states.TheStateManager.quit()
            


#-------------------------------------------------------------------------------

class MainMenu(states.State):

    def __init__(self, *args, **kwargs):
        super(MainMenu, self).__init__(*args, **kwargs)
        self.entries = []
        self.focus_item = 0
        self.num_buttons = 0

        self.bg = utility.Bgd()
        self.lawn = data.load_image("lawn1.png")

        if pygame.mixer.music.get_pos() <= 0:
            pygame.mixer.music.load(data.filepath('JDruid-The_lawn_and_the_ladybug.ogg'))
            pygame.mixer.music.play(-1)

    def on_init(self, *args, **kwargs):
        exit = gui.MenuEntry('Single Player', (400, 80), 50, colorkey=(0,0,0))
        exit.event_clicked += self.on_singleplayer
        self.entries.append(exit)

        exit = gui.MenuEntry('Multi Player', (400, 160), 50, colorkey=(0,0,0))
        exit.event_clicked += self.on_multiplayer
        self.entries.append(exit)

        #exit = gui.MenuEntry('Options', (400, 240), 50, colorkey=(0,0,0))
        #exit.event_clicked += self.on_options
        #self.entries.append(exit)

        exit = gui.MenuEntry('Credits', (400, 240), 50, colorkey=(0,0,0))
        exit.event_clicked += self.on_credits
        self.entries.append(exit)

        exit = gui.MenuEntry('Exit', (400, 320), 50, colorkey=(0,0,0))
        exit.event_clicked += self.on_quit
        self.entries.append(exit)
        self.focus_item = 0
        self.num_buttons = 4

        self.entries[self.focus_item].state = gui.MenuEntry.HOVER
        
    #-- button click handlers --#
    def on_quit(self, *args, **kwargs):
        states.TheStateManager.push(AreYouSureMenu())

    def on_singleplayer(self):
        states.TheStateManager.push(Game())

    def on_multiplayer(self):
        states.TheStateManager.game_options.is_multiplayer = True
        states.TheStateManager.push(Game())

    def on_options(self):
        pass

    def on_credits(self):
        #states.TheStateManager.push(Credits())
        states.TheStateManager.push(SplashScreen())

    #-- per frame updates --#
    def handle_events(self, events, *args, **kwargs):
        for event in events:
            if KEYDOWN == event.type:
                if K_ESCAPE == event.key:
                    self.on_quit()
                elif K_F3 == event.key:
                    self.take_screenshot()
                elif K_UP == event.key or K_w == event.key:
                    self.focus_item -= 1
                elif K_LEFT == event.key or K_a == event.key:
                    self.focus_item = 1 # This is very hackish
                elif K_DOWN == event.key or K_s == event.key:
                    self.focus_item += 1
                elif K_d == event.key or K_RIGHT == event.key:
                    self.focus_item = 0 # Very hackish
                elif K_RETURN == event.key or K_SPACE == event.key:
                    self.entries[self.focus_item].event_clicked()
                    
                for entry in self.entries:
                    entry.handle_event(event)
                self.focus_item %= self.num_buttons
                self.entries[self.focus_item].state = gui.MenuEntry.HOVER
            elif KEYUP == event.type:
                pass
            elif QUIT == event.type:
                self.on_quit()
            else:
                for entry in self.entries:
                    entry.handle_event(event)
        
    def update(self, dt, t):
        self.bg.update(dt, t)
        

    def render(self, screen_surf, dt, t, *args, **kwargs):
        #screen_surf.fill((200, 200, 250))
        self.bg.render(screen_surf, dt, t)
        screen_surf.blit(self.lawn, (0,0))
        self.bg.render_night(screen_surf, dt, t)
        for entry in self.entries:
            entry.render(screen_surf, dt, t)

#-------------------------------------------------------------------------------
class OptionsMenu(MainMenu):

    def on_init(self, *args, **kwargs):
        pass
        
#-------------------------------------------------------------------------------
class AreYouSureMenu(MainMenu):

    def on_init(self, *args, **kwargs):
        left, right = 266, 800 - 266
        exit = gui.MenuEntry('Yes', (right, 300), 50, colorkey=(0,0,0))
        exit.event_clicked += self.on_quit
        self.entries.append(exit)
        back = gui.MenuEntry('No', (left, 300), 50, colorkey=(0,0,0))
        back.event_clicked += self.on_back
        self.entries.append(back)
        
        self.bitmapfont = gui.BitmapFont(30, fontname=data.filepath('fonts/actionman.ttf'), color=(255, 255, 0))
        
#        self.label = gui.Label('Sure you want to quit?', (400, 100), 40)
        self.num_buttons = 2

        self.entries[self.focus_item].state = gui.MenuEntry.HOVER

    def on_quit(self):
        states.TheStateManager.quit()

    def on_back(self):
        states.TheStateManager.pop()

    def render(self, screen, dt, t):
        super(AreYouSureMenu, self).render(screen, dt, t)
        surf = self.bitmapfont.render('Sure you want to quit?', (0, 0, 0))
        srect = surf.get_rect()
        srect.midtop = (400, 200)
        screen.blit(surf, srect)
        
#        self.label.render(screen, dt, t)

#-------------------------------------------------------------------------------
class Credits(states.State):

    def on_init(self, *args, **kwargs):
        self.img = pygame.image.load(data.filepath('splash.png'))

    def handle_events(self, events, *args, **kwargs):
        for event in events:
            if KEYDOWN == event.type:
                if K_F3 == event.key:
                    self.take_screenshot()
                else:
                    states.TheStateManager.pop()
            elif QUIT == event.type:
                states.TheStateManager.pop()
            elif MOUSEBUTTONDOWN == event.type:
                states.TheStateManager.pop()

    def render(self, screen_surf, dt, t, *args, **kwargs):
        screen_surf.fill((127, 127, 127))
        screen_surf.blit(self.img, (0, 0))
#-------------------------------------------------------------------------------
class AreYouSureBreakGameMenu(MainMenu):

    def on_init(self, *args, **kwargs):
        self.bgd = pygame.display.get_surface().copy()
        exit = gui.MenuEntry('Yes', (800 - 266, 300), 70, colorkey=(0, 0, 0))
        exit.event_clicked += self.on_quit
        self.entries.append(exit)
        back = gui.MenuEntry('No', (266, 300), 70, colorkey=(0, 0, 0))
        back.event_clicked += self.on_back
        self.entries.append(back)
        
        self.bitmapfont = gui.BitmapFont(30, fontname=data.filepath('fonts/actionman.ttf'), color=(255, 255, 0))
#        self.label = gui.Label('Go back to main menu?', (400, 100), 50, color=(25, 0, 25))
        self.num_buttons = 2
        self.entries[self.focus_item].state = gui.MenuEntry.HOVER

    def on_quit(self):
        states.TheStateManager.pop()
        states.TheStateManager.pop()

    def on_back(self):
        states.TheStateManager.pop()

    def render(self, screen, dt, t):
        screen.blit(self.bgd, (0, 0))
        #super(AreYouSureBreakGameMenu, self).render(screen, dt, t)
        for entry in self.entries:
            entry.render(screen, dt, t)
        
        surf = self.bitmapfont.render('Go back to main menu?', (0, 0, 0))
        srect = surf.get_rect()
        srect.midtop = (400, 200)
        screen.blit(surf, srect)

#        self.label.render(screen, dt, t)

#-------------------------------------------------------------------------------
class GameEndMenu(MainMenu):

    def __init__(self, msg):
        super(GameEndMenu, self).__init__()
        self.msg = msg

    def on_init(self, *args, **kwargs):
        self.bgd = pygame.display.get_surface().copy()


        back = gui.MenuEntry('Yes', (800 - 266, 300), 70, colorkey=(0, 0, 0))
        back.event_clicked += self.on_back
        self.entries.append(back)

        exit = gui.MenuEntry('No', (266, 300), 70, colorkey=(0, 0, 0))
        exit.event_clicked += self.on_quit
        self.entries.append(exit)

        self.bitmapfont = gui.BitmapFont(30, fontname=data.filepath('fonts/actionman.ttf'), color=(255, 255, 0))

        self.num_buttons = 2
        self.entries[self.focus_item].state = gui.MenuEntry.HOVER

    def on_back(self):
        multiplayer = states.TheStateManager._states[1].multiplayer
        duration = states.TheStateManager._states[1].duration
        states.TheStateManager.pop()
        states.TheStateManager.pop()
        states.TheStateManager.push(Game())

    def on_quit(self):
        states.TheStateManager.pop()
        states.TheStateManager.pop()

    def render(self, screen, dt, t):
        screen.blit(self.bgd, (0, 0))
        for entry in self.entries:
            entry.render(screen, dt, t)
        
        surf = self.bitmapfont.render('Time is up, play again?', (0, 0, 0))
        srect = surf.get_rect()
        srect.midtop = (400, 100)
        screen.blit(surf, srect)
        
        surf = self.bitmapfont.render(self.msg, (0, 0, 0))
        srect = surf.get_rect()
        srect.midtop = (400, 200)
        screen.blit(surf, srect)

#-------------------------------------------------------------------------------

class Game(states.State):

    def __init__(self, *args, **kwargs):
        super(Game, self).__init__(*args, **kwargs)
        options = states.TheStateManager.game_options
        self.multiplayer = options.is_multiplayer
        self.duration = options.duration
        self.end_time = 0

    def on_init(self, *args, **kwargs):
        # background
        self.bgd = pygame.image.load(data.filepath('lawn1.png'))
        self.lawn = LawnManager()
        global sky
        if not sky:
            sky = utility.Bgd()
        self.sky = sky
        
        # time
        if self.duration:
            self.end_time = states.TheStateManager.time + self.duration
        else:
            self.end_time = states.TheStateManager.time
        
        # gui
        self.bitmapfont = gui.BitmapFont(30, fontname=data.filepath('fonts/actionman.ttf'), color=(255, 255, 0))
        self._show_fps = False
        self.healbar_L = gui.HealthBar((20, 20), 0, 10*LawnSegment.MAXHEALTH, (20, 100), (0, 200, 0))
        self.healbar_R = gui.HealthBar((800-40, 20), 0, 10*LawnSegment.MAXHEALTH, (20, 100), (200, 200, 0))
        
        font = pygame.font.Font(None, 40)
        self.welcome_image = font.render('Debug', 3, (255, 255, 255))
        self.rect = self.welcome_image.get_rect()
        screen_rect = states.TheStateManager.screen.get_rect()
        self.rect.center = screen_rect.center
        
        # players
        self.players = [Player(), NPCharacter()]
        if self.multiplayer:
            self.players = [Player(), Player()]
            # init player 2 with different keys
            player2 = self.players[1]
            player2.actionkey_pickup = pygame.K_k
            player2.actionkey_throw = pygame.K_i
            player2.actionkey_walk_l = pygame.K_j
            player2.actionkey_walk_r = pygame.K_l
            player2.side = 1
            
        # stuff
        self.stuff = []
        for i in range(3):
            self.stuff.append(FlyObj((i*80, 350)))
        for i in range(10):
            self.stuff.append(Bird())
        for i in range(2):
            self.stuff.append(LadyBug())
            self.stuff.append(Carterpilar())
        
        self.stuff.append(Mole())
        self.stuff.append(WateringCan(Vec2D(100, 200)))
        self.stuff.append(WateringCan(Vec2D(700, 200)))

    def check_game_end(self, dt, t):
        if self.duration:
            if t >= self.end_time:
                msg = 'Right player wins!'
                if self.lawn.left_score() > self.lawn.right_score():
                    msg = 'Left player wins!'
                states.TheStateManager.push(GameEndMenu(msg))

    def on_exit(self, *args, **kwargs):
        pygame.mixer.stop()

    def on_pause(self, *args, **kwargs):
        self.pause_start_time = states.TheStateManager.time
        pygame.mixer.stop()

    def on_resume(self, *args, **kwargs):
        self.end_time = self.end_time - self.pause_start_time + states.TheStateManager.time
        for player in self.players:
            if isinstance(player, Player):
                player.kdir = 0

    def add_entity(self, entity):
        self.stuff.append(entity)

    def remove_entity(self, entity):
        if entity in self.stuff:
            self.stuff.remove(entity)
            
    def get_collection(self, pos, kind=None, kinds=None):
        lawn = states.TheStateManager.cur_state.lawn
        # Filter Side
        if pos < FENCELEFT:
            ret = [item for item in self.stuff if item.pos.x < FENCELEFT]
        elif pos > FENCERIGHT:
            ret = [item for item in self.stuff if item.pos.x > FENCERIGHT]
        else:
            ret = []
        # Filter Type
        if kind:
            ret = [item for item in ret if isinstance(item, kind)]
        elif kinds:
            filter_ret = []
            for item in ret:
                for k in kinds:
                    if isinstance(item, k): filter_ret.append(item)
            ret = filter_ret
        return ret
            
        
            
    def find_dirty(self, pos):
        lawn = states.TheStateManager.cur_state.lawn
        if pos < FENCELEFT:
            side = 'left'
            start = lawn.left_start
        elif pos > FENCERIGHT:
            side = 'right'
            start = lawn.right_start
        else:
            return None
        closest = (None, 999)
        for idx, ent in enumerate(states.TheStateManager.cur_state.lawn.segments[side]):
            if gamelib.DEBUG: print "Dirty search: ", idx, ent.hitpoints, closest[1]
            if ent.hitpoints < closest[1]:
                closest = (idx, ent.hitpoints)
                
        if closest[0] is not None:
            return start + (closest[0] * 40), closest[1]
        return None
        
    def find_mole(self):
        mole = None
        for ent in self.stuff:
            if isinstance(ent, Mole) and ent.pos.x > FENCERIGHT and isinstance(ent.cur_state, Mole.StatePopup):
                mole = ent
        return mole
            
    def find_closest(self, pos, radius, kind=None):
        # returns (kind, pos)
        if pos < FENCELEFT:
            side = 1
        elif pos > FENCERIGHT:
            side = 2
        else: return None
        closest = (None, 999)
        if not kind:
                filter = FlyObj
        else:
            filter = kind
        for ent in self.stuff:
            if isinstance(ent, filter) and ent.pickupable:
                if side == 1 and ent.pos.x < FENCEMIDDLE:
                    dist = abs(ent.pos.x - pos)
                    if dist < closest[1] and dist < radius:
                        closest = (ent, dist)
                elif side == 2 and ent.pos.x > FENCEMIDDLE:
                    dist = abs(ent.pos.x - pos)
                    if dist < closest[1] and dist < radius:
                        closest = (ent, dist)
        if closest[0]:
            return (closest[0].__class__, closest[0].pos.x)
        else:
            return None
            
    def get_closest(self, pos, radius, kind=None):
        if pos < FENCELEFT:
            side = 1
        elif pos > FENCERIGHT:
            side = 2
        else: return None
        closest = (None, 999)
        if not kind:
                filter = FlyObj
        else:
            filter = kind
        for ent in self.stuff:
            if isinstance(ent, filter) and ent.pickupable:
                if side == 1 and ent.pos.x < FENCEMIDDLE:
                    dist = abs(ent.pos.x - pos)
                    if dist < closest[1] and dist < radius:
                        closest = (ent, dist)
                elif side == 2 and ent.pos.x > FENCEMIDDLE:
                    dist = abs(ent.pos.x - pos)
                    if dist < closest[1] and dist < radius:
                        closest = (ent, dist)
        if closest[0]:
            return (closest[0], closest[0].pos.x)
        else:
            return None

    def handle_events(self, events,  *args, **kwargs):
        for event in events:
            if KEYDOWN == event.type:
                if event.key == K_F2:
                    self._show_fps = not self._show_fps
                elif K_ESCAPE == event.key:
                    states.TheStateManager.push(AreYouSureBreakGameMenu())
                elif K_F3 == event.key:
                    self.take_screenshot()
                elif K_F1 == event.key:
                    gamelib.toggle_debug()
            elif QUIT == event.type:
                states.TheStateManager.push(AreYouSureBreakGameMenu())
            
            for player in self.players:
                player.handle_event(event)

    def update(self, dt, t):
        self.sky.update(dt, t)
        self.lawn.update(dt, t)
        for player in self.players:
            player.update(dt, t)
        for obj in self.stuff:
            obj.update(dt, t)
        self.check_collision()
        self.healbar_L.set_health(self.lawn.left_score())
        self.healbar_R.set_health(self.lawn.right_score())
        self.check_game_end(dt, t)

    def render(self, screen, dt, t, *args, **kwargs):
        # background
        self.sky.render(screen, dt, t)
        screen.blit(self.bgd, (0, 0))
        # player
        for player in self.players:
            player.render(screen, dt, t)
            if gamelib.DEBUG:
                pygame.draw.rect(screen, (255, 0, 0), player.rect, 5)
                pygame.draw.rect(screen, (0, 255, 0), player.spr.rect, 2)
        
        # stuff
        for obj in self.stuff:
            obj.render(screen, dt, t)
            if gamelib.DEBUG:
                pygame.draw.rect(screen, (255, 0, 0), obj.rect, 5)
                pygame.draw.rect(screen, (0, 255, 0), obj.spr.rect, 2)
        # darkening
        # grass
        self.lawn.render(screen, dt, t)
        self.sky.render_night(screen, dt, t)
        # gui
        if gamelib.DEBUG:
            screen.blit(self.welcome_image, self.rect)
        if self._show_fps:
            screen.blit(self.bitmapfont.render('fps:'+str(int(states.TheStateManager.clock.get_fps())), (0, 0, 0)), (400, 440))
        # left healtbar
        self.healbar_L.render(screen, dt, t)
        screen.blit(self.bitmapfont.render(int(self.lawn.left_score()), (0, 0, 0)), (20, 125))
        # right healtbar
        self.healbar_R.render(screen, dt, t)
        s = self.bitmapfont.render(int(self.lawn.right_score()), (0, 0, 0))
        screen.blit(s, (800-20-s.get_rect().w, 125))
        if self.duration:
            seconds = (self.end_time - t) / 1000
        else:
            seconds = (t - self.end_time) / 1000
        if seconds < 0:
            seconds = 0
        minutes = seconds / 60
        seconds = seconds % 60
        points = ':'
        if t % 1000 > 500:
            points = ' '
        seconds = max(0, seconds)
        minutes = max(0, minutes)
        s = self.bitmapfont.render('%02i%s%02i' %(minutes, points,  seconds), (0, 0, 0))
        r = s.get_rect()
        r.center = (400, 40)
        screen.blit(s, r)

    def check_collision(self):
        for player in self.players:
            for idx in player.spr.rect.collidelistall(self.stuff):
                obj = self.stuff[idx]
                player.collision_response(obj)
                obj.collision_response(player)
        stuff = list(self.stuff)
        while stuff:
            obj = stuff.pop()
            self.lawn.check_collisions(obj)
            idx = obj.rect.collidelist(stuff)
            if idx > -1:
                obj.collision_response(stuff[idx])
            
