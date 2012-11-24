_MENU_NAME = 'Transforms'

import math

from koko.shapes.core import Point, Shape, Transform
from koko.shapes.points import *

import koko.lib.shapes

import koko.globals

################################################################################
class ReflectX(Transform):
    ''' Reflection across an X coordinate.'''
    _MENU_NAME = 'Reflect X'
    
    def __init__(self, name='reflect', position='', target=''):
        Transform.__init__(self, name, target)
        self.create_evaluators(position=(position,Point))
    
    @staticmethod
    def new(x, y, scale=1):
        pname = koko.globals.SHAPES.get_name('xpos')
        name  = koko.globals.SHAPES.get_name('reflect')
        
        pt = FreePoint(pname, x, y)
        
        return [pt, ReflectX(name, pname, 0)]
    
    @property
    def _height(self):
        return 250./koko.globals.CANVAS.scale
    
    @property
    def x(self): return self.position.x
    @property
    def y(self): return self.position.y + self._height/4
    
    @property
    def _math(self):
        return koko.lib.shapes.reflect_x(self.target, self.x)._math

    @property
    def _lines(self):
        return [Shape.Line(self.position.x, self.position.y - self._height/2,
                           self.position.x, self.position.y + self._height/2)]
        
################################################################################
class ReflectY(Transform):
    ''' Reflection across an Y coordinate.'''
    _MENU_NAME = 'Reflect Y'
    
    def __init__(self, name='reflect', position='', target=''):
        Transform.__init__(self, name, target)
        self.create_evaluators(position=(position,Point))
    
    @staticmethod
    def new(x, y, scale=1):
        pname = koko.globals.SHAPES.get_name('ypos')
        name  = koko.globals.SHAPES.get_name('reflect')
        
        pt = FreePoint(pname, x, y)
        
        return [pt, ReflectY(name, pname, 0)]
    
    @property
    def _length(self):
        return 250./koko.globals.CANVAS.scale
    
    @property
    def _lines(self):
        return [Shape.Line(self.position.x - self._length/2, self.position.y,
                           self.position.x + self._length/2, self.position.y)]
        
    @property
    def x(self): return self.position.x + self._length/4
    @property
    def y(self): return self.position.y
    
    @property
    def _math(self):
        return koko.lib.shapes.reflect_y(self.target, self.y)._math