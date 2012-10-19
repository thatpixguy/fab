import inspect
import re

import koko.singletons as singletons

# Define the modules from which we'll get shapes
import koko.primitives.shapes2d
import koko.primitives.points
import koko.primitives.transforms

from koko.point import Point

################################################################################
class ShapeSet(object):
    def __init__(self):
        # Store a link to this ShapeSet in the global singletons module.
        singletons.shape_set = self
        self.shapes = []
        
        # We want nodes to be able to use common math functions
        self.other = {}
        exec('from math import *', self.other)
        
        # Used to keep track of who is looking up who
        self.children = []
        self.saved_links = []
        
        # Used by the main app to check when we have
        # to rerender the whole image.
        self.reeval_required = False
        
        # Look up all of the shape constructors and store them
        # so that the canvas can easily make a right-click menu.
        self.find_constructors()

########################################

    def find_constructors(self):
        # Dynamically create a set of constructors for each object type
        # in the koko.primitives module
        lists = {}
        for name, obj in inspect.getmembers(koko.primitives):
            if not inspect.ismodule(obj):
                continue
            for name, obj in inspect.getmembers(obj):
                if inspect.isclass(obj) and issubclass(obj, Point):

                    if not 'koko.primitives' in obj.__module__:
                        continue
                    module = inspect.getmodule(obj)
                    if module not in lists.keys():
                        lists[module] = set()
                    
                    # For a new object, automatically add properties
                    # to the class.  (black magic, don't worry)
                    if obj not in lists[module]:
                        obj.build_properties()
                    
                    # And add it to the list of objects.
                    lists[module].add(obj)
                    
        self.constructors = {}
        for T in lists:
            self.constructors[T._MENU_NAME] = []
            for S in lists[T]:
                self.constructors[T._MENU_NAME] += [(S._MENU_NAME, S.new)]

########################################

    def propagate_name_change(self, old, new):
        if not new:
            return
        regex = re.compile("([^a-zA-z_0-9]|\A)(%s)([^a-zA-z0-9]+|\Z)" % old)
        for s in self.shapes:
            for p in s.parameters.itervalues():
                if re.search(regex, p.expr):
                    p.expr = re.sub(regex, '\1%s\3'%new, p.expr)[1:-1]

########################################

    def reconstructor(self):
        '''Returns a set of reconstructor objects, used to regenerate
           a set of shapes.'''
        return [s.reconstructor() for s in self.shapes]
    
########################################

    def reconstruct(self, R):
        '''Reload the set of shapes from a reconstructor object.'''
        self.clear()
        for r in R:
            self.shapes += [r[0](**r[1])]
    
########################################

    def clear(self):
        while self.shapes:
            self.delete(self.shapes[0])
    
########################################
    
    def add_shapes(self, shapes):
        self.shapes += shapes
        self.check_hover()
        
########################################
    
    def delete(self, point):
        ''' Delete a particular point.
            
            Pushes this event to the canvas's undo stack.'''

        if point in self.shapes:
            point.deleted = True
            point.hover = False
            point.selected = False
            self.shapes.remove(point)
            
            self.modified = True
            
########################################

    def get_name(self, prefix, count=1):
        '''Returns a non-colliding name with the given prefix.'''
        vals = []
        for s in self.shapes:
            try:
                vals += [int(s.name.replace(prefix,''))]
            except ValueError:
                pass
        
        results = []
        while len(results) < count:
            i = 0
            while i in vals:
                i += 1
            results += ['%s%i' % (prefix, i)]
            vals += [i]
        
        if len(results) == 1:
            return results[0]
        else:
            return results
    
########################################

    def push_child(self, name):
        self.children += [name]
        self.saved_links += [[]]

########################################

    def pop_child(self):
        self.children = self.children[:-1]
        self.saved_links = self.saved_links[:-1]

########################################

    def __getitem__(self, name):
        '''Looks up a variable.
          
           Saves the two-way link between parent and child.'''
        if name in self.other.keys():
            return self.other[name]

        # Pick the first item with a matching name.
        try:
            found = [s for s in self.shapes if s.name == name][0]
        except IndexError:
            raise KeyError(name)
        
        if self.children:
            self.saved_links[-1] += [(found, self.children[-1])]
        
        return found

########################################

    def set_value(self, result):
        '''Records the last set of parent/child links, as well as
           the type of value computed.'''

        for L in self.saved_links[-1]:
            if not L[1] in L[0].children:
                L[0].children[L[1]] = set()
            L[0].children[L[1]].add(result)

            if not L[0] in L[1].parents:
                L[1].parents[L[0]] = set()
            L[1].parents[L[0]].add(result)
        
########################################

    @property
    def dict(self):
        return {s.name: s for s in self.shapes}
            
########################################

    def check_hover(self):
        '''Based on mouse position, updates the hover status of points.
           Returns True if the hover status has changed, false otherwise.'''
        changed = False
        mx, my = singletons.canvas.pixel_to_pos(*singletons.canvas.mouse)
        for s in self.shapes:
            if (mx, my, singletons.canvas.scale) in s:
                if not s.hover:
                    s.hover = True
                    changed = True
            else:
                if s.hover:
                    s.hover = False
                    changed = True
        return changed

########################################

    def get_target(self):
        '''Returns the first shape under the mouse.'''
        mx, my = singletons.canvas.pixel_to_pos(*singletons.canvas.mouse)
        for s in self.shapes:
            if (mx, my, singletons.canvas.scale) in s:
                return s
        return None

########################################

    @property
    def modified(self):
        try:
            self._modified
        except AttributeError:
            self._modified = True
        return self._modified or any(s.modified for s in self.shapes)
    @modified.setter
    def modified(self, value):
        for s in self.shapes:
            s.modified = value
        self._modified = value
        
########################################

    def draw(self):
        '''Draws the set of shapes.'''
        if self.modified:
            self.clear_cache()
            self.fill_cache()
            
        for s in self.shapes[::-1]:
            s.draw(singletons.canvas)
            s.drawn = True

        for s in self.shapes[::-1]:
            if s.selected or s.dragging or s.hover:
                s.draw_links(singletons.canvas)
        
        if self.modified:
            self.modified = False
            self.reeval_required = True

                
########################################

    def clear_cache(self):
        for s in self.shapes:
            s.clear_cache()

########################################

    def fill_cache(self):
        for s in self.shapes:
            s.fill_cache()