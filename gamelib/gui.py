#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: gui.py 404 2009-05-02 20:24:12Z pekuja $'

import string
import pygame

from pygame.locals import *

import data
import events
import gradients

#-------------------------------------------------------------------------------
class UIElement(object):
      def __init__(self):
            self.rect = pygame.Rect(0,0,0,0)

      def hit(self, x, y):
            return self.rect.collidepoint(x, y)

      def handle_event(self, event):
            raise NotImplementedError

      def render(self, surf, *args, **kwargs):
            raise NotImplementedError

#-------------------------------------------------------------------------------
class Button(object):

    NORMAL, HOVER, PRESSED, DISABLED = range(4)

    def __init__(self, pos, size, state_images, do_resize=False):
        super(Button, self).__init__()

        # states: 0=normal, 1=hover, 2=pressed, 3=disabled
        self._images = state_images
        self.rect = pygame.Rect(pos, size)
        self.rect.center = pos
        self.state = self.NORMAL
        # resize images to fit button size
        if do_resize:
            for idx, img in enumerate(self._images):
                self._images[idx] = pygame.transform.smoothscale(img, self.rect.size)
        self.image = self._images[0]
        self.event_clicked = events.Event()

    def hit(self, x, y):
        return self.rect.collidepoint(x, y)

    def handle_event(self, event):
        if MOUSEMOTION == event.type:
            if not self.state == self.PRESSED:
                p = event.pos
                if self.hit(*p) and event.buttons == (0, 0, 0):
                    self.state = self.HOVER
                else:
                    self.state = self.NORMAL
        elif MOUSEBUTTONDOWN == event.type:
            p = event.pos
            if self.hit(*p):
                self.state = self.PRESSED
        elif MOUSEBUTTONUP == event.type:
            p = event.pos
            if self.hit(*p) and self.state == self.PRESSED:
                self.event_clicked() # TODO: maybe pass some data?
            self.state = self.NORMAL
        else:
            self.state = self.NORMAL

    def render(self, surf, *args, **kwargs):
        img = self._images[self.state]
        if isinstance(img, pygame.Surface):
            rect = img.get_rect()
            rect.center = self.rect.center
            surf.blit(img, rect)
        else:
            img.render(surf, *args)
#-------------------------------------------------------------------------------
class MenuEntry(Button):

    def __init__(self, text, pos, size, norm_col=(255, 242, 0), hover_col=(251, 176, 4), pressed_col=(202, 251, 4), disabled_col=(151, 146, 104), colorkey=None):
        self.font_name = data.filepath('fonts/actionman.ttf')
        normal = BitmapFont(size, fontname=self.font_name, color=norm_col,).render(text, colorkey=colorkey, monospaced=False)
        hover = BitmapFont(size, fontname=self.font_name, color=hover_col).render(text, colorkey=colorkey, monospaced=False)
        pressed = BitmapFont(size, fontname=self.font_name, color=pressed_col).render(text, colorkey=colorkey, monospaced=False)
        disabled = BitmapFont(size*0.8, fontname=self.font_name, color=disabled_col).render(text, colorkey=colorkey, monospaced=False)
        img_size = hover.get_size()
        super(MenuEntry, self).__init__(pos, img_size, [normal, hover, pressed, disabled])

#-------------------------------------------------------------------------------
class Label(object):

    def __init__(self, text, pos, size, color=None, fontname=None, aa=False):
        super(Label, self).__init__()
        self.__font = pygame.font.Font(fontname, size)
        self.__surface = None
        self.__pos = pos
        self.__size = size
        self.__aa = False
        self.__fontname = fontname
        if not color:
            color = pygame.Color(128, 128, 128)
        self.__color = color

        self.__set_text(text)

    # PROPERTIES BEGIN
    # TEXT
    def __set_text(self, text):
        self.__text = text
        self.__prerender()
    def __get_text(self): return self.__text
    text = property(__get_text, __set_text)
    
    # POSITION
    def __set_pos(self, pos):
        self.__pos = pos
        self.__prerender()
    def __get_pos(self): return self.__pos
    position = property(__get_pos, __set_pos)

    # SIZE
    def __set_size(self, size):
        self.__size = max(0, size)
        self.__size = min(self.__size, 128)
        self.__prerender()
    def __get_size(self): return self.__size
    size = property(__get_size, __set_size)
    
    # COLOR
    def __set_color(self, color):
        self.__color = color
        self.__prerender()
    def __get_color(self): return self.__color
    color = property(__get_color, __set_color)
    
    # ALIASING
    def __set_aa(self, aa):
        self.__aa = aa
        self.__prerender()
    def __get_aa(self): return self.__aa
    aliasing = property(__get_aa, __set_aa)
    
    # FONTNAME
    def __set_font(self, fontname):
        self.__fontname = fontname
        self.font = pygame.font.Font(fontname, self.size)
        self.__prerender()
    def __get_font(self): return self.__fontname
    fontname = property(__get_font, __set_font)

    def __prerender(self):
        self.__surface = self.__font.render(self.__text, self.aliasing, self.color)
        self.rect = self.__surface.get_rect()
        self.rect.center = self.position

    def hit(self, x, y):
        return self.rect.collidepoint(x, y)

    def handle_event(self, event):
        pass

    def render(self, surf, *args, **kwargs):
        surf.blit(self.__surface, self.rect)


