import inspect

from koko.shapes.core import Primitive
import koko.shapes.points
import koko.shapes.shapes2d
import koko.shapes.transforms
import koko.shapes.pcb

def find_constructors():
    lists = {}
    for name, obj in inspect.getmembers(koko.shapes):
        if not inspect.ismodule(obj):
            continue
        for name, obj in inspect.getmembers(obj):
            if inspect.isclass(obj) and issubclass(obj, Primitive):
            
                module = inspect.getmodule(obj)
                
                if module not in lists.keys():
                    lists[module] = set()
                lists[module].add(obj)
                
    constructors = {}
    for T in lists:
        if not hasattr(T, '_MENU_NAME'):
            continue
#        print 'Scanning',T._MENU_NAME
        constructors[T._MENU_NAME] = []
        for S in lists[T]:
#            print '\tFound',S,
            if '_MENU_NAME' in S.__dict__:
#                print 'with menu name',S._MENU_NAME
                constructors[T._MENU_NAME] += [(S._MENU_NAME, S.new)]
#            else:
#                print 'without menu name.'
    return constructors

constructors = find_constructors()