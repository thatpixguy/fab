_MENU_NAME = 'Points'

import math

import wx

from koko.point import Point
import koko.singletons as singletons

################################################################################

class FreePoint(Point):
    _MENU_NAME = 'Free point'
    
    def __init__(self, name=str, x=float, y=float, **kwargs):
        Point.__init__(self, name, x=x, y=y, **kwargs)
        
########################################

    @staticmethod
    def new(x, y, scale=1):
        pt = FreePoint(singletons.shape_set.get_name('pt'), x, y)
        return [pt]
        
    @property
    def _x_free(self):
        try:
            float(self['x'].expr)
            return True
        except ValueError:
            return False

    @property
    def _y_free(self):
        try:
            float(self['y'].expr)
            return True
        except ValueError:
            return False
    
########################################

    def draw(self, canvas):
        x, y = canvas.pos_to_pixel(self.x, self.y)
        
        light_color = self.light_color        
        dark_color  = self.dark_color
        
        dark_grey   = wx.Colour(60, 60, 60)
        light_grey  = wx.Colour(100, 100, 100)

            
        if self.valid and not self.deleted:
            
            # If the point is being dragged, draw small
            # arrows to show in which ways it is free
            if self.dragging or self.hover:
                if self._x_free:
                    canvas.dc.SetPen(wx.Pen(light_color, 8))
                else:
                    canvas.dc.SetPen(wx.Pen(light_grey, 8))
                canvas.dc.DrawLine(x-10, y, x+10, y)
                
                if self._y_free:
                    canvas.dc.SetPen(wx.Pen(light_color, 8))
                else:
                    canvas.dc.SetPen(wx.Pen(light_grey, 8))
                canvas.dc.DrawLine(x, y-10, x, y+10)
                    
                if self._x_free:
                    canvas.dc.SetPen(wx.Pen(dark_color, 4))
                else:
                    canvas.dc.SetPen(wx.Pen(dark_grey, 4))
                canvas.dc.DrawLine(x-10, y, x+10, y)
                
                if self._y_free:
                    canvas.dc.SetPen(wx.Pen(dark_color, 4))
                else:
                    canvas.dc.SetPen(wx.Pen(dark_grey, 4))
                canvas.dc.DrawLine(x, y-10, x, y+10)
        
        Point.draw(self, canvas)

            
########################################

    def drag(self, dx, dy):
        '''If we can add a float to x and y values, then do so;
           otherwise leave them as they are.'''
        if self._x_free:
            self['x'].expr = str(float(self['x'].expr) + dx)
        if self._y_free:
            self['y'].expr = str(float(self['y'].expr) + dy)
            
################################################################################

class LinkedPoint(Point):
    _MENU_NAME = 'Linked point'

    def __init__(self, name=str, parent=Point,
                 dx=float, dy=float, **kwargs):
                 
        Point.__init__(self, name, parent=parent,
                       dx=dx, dy=dy, **kwargs)
        
########################################

    @staticmethod
    def new(x, y, scale=1):
        pt = LinkedPoint(singletons.shape_set.get_name('pt'),
                         '', dx=x, dy=y)
        return [pt]

    @property
    def x(self):
        return self['parent'].eval().x + self.dx
        
    @property
    def y(self):
        return self['parent'].eval().y + self.dy

    @property
    def dx(self):
        return self['dx'].eval()
        
    @property
    def dy(self):
        return self['dy'].eval()
        
    @property
    def _x_free(self):
        try:
            float(self['dx'].expr)
            return True
        except ValueError:
            return False

    @property
    def _y_free(self):
        try:
            float(self['dy'].expr)
            return True
        except ValueError:
            return False
    
