import koko.singletons as singletons
import threading

class Evaluator(object):
    '''Class to do lazy evaluation of expressions.'''
    
    def __init__(self, parent, expr, out):
        self.parent = parent
        self.expr = expr
        self.type = out

        self.result = self.type()

        self.valid = False
        self.modified = True
        self.cached = False
        
    def eval(self):
        '''Evaluate the given expression.
        
           Sets self.valid to True or False depending on whether the
           evaluation succeeded.'''
        if self.cached:
            return self.result
        
        
        # Prevent recursive loops (e.g. defining pt0.x = pt0.x)
        try:
            if self.recursing:
                self.valid = False
                raise RuntimeError('Bad recursion')
        except AttributeError:
            self.recursing = True

        # Set a few variables
        self.valid = True
        
        # Tell the geometry dictionary who is looking things up
        singletons.shape_set.push_child(self.parent)
        
        try:
            #Evaluate the magical expression
            c = eval(self._expr, {}, singletons.shape_set)
        except:
            self.valid = False
        else:
            # Coerce into the desired type
            if not issubclass(type(c), self.type):
                try:    c = self.type(c)
                except: self.valid = False
                    
            # Make sure that we haven't ended up invalid
            # due to bad recursion somewhere down the line
            if self.valid:
                self.result = c

        # Restore the geometry dictionary's previous child.
        del self.recursing


        # Inform the monitor of what result was obtained
        singletons.shape_set.set_value(self.result)
        singletons.shape_set.pop_child()

        self.cached = True
        return self.result
            
    
    @property
    def expr(self):
        try:
            return self._expr
        except AttributeError:
            self._expr = ''
            return self._expr
    @expr.setter
    def expr(self, value):
        value = str(value)
        if self.expr != value:
            self.modified = True
        self._expr = value
        

################################################################################
import re

class NameEvaluator(Evaluator):
    '''Class to store valid variable names.'''
    def __init__(self, parent, expr, out=str):
        if out is not str:
            raise TypeError('NameEvaluator must output string.')
        Evaluator.__init__(self, parent, expr, out)
    
    def eval(self):        
        if re.match('[a-zA-Z_][0-9a-zA-Z_]*$', self.expr):
            self.valid = True
            self.result = self.expr
        else:
            self.valid = False
        return self.result