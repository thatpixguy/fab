_MENU_NAME = '2D shapes'
import math

import wx

from koko.math_shape import MathShape
from koko.point import Point
from koko.primitives.points import *

import koko.singletons as singletons
import koko.lib.shapes

class CornerRectangle(MathShape):
    _MENU_NAME = 'Rectangle (from corner)'
    
    def __init__(self, name=str, x=float, y=float, corner=Point):
        MathShape.__init__(self, name=name, x=x, y=y, corner=corner)
        
    @staticmethod
    def new(x, y, scale=1):
        rectName = singletons.shape_set.get_name('rect')
        corner = LinkedPoint(singletons.shape_set.get_name('pt'),
                             rectName, scale, scale)
        rect = CornerRectangle(rectName, x, y, corner=corner.name)
        return [rect, corner]

    @property
    def xmin(self):
        return min(self.x, self.corner.x)
    @property
    def xmax(self):
        return max(self.x, self.corner.x)
    @property
    def ymin(self):
        return min(self.y, self.corner.y)
    @property
    def ymax(self):
        return max(self.y, self.corner.y)
    @property
    def _math(self):
        return koko.lib.shapes.rectangle(self.xmin, self.xmax,
                                         self.ymin, self.ymax)._math
                          
    def draw(self, canvas):
        xmin, ymin = canvas.pos_to_pixel(self.xmin, self.ymin)
        xmax, ymax = canvas.pos_to_pixel(self.xmax, self.ymax)

        if self.valid:
            canvas.dc.SetPen(wx.Pen(self.dark_color, 2,
                                    wx.SHORT_DASH))
        else:
            canvas.dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2,
                                    wx.SHORT_DASH))

        canvas.dc.DrawLine(xmin+1, ymax-1, xmin+1, ymin-1)
        canvas.dc.DrawLine(xmax+1, ymax-1, xmax+1, ymin-1)
        canvas.dc.DrawLine(xmin+1, ymin-1, xmax+1, ymin-1)
        canvas.dc.DrawLine(xmin+1, ymax-1, xmax+1, ymax-1)

        MathShape.draw(self, canvas)

################################################################################
        
class CenterCircle(MathShape):
    _MENU_NAME = 'Circle (from center)'
    
    def __init__(self, name=str, x=float, y=float, edge=Point):
        MathShape.__init__(self, name=name, x=x, y=y, edge=edge)
        
    @staticmethod
    def new(x, y, scale=1):
        cname  = singletons.shape_set.get_name('circle')
        ptname = singletons.shape_set.get_name('pt')
        
        edge   = LinkedPoint(ptname, cname, scale, 0)
        circ   = CenterCircle(cname, x, y, ptname)
        return [circ, edge]
        
    @property
    def r(self):
        return ((self.edge.x-self.x)**2 + (self.edge.y-self.y)**2)**0.5
        
    @property
    def _math(self):
        return koko.lib.shapes.circle(self.x, self.y, self.r)._math
                          
    def draw(self, canvas):
        x, y = canvas.pos_to_pixel(self.x, self.y)
        r    = canvas.pos_to_pixel(self.r)

        if self.valid:
            canvas.dc.SetPen(wx.Pen(self.dark_color, 2,
                                    wx.SHORT_DASH))
        else:
            canvas.dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2,
                                    wx.SHORT_DASH))
        canvas.dc.SetBrush(wx.TRANSPARENT_BRUSH)
        canvas.dc.DrawCircle(x, y, r)
        MathShape.draw(self, canvas)
        
################################################################################
        
class EdgeCircle(MathShape):
    _MENU_NAME = 'Circle (from edge)'
    
    def __init__(self, name=str, x=float, y=float, center=Point):
        MathShape.__init__(self, name=name, x=x, y=y, center=center)
        
    @staticmethod
    def new(x, y, scale=1):
        cname  = singletons.shape_set.get_name('circle')
        ptname = singletons.shape_set.get_name('pt')
        
        center  = LinkedPoint(ptname, cname, scale, 0)
        circ    = EdgeCircle(cname, x, y, ptname)
        return [circ, center]
        
    @property
    def r(self):
        return ((self.center.x-self.x)**2 + (self.center.y-self.y)**2)**0.5
        
    @property
    def _math(self):
        return koko.lib.shapes.circle(self.center.x,
                                      self.center.y,
                                      self.r)._math
                          
    def draw(self, canvas):
        x, y = canvas.pos_to_pixel(self.center.x, self.center.y)
        r    = canvas.pos_to_pixel(self.r)

        if self.valid:
            canvas.dc.SetPen(wx.Pen(self.dark_color, 2,
                                    wx.SHORT_DASH))
        else:
            canvas.dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2,
                                    wx.SHORT_DASH))
        canvas.dc.SetBrush(wx.TRANSPARENT_BRUSH)
        canvas.dc.DrawCircle(x, y, r)
        MathShape.draw(self, canvas)