########################################

    def draw(self, canvas):
        x, y = canvas.pos_to_pixel(self.x, self.y)
        
        light_color = self.light_color        
        dark_color  = self.dark_color
        
        dark_grey   = wx.Colour(60, 60, 60)
        light_grey  = wx.Colour(100, 100, 100)

            
        if self.valid and not self.deleted:
            
            # If the point is being dragged, draw small
            # arrows to show in which ways it is free
            if self.dragging or self.hover:
                if self._x_free:
                    canvas.dc.SetPen(wx.Pen(light_color, 8))
                else:
                    canvas.dc.SetPen(wx.Pen(light_grey, 8))
                canvas.dc.DrawLine(x-10, y, x+10, y)
                
                if self._y_free:
                    canvas.dc.SetPen(wx.Pen(light_color, 8))
                else:
                    canvas.dc.SetPen(wx.Pen(light_grey, 8))
                canvas.dc.DrawLine(x, y-10, x, y+10)
                    
                if self._x_free:
                    canvas.dc.SetPen(wx.Pen(dark_color, 4))
                else:
                    canvas.dc.SetPen(wx.Pen(dark_grey, 4))
                canvas.dc.DrawLine(x-10, y, x+10, y)
                
                if self._y_free:
                    canvas.dc.SetPen(wx.Pen(dark_color, 4))
                else:
                    canvas.dc.SetPen(wx.Pen(dark_grey, 4))
                canvas.dc.DrawLine(x, y-10, x, y+10)
        
        Point.draw(self, canvas)

            
########################################

    def drag(self, dx, dy):
        '''If we can add a float to x and y values, then do so;
           otherwise leave them as they are.'''
        if self._x_free:
            self['dx'].expr = str(float(self['dx'].expr) + dx)
        if self._y_free:
            self['dy'].expr = str(float(self['dy'].expr) + dy)

################################################################################

class PerpendicularPoint(Point):
    _MENU_NAME = 'Perpendicular point'

    def __init__(self, name=str, parent=Point, perp=Point,
                 offset=float, **kwargs):
                 
        Point.__init__(self, name, parent=parent, perp=perp,
                       offset=offset, **kwargs)
                       
    @staticmethod
    def new(x, y, scale=1):
        pt = PerpendicularPoint(singletons.shape_set.get_name('pt'),
                         '', '', 0)
        return [pt]
      
    @property
    def offset(self):
        return self['offset'].eval()
                         
    @property
    def angle(self):
        dy = self['parent'].eval().y - self['perp'].eval().y
        dx = self['parent'].eval().x - self['perp'].eval().x
        return math.atan2(dy, dx) + math.pi/2
        
    @property
    def x(self):
        return self['parent'].eval().x + self.offset*math.cos(self.angle)
        
    @property
    def y(self):
        return self['parent'].eval().y + self.offset*math.sin(self.angle)
    
    @property
    def _offset_free(self):
        try:    float(self['offset'].expr)
        except: return False
        else:   return True
        
    def drag(self, dx, dy):
        if not self._offset_free:
            return
            
        mag = (dx**2 + dy**2)**0.5
        angle = atan2(dy, dx)
        delta = mag*math.cos(angle - self.angle)
        self['offset'].expr = str(float(self['offset'].expr) + delta)
    
    def draw(self, canvas):
    
        x, y = canvas.pos_to_pixel(self.x, self.y)

        light_color = self.light_color        
        dark_color  = self.dark_color

        dark_grey   = wx.Colour(60, 60, 60)
        light_grey  = wx.Colour(100, 100, 100)
    
        if self.valid and not self.deleted:
            canvas.dc.SetBrush(wx.Brush(dark_color))
            if self.dragging or self.hover:
                x0 = x - math.cos(self.angle)*10
                x1 = x + math.cos(self.angle)*10
                y0 = y + math.sin(self.angle)*10
                y1 = y - math.sin(self.angle)*10
                if self._offset_free:
                    canvas.dc.SetPen(wx.Pen(light_color, 8))
                    canvas.dc.DrawLine(x0, y0, x1, y1)
                    canvas.dc.SetPen(wx.Pen(dark_color, 4))
                    canvas.dc.DrawLine(x0, y0, x1, y1)
                else:
                    canvas.dc.SetPen(wx.Pen(light_grey,8 ))
                    canvas.dc.DrawLine(x0, y0, x1, y1)
                    canvas.dc.SetPen(wx.Pen(dark_grey, 4))
                    canvas.dc.DrawLine(x0, y0, x1, y1)                
        
        Point.draw(self, canvas)