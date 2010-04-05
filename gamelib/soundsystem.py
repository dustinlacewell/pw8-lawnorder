from data import load_sound
import random
import os

class SoundSystem:
    _eat = None
    _poop = None
    _water = None
    _current_water = None
    _grunt = None

def init():
    SoundSystem._eat = [load_sound("eat1.wav"),
            load_sound("eat2.wav"),
            load_sound("eat3.wav")]
    SoundSystem._poop = [load_sound("poop.wav")]
    SoundSystem._water = [load_sound("water.wav")]
    SoundSystem._grunt = [load_sound(os.path.join("grunt", "grunt.oga")),
              load_sound(os.path.join("grunt", "grunt2.oga")),
              load_sound(os.path.join("grunt", "grunt3.oga")),
              load_sound(os.path.join("grunt", "grunt4.oga"))]

def eat():
    if not SoundSystem._eat:
        init()
    sound = random.choice(SoundSystem._eat)
    sound.set_volume(0.5)
    sound.play()

def poop():
    if not SoundSystem._poop:
        init()
    random.choice(SoundSystem._poop).play()
    
def water_start():
    if not SoundSystem._water:
        init()
    SoundSystem._current_water = random.choice(SoundSystem._water)
    SoundSystem._current_water.play(loops=-1)
    
def water_stop():
    if SoundSystem._current_water:
        SoundSystem._current_water.fadeout(100)
    
def grunt():
    if not SoundSystem._grunt:
        init()
    random.choice(SoundSystem._grunt).play()
    
