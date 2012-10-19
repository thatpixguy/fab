from math import *
import inspect

import wx

from koko.evaluator import *
from koko.lib.math_string import MathString

class Point(object):
    def __init__(self, name=str, **kwargs):
        
        self.parameters = {'name': NameEvaluator(self, name, str)}
               
        self.hover      = False
        self.selected   = False
        self.dragging   = False
        self.deleted    = False
        self.drawn      = False

        self.dark_color  = wx.Colour(150, 150, 150)
        self.light_color = wx.Colour(230, 230, 230)

        # THIS IS AWESOME.
        # I'm checking the constructor's default arguments, which
        # need to be set to the appropriate types.
        #
        # These types are saved in that argument's evaluator,
        # so it can check to make sure that it is spitting out
        # something reasonable.
        argspec = inspect.getargspec(self.__class__.__init__)

        args = argspec.args[1:]
        defaults = argspec.defaults

        if len(args) != len(defaults):
            raise SyntaxError('Subclass of point must have argument defaults.')
        
        # Black magic.
        for arg, default in zip(args, defaults):
            if arg in kwargs.keys():
                if type(default) is not type:
                    SyntaxError('Subclass of point argument defaults must be types.')
                self.parameters[arg] = Evaluator(self, kwargs[arg], default)

        self.parents = {}
        self.children = {}
        
    def reconstructor(self):
        return (self.__class__, {k: self.parameters[k].expr
                                 for k in self.parameters})

    @classmethod
    def build_properties(cls):
        '''Automatically make properties (in the form instance.prop)
           for parameters defined in the constructor.
        '''
        props = [p for p,t in inspect.getmembers(cls) if type(t) == property]
        argspec = inspect.getargspec(cls.__init__)
        args = argspec.args[1:]
        for arg in args:
            def makefun(parameter):
                return lambda i: i[parameter].eval()
            setattr(cls, arg, property(makefun(arg)))
    
    @classmethod
    def rank(cls):
        if cls is Point:
            return 0
        else:
            return cls.__base__.rank() + 1
########################################

    def __getitem__(self, i):
        '''Overload [] operator to get a parameter.'''
        return self.parameters[i]

########################################

    def clear_cache(self):
        ''' Empties out the cache, both for parent/child
            relationships and the saved values for evaluators.'''
        self.parents = {}
        self.children = {}
        for p in self.parameters.itervalues():
            p.cached = False

########################################

    def fill_cache(self):
        ''' Fills the evaluator caches.'''
        for p in self.parameters:
            self[p].eval()
        
########################################
    
    @property
    def modified(self):
        m = any(p.modified for p in self.parameters.itervalues())
        return m
        
    @modified.setter
    def modified(self, value):
        for p in self.parameters.itervalues():
            p.modified = value
    
    @property
    def x(self):
        return 0   
    @property
    def y(self):
        return 0
########################################

    @property
    def valid(self):
        return all(p.valid for p in self.parameters.itervalues())
    
########################################

    def __contains__(self, (mx, my, scale)):
        distance = ((mx - self.x)**2 + (my - self.y)**2)**0.5
        return distance < 5/scale

########################################

    def draw(self, canvas):
        x, y = canvas.pos_to_pixel(self.x, self.y)
        
        light_color = self.light_color        
        dark_color  = self.dark_color
        
        dark_red    = wx.Colour(255, 0, 0)
        light_red   = wx.Colour(255, 80, 60)
        
        dark_grey   = wx.Colour(60, 60, 60)
        light_grey  = wx.Colour(100, 100, 100)
        
        if self.deleted:
            canvas.dc.SetBrush(wx.Brush(dark_grey))
            canvas.dc.SetPen(wx.Pen(light_grey, 4))
            canvas.dc.DrawCircle(x, y, 8)
            
        elif self.valid:
            canvas.dc.SetBrush(wx.Brush(dark_color))
            if self.hover:
                canvas.dc.SetPen(wx.Pen(light_color, 4))
                canvas.dc.DrawCircle(x, y, 6)
            elif self.selected or self.dragging:
                canvas.dc.SetPen(wx.Pen(light_color, 2))
                canvas.dc.DrawCircle(x, y, 5)
            else:
                canvas.dc.SetPen(wx.TRANSPARENT_PEN)
                canvas.dc.DrawCircle(x, y, 4)
                
        else:
            r = 3
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
            
########################################

    def draw_links(self, canvas):
        
        x, y = canvas.pos_to_pixel(self.x, self.y)
        line_color = wx.Colour(60, 160, 255)

        def arrow(x1, y1, x2, y2, color, just_head = False):
            '''Helper function to draw an arrow.'''
            angle = -atan2(y2-y1, x2-x1)
            size = 15
            x2 -= (5+size)*cos(angle)
            y2 += (5+size)*sin(angle)
            
            if not just_head:
                canvas.dc.SetPen(wx.Pen(color, 4, wx.LONG_DASH))
                canvas.dc.DrawLine(x2, y2, x1, y1)

            x2 += size*cos(angle)
            y2 -= size*sin(angle)            
            canvas.dc.SetPen(wx.TRANSPARENT_PEN)
            canvas.dc.SetBrush(wx.Brush(color))
            shape = [wx.Point(x2, y2),
                     wx.Point(x2-size*cos(angle+pi/8),
                              y2+size*sin(angle+pi/8)),
                     wx.Point(x2-size*cos(angle-pi/8),
                              y2+size*sin(angle-pi/8))]
            canvas.dc.DrawPolygon(shape)
            
        
        # Figure out the intersection of the two nodes
        both = {}
        keys = [k for k in self.parents.keys() + self.children.keys() if
                k in self.parents and k in self.children]
        for k in keys:
            both[k] = self.children[k].union(self.parents[k])
        
        def select_color(data):
            '''Based on the data passed from one node to another,
               pick an appropriate color for the linking arrow.
               
               The arrow will be the color of the highest-rank information
               passed back and forth.'''
            bestRank = -2
            bestData = None
            for d in data:
                try: rank = d.rank()
                except AttributeError: rank = -1
                if rank > bestRank:
                    bestRank = rank
                    bestData = d
            
            try: return bestData.dark_color
            except AttributeError: return wx.Colour(150, 150, 150)
        
        # Draw arrows to parents
        for node in self.parents:
            if node.selected or node.deleted or node in self.children:
                continue
            nodeX, nodeY = canvas.pos_to_pixel(node.x, node.y)

            bestRank = -2
            bestClass = None
            
            color = select_color(self.parents[node])
            arrow(nodeX, nodeY, x, y, color)
            
            
        # Draw arrows to children
        for node in self.children:
            if node.selected or node.deleted or node in self.parents:
                continue
            nodeX, nodeY = canvas.pos_to_pixel(node.x, node.y)
            
            color = select_color(self.children[node])
            arrow(x, y, nodeX, nodeY, color)
        
        for node in both:
            if node.selected or node.deleted:
                continue
            nodeX, nodeY = canvas.pos_to_pixel(node.x, node.y)
            
            color = select_color(both[node])
            arrow(x, y, nodeX, nodeY, color)
            arrow(nodeX, nodeY, x, y, color, just_head=True)

            
########################################

    def drag(self, dx, dy):
        pass
    
    def drop(self):
        self.dragging  = False