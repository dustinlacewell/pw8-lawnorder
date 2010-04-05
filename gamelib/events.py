#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO: docstring
"""

__version__ = '$Id: events.py 189 2009-04-27 18:23:55Z dr0iddr0id $'

import warnings

class Event(object):

    def __init__(self, name=None):
        if name:
            self.name = name
        else:
            self.name = self
        self._observers = []

    def add(self, obs):
        if obs not in self._observers:
            self._observers.append(obs)
        else:
            msg = u"attemp to add observer twice: %s " % str(obs)
            warnings.warn(msg)
        return self

    def remove(self, obs):
        if obs in self._observers:
            self._observers.remove(obs)
        return self

    def fire(self, *args, **kwargs):
        for obs in list(self._observers):
            obs(*args, **kwargs)

    def clear(self):
        self._observers = []

    __iadd__ = add
    __isub__ = remove
    __call__ = fire
    
if __name__ == '__main__':
    
    def f1(*args, **kwargs):
        print 'f1', args, kwargs
    
    def f2(*args, **kwargs):
        print 'f2', args, kwargs
    
    e = Event()
    e += f1
    e += f2
    
    e('first call')

    e -= f1
    e('second call')