################################################################################

class Triangle(MathShape):
    _MENU_NAME = 'Triangle'
    
    def __init__(self, name=str, x=float, y=float, cornerA=Point, cornerB=Point):
        MathShape.__init__(self, name=name, x=x, y=y,
                           cornerA=cornerA, cornerB=cornerB)

    @staticmethod
    def new(x, y, scale=1):
        tname  = singletons.shape_set.get_name('tri')
        ptnames = singletons.shape_set.get_name('pt', 2)
        
        tri = Triangle(tname, x, y, ptnames[0], ptnames[1])
        pt1 = LinkedPoint(ptnames[0], tname, scale, 0)
        pt2 = LinkedPoint(ptnames[1], tname, 0, scale)
        
        return [tri, pt1, pt2]
    
    @property
    def _math(self):
        angleA = math.atan2(self.y - self.cornerA.y, self.x - self.cornerA.x)
        angleB = math.atan2(self.y - self.cornerB.y, self.x - self.cornerB.x)
        
        if (angleA - angleB)%(2*math.pi)<math.pi:
            return koko.lib.shapes.triangle(self.x, self.y,
                            self.cornerA.x, self.cornerA.y,
                            self.cornerB.x, self.cornerB.y)._math
        else:
            return koko.lib.shapes.triangle(self.x, self.y,
                            self.cornerB.x, self.cornerB.y,
                            self.cornerA.x, self.cornerA.y)._math

    def draw(self, canvas):
        x0, y0 = canvas.pos_to_pixel(self.x, self.y)
        x1, y1 = canvas.pos_to_pixel(self.cornerA.x,
                                     self.cornerA.y)
        x2, y2 = canvas.pos_to_pixel(self.cornerB.x,
                                     self.cornerB.y)
        
        if self.valid:
            canvas.dc.SetPen(wx.Pen(self.dark_color, 2,
                                    wx.SHORT_DASH))
        else:
            canvas.dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2,
                                    wx.SHORT_DASH))
        canvas.dc.SetBrush(wx.TRANSPARENT_BRUSH)
        
        canvas.dc.DrawLine(x0, y0, x1, y1)
        canvas.dc.DrawLine(x1, y1, x2, y2)
        canvas.dc.DrawLine(x2, y2, x0, y0)
        MathShape.draw(self, canvas)
        
################################################################################

class Tab(MathShape):
    _MENU_NAME = 'Tab'
    
    def __init__(self, name=str, x=float, y=float,
                 top=Point, base=PerpendicularPoint,
                 chamfer=PerpendicularPoint):
        MathShape.__init__(self, name=name, x=x, y=y,
                           top=top, base=base, chamfer=chamfer)

    @staticmethod
    def new(x, y, scale=1):
        tname  = singletons.shape_set.get_name('tab')
        ptnames = singletons.shape_set.get_name('pt', 3)
        
        tab = Tab(tname, x, y, ptnames[0], ptnames[1], ptnames[2])
        top = LinkedPoint(ptnames[0], tname, 0, scale)
        base = PerpendicularPoint(ptnames[1], parent=tname, perp=ptnames[0],
                                  offset=scale*0.8)
        chamfer = PerpendicularPoint(ptnames[2], parent=ptnames[0], perp=tname,
                                  offset=-scale*0.6)
        
        return [tab, top, base, chamfer]
        
    @property
    def width(self):
        return abs(self.base.offset*2)
    @property
    def height(self):
        return math.sqrt((self.x - self.top.x)**2 + (self.y - self.top.y)**2)
    @property
    def angle(self):
        return math.atan2(self.top.y - self.y, self.top.x - self.x)
    @property
    def _math(self):
        r = koko.lib.shapes.rectangle(-self.height, 0,
                                      -self.width/2, self.width/2)
        chamfer = self.width/2 - abs(self.chamfer.offset)
        t = koko.lib.shapes.right_triangle(-self.height-0.1, -self.width/2-0.1, chamfer+0.2)
        r -= t + koko.lib.shapes.reflect_y(t)
        r = koko.lib.shapes.rotate(r, self.angle*180/math.pi+180)
        r = koko.lib.shapes.move(r, self.x, self.y)
        return r._math
        
    def draw(self, canvas):
    
        cos = math.cos(self.angle)
        sin = math.sin(self.angle)
        def rotate(x, y):
            return (x*cos-y*sin, x*sin+y*cos)
        
        
        if self.valid:
            canvas.dc.SetPen(wx.Pen(self.dark_color, 2,
                                    wx.SHORT_DASH))
        else:
            canvas.dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2,
                                    wx.SHORT_DASH))
        canvas.dc.SetBrush(wx.TRANSPARENT_BRUSH)

        chamfer = self.width/2 - abs(self.chamfer.offset)
        points = [(0, -self.width/2),
                  (0, self.width/2),
                  (self.height - chamfer, self.width/2),
                  (self.height, self.width/2 - chamfer),
                  (self.height, -self.width/2 + chamfer),
                  (self.height - chamfer, -self.width/2),
                  (0, -self.width/2)]
        for i in range(1, len(points)):
            x0, y0 = rotate(points[i-1][0], points[i-1][1])
            x1, y1 = rotate(points[i][0], points[i][1])
            x0, y0 = canvas.pos_to_pixel(x0 + self.x, y0 + self.y)
            x1, y1 = canvas.pos_to_pixel(x1 + self.x, y1 + self.y)
            canvas.dc.DrawLine(x0, y0, x1, y1)
        MathShape.draw(self, canvas)        

