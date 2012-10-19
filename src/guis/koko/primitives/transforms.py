_MENU_NAME = 'Transforms'

from koko.math_shape import Transform
from koko.lib.math_string import MathString
from koko.point import Point
from koko.primitives.points import *

import koko.lib.shapes
import koko.singletons as singletons

import wx
import math

class ReflectX(Transform):
    _MENU_NAME = 'Reflect X'
    
    def __init__(self, name=str, x=float, y=float, target=MathString):
        Transform.__init__(self, name=name, x=x, y=y, target=target)
        
    @staticmethod
    def new(x, y, scale=1):
        name = singletons.shape_set.get_name('reflect')
        reflect = ReflectX(name, x, y, '')
        return [reflect]

    @property
    def _math(self):
        return koko.lib.shapes.reflect_x(self.target, self.x)._math
    
    def draw(self, canvas):
        x, y = canvas.pos_to_pixel(self.x, self.y)
        
        if self.valid:
            canvas.dc.SetPen(wx.Pen(self.dark_color, 2,
                                    wx.DOT))
        else:
            canvas.dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2,
                                    wx.DOT))
        
        canvas.dc.DrawLine(x, y-200, x, y+200)
        Transform.draw(self, canvas)
        
################################################################
        
class ReflectY(Transform):
    _MENU_NAME = 'Reflect Y'
    
    def __init__(self, name=str, x=float, y=float, target=MathString):
        Transform.__init__(self, name=name, x=x, y=y, target=target)
        self.dark_color  = wx.Colour(190, 190, 0)
        self.light_color = wx.Colour(255, 255, 0)
        
    @staticmethod
    def new(x, y, scale=1):
        name = singletons.shape_set.get_name('reflect')
        reflect = ReflectY(name, x, y, '')
        return [reflect]

    @property
    def _math(self):
        return koko.lib.shapes.reflect_y(self.target, self.y)._math
    
    def draw(self, canvas):
        x, y = canvas.pos_to_pixel(self.x, self.y)
        
        if self.valid:
            canvas.dc.SetPen(wx.Pen(self.dark_color, 2,
                                    wx.DOT))
        else:
            canvas.dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2,
                                    wx.DOT))
        
        canvas.dc.DrawLine(x-200, y, x+200, y)
        Transform.draw(self, canvas)
        
################################################################
        
class ShearXY(Transform):
    _MENU_NAME = 'Shear XY'
    
    def __init__(self, name=str, x=float, y=float, target=MathString,
                 amount=Point):
        Transform.__init__(self, name=name, x=x, y=y, target=target,
                           amount=amount)
        self.dark_color  = wx.Colour(190, 190, 0)
        self.light_color = wx.Colour(255, 255, 0)
        
    @staticmethod
    def new(x, y, scale=1):
        name = singletons.shape_set.get_name('shear')
        ptname  = singletons.shape_set.get_name('pt')
        shear = ShearXY(name, x, y, '', ptname)
        pt0   = LinkedPoint(ptname, name, 0, scale)
        return [shear, pt0]

    @property
    def _math(self):
        moved = koko.lib.shapes.move(self.target, 0, -self.y)
        sheared = koko.lib.shapes.shear_x_y(
            moved, -self.amount.dy, self.amount.dy,
            -self.amount.dx,self.amount.dx)._math
        return koko.lib.shapes.move(sheared, 0, self.y)._math
    
        
    def draw(self, canvas):
        dy = self.amount.y - self.y
        dx = self.amount.x - self.x

        if self.valid:
            canvas.dc.SetPen(wx.Pen(self.dark_color, 2,
                                    wx.DOT))
        else:
            canvas.dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2,
                                    wx.DOT))
        
        x0, y0 = canvas.pos_to_pixel(self.x, self.y - dy)
        x1, y1 = canvas.pos_to_pixel(self.x, self.y + dy)
        offset = canvas.pos_to_pixel(dx)
        
        canvas.dc.DrawLine(x0, y0, x1, y1)
        canvas.dc.DrawLine(x0, y0, x0-offset, y0)
        canvas.dc.DrawLine(x1, y1, x1+offset, y1)
        canvas.dc.DrawLine(x0-offset, y0, x1+offset, y1)
        Transform.draw(self, canvas)
        
        
    