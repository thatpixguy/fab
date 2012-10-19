import wx

from koko.primitives.points import FreePoint
from koko.lib.math_string import MathString

class MathShape(FreePoint, MathString):
    def __init__(self, name=str, x=float, y=float, **kwargs):
        # Create the Point parent class
        FreePoint.__init__(self, name, x, y, **kwargs)
        
        self.dark_color  = wx.Colour(60, 160, 255)
        self.light_color = wx.Colour(150, 200, 232)

        
    def draw(self, canvas):
        x, y = canvas.pos_to_pixel(self.x, self.y)
        
        dark_color  = self.dark_color
        light_color = self.light_color
        
        dark_red  = wx.Colour(255, 0, 0)
        light_red = wx.Colour(255, 80, 60)
        
        dark_grey   = wx.Colour(60, 60, 60)
        light_grey  = wx.Colour(100, 100, 100)
        
        if self.valid:
            canvas.dc.SetBrush(wx.TRANSPARENT_BRUSH)
            
            # If the point is being dragged, draw small
            # arrows to show in which ways it is free
            if self.dragging or self.hover:
                if self._x_free:
                    canvas.dc.SetPen(wx.Pen(light_color, 8))
                else:
                    canvas.dc.SetPen(wx.Pen(light_grey, 8))
                canvas.dc.DrawLine(x-14, y, x+14, y)
                
                if self._y_free:
                    canvas.dc.SetPen(wx.Pen(light_color, 8))
                else:
                    canvas.dc.SetPen(wx.Pen(light_grey, 8))
                canvas.dc.DrawLine(x, y-14, x, y+14)
                    
                if self._x_free:
                    canvas.dc.SetPen(wx.Pen(dark_color, 4))
                else:
                    canvas.dc.SetPen(wx.Pen(dark_grey, 4))
                canvas.dc.DrawLine(x-14, y, x+14, y)
                
                if self._y_free:
                    canvas.dc.SetPen(wx.Pen(dark_color, 4))
                else:
                    canvas.dc.SetPen(wx.Pen(dark_grey, 4))
                canvas.dc.DrawLine(x, y-14, x, y+14)
            
            
            if self.hover:
                canvas.dc.SetPen(wx.Pen(light_color, 10))
                canvas.dc.DrawCircle(x, y, 6)
            elif self.selected or self.dragging:
                canvas.dc.SetPen(wx.Pen(light_color, 8))
                canvas.dc.DrawCircle(x, y, 6)
                
            canvas.dc.SetPen(wx.Pen(dark_color, 4))
            canvas.dc.DrawCircle(x, y, 6)
                
        else:
            r = 5
            if self.hover:
                canvas.dc.SetPen(wx.Pen(light_red, 10))
                canvas.dc.DrawLine(x-r, y-r, x+r, y+r)
                canvas.dc.DrawLine(x-r, y+r, x+r, y-r)
            elif self.selected or self.dragging:
                canvas.dc.SetPen(wx.Pen(light_red, 8))
                canvas.dc.DrawLine(x-r, y-r, x+r, y+r)
                canvas.dc.DrawLine(x-r, y+r, x+r, y-r)
            canvas.dc.SetPen(wx.Pen(dark_red, 4))
            canvas.dc.DrawLine(x-r, y-r, x+r, y+r)
            canvas.dc.DrawLine(x-r, y+r, x+r, y-r)
    
    @property
    def _math(self):
        return '0'

################################################################################

class Transform(MathShape):
    def __init__(self, name=str, x=float, y=float, target=MathString, **kwargs):
        MathShape.__init__(self, name=name, x=x, y=y, target=target, **kwargs)
        self.dark_color  = wx.Colour(190, 190, 0)
        self.light_color = wx.Colour(255, 255, 0)