################################################################################

class Slot(MathShape):
    _MENU_NAME = 'Slot'
    
    def __init__(self, name=str, x=float, y=float,
                 bottom=Point, base=PerpendicularPoint,
                 chamfer=PerpendicularPoint):
        MathShape.__init__(self, name=name, x=x, y=y,
                           bottom=bottom, base=base, chamfer=chamfer)

    @staticmethod
    def new(x, y, scale=1):
        tname  = singletons.shape_set.get_name('slot')
        ptnames = singletons.shape_set.get_name('pt', 3)
        
        slot = Slot(tname, x, y, ptnames[0], ptnames[1], ptnames[2])
        bottom = LinkedPoint(ptnames[0], tname, 0, scale)
        base = PerpendicularPoint(ptnames[1], parent=ptnames[0], perp=tname,
                                  offset=-scale*0.8)
        chamfer = PerpendicularPoint(ptnames[2], parent=tname, perp=ptnames[0],
                                  offset=scale*0.9)
        
        return [slot, bottom, base, chamfer]
           
    @property
    def width(self):
        return abs(self.base.offset*2)
    @property
    def depth(self):
        return math.sqrt((self.x - self.bottom.x)**2 +
                         (self.y - self.bottom.y)**2)
    @property
    def angle(self):
        return math.atan2(self.y - self.bottom.y, self.x - self.bottom.x)
    @property
    def _math(self):
        r = koko.lib.shapes.rectangle(0, self.depth,
                                      -self.width/2, self.width/2)
        chamfer = abs(self.chamfer.offset) - self.width/2
        t = koko.lib.shapes.right_triangle(0, self.width/2, chamfer)
        r += t + koko.lib.shapes.reflect_y(t)
        r = koko.lib.shapes.rotate(r, self.angle*180/math.pi+180)
        r = koko.lib.shapes.move(r, self.x, self.y)
        return r._math
        
    def draw(self, canvas):
    
        cos = math.cos(self.angle)
        sin = math.sin(self.angle)
        def rotate(x, y):
            return (x*cos-y*sin, x*sin+y*cos)
        
        if self.valid:
            canvas.dc.SetPen(wx.Pen(self.dark_color, 2,
                                    wx.SHORT_DASH))
        else:
            canvas.dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2,
                                    wx.SHORT_DASH))
        canvas.dc.SetBrush(wx.TRANSPARENT_BRUSH)

        chamfer = abs(abs(self.chamfer.offset) - self.width/2)
        points = [(0, self.chamfer.offset),
                  (0, -self.chamfer.offset),
                  (-chamfer, -self.width/2),
                  (-self.depth, -self.width/2),
                  (-self.depth, self.width/2),
                  (-chamfer, self.width/2),
                  (0, self.chamfer.offset)]

        for i in range(1, len(points)):
            x0, y0 = rotate(points[i-1][0], points[i-1][1])
            x1, y1 = rotate(points[i][0], points[i][1])
            x0, y0 = canvas.pos_to_pixel(x0 + self.x, y0 + self.y)
            x1, y1 = canvas.pos_to_pixel(x1 + self.x, y1 + self.y)
            canvas.dc.DrawLine(x0, y0, x1, y1)
        MathShape.draw(self, canvas)        
