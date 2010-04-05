#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''


__version__ = '$Id: main.py 413 2009-05-02 22:19:00Z dr0iddr0id $'

try:
    import psyco
    psyco.full()
except:
    pass

import data
import states
import screens

import sys

def main():
    file = open("debug.txt", 'w')
    sys.stdout = file
    first_state = screens.Splash2()
    states.GameMain(first_state).run()