#-------------------------------------------------------------------------------

class BitmapFont(object):

    cache = {} # {(fontname, size, alias, color, bgdcolor):BitmapFont}

    def __new__(cls, size, antialias=0, fontname=None, color=(255, 255, 255), bgcolor=None):
        # return the cached font
        key = (size, antialias, fontname, color, bgcolor)
        if key in cls.cache:
            return cls.cache[key]
        else:
            return super(BitmapFont, cls).__new__(cls)#, size, antialias, fontname, color, bgcolor) 

    def __init__(self, size, antialias=0, fontname=None, color=(255, 255, 255), bgcolor=None):
        # cache the font
        BitmapFont.cache[(size, antialias, fontname, color, bgcolor)] = self
        self.img_chars = {}
        self.shadow_chars = {}
        self.metrics = {}
        font = pygame.font.Font(fontname, int(size))
        self.width = 0
        self.height = 0
        for char in string.printable:
            if bgcolor:
                img = font.render(char, antialias, color)#, bgcolor)
                shadow = font.render(char, antialias, (50,50,50), bgcolor)
            else:
                img = font.render(char, antialias, color)
                shadow = font.render(char, antialias, (50,50,50))
            self.metrics[char] = font.metrics(char)[0]
            self.img_chars[char] = img
            self.shadow_chars[char] = shadow
            w, h = img.get_size()
            if w > self.width:
                self.width = w
            if h > self.height:
                self.height = h

        self.height += 3
        self.width += 3

    def render(self, text, colorkey=None, monospaced=True):
        # TODO: it is just monospaced only
        text = str(text)
        if monospaced:
            w = self.width * len(text)
            surf = pygame.Surface((w, self.height)).convert()
            for idx, char in enumerate(text):
                surf.blit(self.shadow_chars.get(char, string.whitespace), (idx * self.width + 3, 3))
                surf.blit(self.img_chars.get(char, string.whitespace), (idx * self.width, 0))
        else:
            w = 0
            for char in text:
                w += self.metrics[char][4]
            surf = pygame.Surface((w, self.height)).convert()
            xpos = 0
            for idx, char in enumerate(text):
                surf.blit(self.shadow_chars.get(char, string.whitespace), (xpos + 3, 3))
                surf.blit(self.img_chars.get(char, string.whitespace), (xpos, 0))
                xpos += self.metrics[char][4]
            
        if colorkey:
            surf.set_colorkey(colorkey)
        return surf

    @classmethod
    def clear(cls):
        cls.cache.clear()


#-------------------------------------------------------------------------------

class HealthBar(object):

    def __init__(self, pos, min_points, max_points, size, color):
        self.images = {}
        self.pos = pos
        self.min_points = min_points
        self.max_points = max_points
        self.max_sub_min = max_points - min_points
        for i in range(100+1):
            surf = pygame.Surface(size).convert()
            surf.fill((255, 0, 255))
            surf.set_colorkey((255, 0, 255))
            h = size[1] * i * 0.01
            if h:
                rect = pygame.Rect(0, size[1] - h, size[0], h)
                r, g, b = color
                tmp = gradients.vertical(rect.size, (r, g, b, 255), (255, 0, 0,  255)).convert()
                surf.blit(tmp, rect)
                #surf.fill(color, rect)
            pygame.draw.rect(surf, color, surf.get_rect(), 1)
            self.images[i] = surf

    def set_health(self, health):
        assert health <= self.max_points and health >= self.min_points, 'healt = %s' % health
        key = int(100 * (health - self.min_points) / self.max_sub_min)
        # make sure that key is in range [0,100]
        key = min(100, max(key, 0))
        self.image = self.images[key]

    def render(self, screen, dt, t):
        screen.blit(self.image, self.pos)

