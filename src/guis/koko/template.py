TEMPLATE = '''from koko.lib.shapes import *

# Render boundaries
cad.xmin = -1
cad.xmax = 1
cad.ymin = -1
cad.ymax = 1
cad.mm_per_unit = 25.4 # inch units

cad.function = circle(0, 0, 0.5)'''