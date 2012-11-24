import inspect
import re
import weakref

import koko.globals

from koko.shapes.core import Primitive

################################################################################
class ShapeSet(object):
    def __init__(self):
        # Store a link to this ShapeSet in the global singletons module.
        self.shapes = []
        self.map = ShapeMap(self.shapes)
        
        # Used by the main app to check when we have
        # to rerender the whole image.
        self.reeval_required = False

########################################

    def __getitem__(self, name):
        return self.map[name]

    def propagate_name_change(self, old, new):
        if not new:
            return
        regex = re.compile("([^a-zA-z_0-9]|\A)(%s)([^a-zA-z0-9]+|\Z)" % old)
        for s in self.shapes:
            for k in s.parameters:
                if k == 'name':
                    continue
                p = s.parameters[k]
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
        '''Adds a new shape to the shape set.'''
        self.shapes += shapes
        
########################################
    
    def delete(self, point):
        ''' Delete a particular point.'''

        if point in self.shapes:
            point.deleted = True
            point.hover = False
            point.selected = False
            self.shapes.remove(point)
            
            self.modified = True
            
########################################

    def get_name(self, prefix, count=1, minimum=0):
        '''Returns a non-colliding name with the given prefix.'''
        vals = []
        for s in self.shapes:
            try:
                vals += [int(s.name.replace(prefix,''))]
            except ValueError:
                pass
        
        results = []
        while len(results) < count:
            i = minimum
            while i in vals:
                i += 1
            results += ['%s%i' % (prefix, i)]
            vals += [i]
        
        if len(results) == 1:
            return results[0]
        else:
            return results
        
########################################

    @property
    def dict(self):
        return dict((s.name, s) for s in self.shapes)
            
########################################

    def check_hover(self, x, y, r):
        '''Based on mouse position, updates the hover status of points.
           Returns True if the hover status has changed, false otherwise.'''
        
        t = self.get_target(x, y, r)

        changed = []
        for s in self.shapes:
            if s.hover:
                changed += [s]
            s.hover = False
        
        if t:
            if t in changed:
                changed.remove(t)
            else:
                changed += [t]
            t.hover = True
            
        return changed != []

########################################

    def get_target(self, x, y, r):
        '''Returns the shape under the mouse with the lowest rank.'''
        found = []
        for s in self.shapes:
            if s.intersects(x, y, r):
                found += [s]
        if not found:
            return None
        ranks = [f.priority for f in found]
        return found[ranks.index(min(ranks))]

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
            self.update_cache()
            
#        for s in self.shapes:
#            if s.selected or s.dragging or s.hover:
#                s.draw_links(koko.globals.CANVAS)
        
        ranked = {}
        for s in self.shapes:
            ranked[s.priority] = ranked.get(s.priority, []) + [s]
        for k in sorted(ranked.keys())[::-1]:
            for s in ranked[k]:
                s.draw(koko.globals.CANVAS)
        
        for s in self.shapes:
            if s.hover and not s.selected:
                s.draw_label(koko.globals.CANVAS)
                
        if self.modified:
            self.modified = False
            self.reeval_required = True

                
########################################

    def update_cache(self):
        self.clear_cache()
        self.fill_cache()

    def clear_cache(self):
        for s in self.shapes:
            s.clear_cache()

    def fill_cache(self):
        for s in self.shapes:
            s.fill_cache()
            

################################################################################

class ShapeMap(object):
    def __init__(self, shapes):
        self.shapes = shapes
        self.children = []
        self.saved_links = []
        
        # We want nodes to be able to use common math functions
        self.other = {}
        exec('from math import *', self.other)
    
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
                L[0].children[L[1]] = []
            L[0].children[L[1]].append(result)

            if not L[0] in L[1].parents:
                L[1].parents[L[0]] = []
            L[1].parents[L[0]].append(result)
    