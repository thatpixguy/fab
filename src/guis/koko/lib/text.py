#   koko.lib.text.py
#   Simple math-string based font.

#   Matt Keeter
#   matt.keeter@cba.mit.edu

#   kokompe.cba.mit.edu

################################################################################

from shapes import *

def text(text, x, y, height = 1, align = 'CC'):

    dx, dy = 0, 0
    text_shape = '0'
    
    for line in text.split('\n'):
        line_shape = '0'
        
        for chr in line:
            if not chr in _glyphs.keys():
                print 'Warning:  Unknown character "%s" in koko.lib.text' % chr
            else:
                line_shape += move(_glyphs[chr], dx, dy)
                dx += _glyphs[chr].width + 0.1
        
        if align[0] == 'L':
            text_shape += line_shape
        elif align[0] == 'C':
            text_shape += move(line_shape, -dx / 2, 0)
        elif align[0] == 'R':
            text_shape += move(line_shape, -dx, 0)
        
        dy -= 1.55
        dx = 0
    
    if align[1] == 'T':
        text_shape = move(text_shape, 0, -1)
    elif align[1] == 'B':
        text_shape = move(text_shape, 0, -1.55 - dy,)
    elif align[1] == 'C':
        text_shape = move(text_shape, 0, (-2.55-dy)/2)
    
    if height != 1:
        text_shape = scale_xy(text_shape, 0, 0, height)
        dx *= height
        dy *= height
    
    return move(text_shape, x, y)


_glyphs = {}

shape = triangle(0, 0, 0.35, 1, 0.1, 0)
shape += triangle(0.1, 0, 0.35, 1, 0.45, 1)
shape += triangle(0.35, 1, 0.45, 1, 0.8, 0)
shape += triangle(0.7, 0, 0.35, 1, 0.8, 0)
shape += rectangle(0.2, 0.6, 0.3, 0.4)
shape.width = 0.8
_glyphs['A'] = shape


shape = circle(0.25, 0.275, 0.275)
shape -= circle(0.25, 0.275, 0.175)
shape = shear_x_y(shape, 0, 0.35, 0, 0.1)
shape += rectangle(0.51, 0.61, 0, 0.35)
shape = move(shape, -0.05, 0)
shape.width = 0.58
_glyphs['a'] = shape


shape = circle(0.3, 0.725, 0.275)
shape -= circle(0.3, 0.725, 0.175)
shape += circle(0.3, 0.275, 0.275)
shape -= circle(0.3, 0.275, 0.175)
shape &= rectangle(0.3, 1, 0, 1)
shape += rectangle(0, 0.1, 0, 1)
shape += rectangle(0.1, 0.3, 0, 0.1)
shape += rectangle(0.1, 0.3, 0.45, 0.55)
shape += rectangle(0.1, 0.3, 0.9, 1)
shape.width = 0.575
_glyphs['B'] = shape


shape = circle(0.25, 0.275, 0.275)
shape -= circle(0.25, 0.275, 0.175)
shape &= rectangle(0.25, 1, 0, 0.275) + rectangle(0, 1, 0.275, 1)
shape += rectangle(0, 0.1, 0, 1)
shape += rectangle(0.1, 0.25, 0, 0.1)
shape.width = 0.525
_glyphs['b'] = shape


shape = circle(0.3, 0.7, 0.3) - circle(0.3, 0.7, 0.2)
shape += circle(0.3, 0.3, 0.3) - circle(0.3, 0.3, 0.2)
shape -= rectangle(0, 0.6, 0.3, 0.7)
shape -= triangle(0.3, 0.5, 1, 1.5, 1, -0.5)
shape -= rectangle(0.3, 0.6, 0.2, 0.8)
shape += rectangle(0, 0.1, 0.3, 0.7)
shape.width = 0.57
_glyphs['C'] = shape


shape = circle(0.275, 0.275, 0.275)
shape -= circle(0.275, 0.275, 0.175)
shape -= triangle(0.275, 0.275, 0.55, 0.55, 0.55, 0)
shape.width = 0.48
_glyphs['c'] = shape


shape = circle(0.1, 0.5, 0.5) - circle(0.1, 0.5, 0.4)
shape &= rectangle(0, 1, 0, 1)
shape += rectangle(0, 0.1, 0, 1)
shape.width = 0.6
_glyphs['D'] = shape


shape = reflect_x(_glyphs['b'], _glyphs['b'].width/2)
shape.width = _glyphs['b'].width
_glyphs['d'] = shape


shape = rectangle(0, 0.1, 0, 1)
shape += rectangle(0.1, 0.6, 0.9, 1)
shape += rectangle(0.1, 0.6, 0, 0.1)
shape += rectangle(0.1, 0.5, 0.45, 0.55)
shape.width = 0.6
_glyphs['E'] = shape


shape = circle(0.275, 0.275, 0.275)
shape -= circle(0.275, 0.275, 0.175)
shape -= triangle(0.1, 0.275, 0.75, 0.275, 0.6, 0)
shape += rectangle(0.05, 0.55, 0.225, 0.315)
shape &=  circle(0.275, 0.275, 0.275)
shape.width = 0.55
_glyphs['e'] = shape


shape = rectangle(0, 0.1, 0, 1)
shape += rectangle(0.1, 0.6, 0.9, 1)
shape += rectangle(0.1, 0.5, 0.45, 0.55)
shape.width = 0.6
_glyphs['F'] = shape


shape = circle(0.4, 0.75, 0.25) - circle(0.4, 0.75, 0.15)
shape &= rectangle(0, 0.4, 0.75, 1)
shape += rectangle(0, 0.4, 0.45, 0.55)
shape += rectangle(0.15, 0.25, 0, 0.75)
shape.width = 0.4
_glyphs['f'] = shape


shape = circle(0.275, -0.1, 0.275)
shape -= circle(0.275, -0.1, 0.175)
shape &= rectangle(0, 0.55, -0.375, -0.1)
shape += circle(0.275, 0.275, 0.275) - circle(0.275, 0.275, 0.175)
shape += rectangle(0.45, 0.55, -0.1, 0.55)
shape.width = 0.55
_glyphs['g'] = shape


shape = circle(0.3, 0.7, 0.3) - circle(0.3, 0.7, 0.2)
shape += circle(0.3, 0.3, 0.3) - circle(0.3, 0.3, 0.2)
shape -= rectangle(0, 0.6, 0.3, 0.7)
shape += rectangle(0, 0.1, 0.3, 0.7)
shape += rectangle(0.5, 0.6, 0.3, 0.4)
shape += rectangle(0.3, 0.6, 0.4, 0.5)
shape.width = 0.6
_glyphs['G'] = shape


shape = rectangle(0, 0.1, 0, 1)
shape += rectangle(0.5, 0.6, 0, 1)
shape += rectangle(0.1, 0.5, 0.45, 0.55)
shape.width = 0.6
_glyphs['H'] = shape


shape = circle(0.275, 0.275, 0.275)
shape -= circle(0.275, 0.275, 0.175)
shape &= rectangle(0, 0.55, 0.275, 0.55)
shape += rectangle(0, 0.1, 0, 1)
shape += rectangle(0.45, 0.55, 0, 0.275)
shape.width = 0.55
_glyphs['h'] = shape


shape = rectangle(0, 0.5, 0, 0.1)
shape += rectangle(0, 0.5, 0.9, 1)
shape += rectangle(0.2, 0.3, 0.1, 0.9)
shape.width = 0.5
_glyphs['I'] = shape


shape = rectangle(0.025, 0.125, 0, 0.55)
shape += circle(0.075, 0.7, 0.075)
shape.width = 0.15
_glyphs['i'] = shape


shape = circle(0.275, 0.275, 0.275)
shape -= circle(0.275, 0.275, 0.175)
shape &= rectangle(0, 0.55, 0, 0.275)
shape += rectangle(0.45, 0.55, 0.275, 1)
shape.width = 0.55
_glyphs['J'] = shape


shape = circle(0.0, -0.1, 0.275)
shape -= circle(0.0, -0.1, 0.175)
shape &= rectangle(0, 0.55, -0.375, -0.1)
shape += rectangle(0.175, 0.275, -0.1, 0.55)
shape += circle(0.225, 0.7, 0.075)
shape.width = 0.3
_glyphs['j'] = shape


shape = rectangle(0, 0.6, 0, 1)
shape -= triangle(0.1, 1, 0.5, 1, 0.1, 0.6)
shape -= triangle(0.5, 0, 0.1, 0, 0.1, 0.4)
shape -= triangle(0.6, 0.95, 0.6, 0.05, 0.18, 0.5)
shape.width = 0.6
_glyphs['K'] = shape


shape = rectangle(0, 0.5, 0, 1)
shape -= triangle(0.1, 1, 0.5, 1, 0.1, 0.45)
shape -= triangle(0.36, 0, 0.1, 0, 0.1, 0.25)
shape -= triangle(0.6, 1, 0.5, 0.0, 0.18, 0.35)
shape -= triangle(0.1, 1, 0.6, 1, 0.6, 0.5)
shape.width = 0.5
_glyphs['k'] = shape


shape = rectangle(0, 0.6, 0, 0.1)
shape += rectangle(0, 0.1, 0, 1)
shape.width = 0.6
_glyphs['L'] = shape


shape = rectangle(0.025, 0.125, 0, 1)
shape.width = 0.15
_glyphs['l'] = shape


shape = rectangle(0, 0.1, 0, 1)
shape += rectangle(0.7, 0.8, 0, 1)
shape += triangle(0, 1, 0.1, 1, 0.45, 0)
shape += triangle(0.45, 0, 0.35, 0, 0, 1)
shape += triangle(0.7, 1, 0.8, 1, 0.35, 0)
shape += triangle(0.35, 0, 0.8, 1, 0.45, 0)
shape.width = 0.8
_glyphs['M'] = shape


shape = circle(0.175, 0.35, 0.175) - circle(0.175, 0.35, 0.075)
shape += circle(0.425, 0.35, 0.175) - circle(0.425, 0.35, 0.075)
shape &= rectangle(0, 0.65, 0.35, 0.65)
shape += rectangle(0, 0.1, 0, 0.525)
shape += rectangle(0.25, 0.35, 0, 0.35)
shape += rectangle(0.5, 0.6, 0, 0.35)
shape.width = 0.6
_glyphs['m'] = shape


shape = rectangle(0, 0.1, 0, 1)
shape += rectangle(0.5, 0.6, 0, 1)
shape += triangle(0, 1, 0.1, 1, 0.6, 0)
shape += triangle(0.6, 0, 0.5, 0, 0, 1)
shape.width = 0.6
_glyphs['N'] = shape


shape = circle(0.275, 0.275, 0.275)
shape -= circle(0.275, 0.275, 0.175)
shape &= rectangle(0, 0.55, 0.325, 0.55)
shape += rectangle(0, 0.1, 0, 0.55)
shape += rectangle(0.45, 0.55, 0, 0.325)
shape.width = 0.55
_glyphs['n'] = shape


shape = circle(0.3, 0.7, 0.3) - circle(0.3, 0.7, 0.2)
shape += circle(0.3, 0.3, 0.3) - circle(0.3, 0.3, 0.2)
shape -= rectangle(0, 0.6, 0.3, 0.7)
shape += rectangle(0, 0.1, 0.3, 0.7)
shape += rectangle(0.5, 0.6, 0.3, 0.7)
shape.width = 0.6
_glyphs['O'] = shape


shape = circle(0.275, 0.275, 0.275)
shape -= circle(0.275, 0.275, 0.175)
shape.width = 0.55
_glyphs['o'] = shape


shape = circle(0.3, 0.725, 0.275)
shape -= circle(0.3, 0.725, 0.175)
shape &= rectangle(0.3, 1, 0, 1)
shape += rectangle(0, 0.1, 0, 1)
shape += rectangle(0.1, 0.3, 0.45, 0.55)
shape += rectangle(0.1, 0.3, 0.9, 1)
shape.width = 0.575
_glyphs['P'] = shape


shape = circle(0.275, 0.275, 0.275)
shape -= circle(0.275, 0.275, 0.175)
shape += rectangle(0, 0.1, -0.375, 0.55)
shape.width = 0.55
_glyphs['p'] = shape


shape = circle(0.3, 0.7, 0.3) - circle(0.3, 0.7, 0.2)
shape += circle(0.3, 0.3, 0.3) - circle(0.3, 0.3, 0.2)
shape -= rectangle(0, 0.6, 0.3, 0.7)
shape += rectangle(0, 0.1, 0.3, 0.7)
shape += rectangle(0.5, 0.6, 0.3, 0.7)
shape += triangle(0.5, 0.1, 0.6, 0.1, 0.6, 0)
shape += triangle(0.5, 0.1, 0.5, 0.3, 0.6, 0.1)
shape.width = 0.6
_glyphs['Q'] = shape


shape = circle(0.275, 0.275, 0.275) - circle(0.275, 0.275, 0.175)
shape += rectangle(0.45, 0.55, -0.375, 0.55)
shape.width = 0.55
_glyphs['q'] = shape


shape = circle(0.3, 0.725, 0.275)
shape -= circle(0.3, 0.725, 0.175)
shape &= rectangle(0.3, 1, 0, 1)
shape += rectangle(0, 0.1, 0, 1)
shape += rectangle(0.1, 0.3, 0.45, 0.55)
shape += rectangle(0.1, 0.3, 0.9, 1)
shape += triangle(0.3, 0.5, 0.4, 0.5, 0.575, 0)
shape += triangle(0.475, 0.0, 0.3, 0.5, 0.575, 0)
shape.width = 0.575
_glyphs['R'] = shape


shape = circle(0.55, 0, 0.55) - scale_x(circle(0.55, 0, 0.45), 0.55, 0.8)
shape &= rectangle(0, 0.55, 0, 0.55)
shape = scale_x(shape, 0, 0.7)
shape += rectangle(0, 0.1, 0, 0.55)
shape.width = 0.385
_glyphs['r'] = shape


shape = circle(0.275, 0.725, 0.275)
shape -= circle(0.275, 0.725, 0.175)
shape -= rectangle(0.275, 0.55, 0.45, 0.725)
shape += reflect_x(reflect_y(shape, 0.5), .275)
shape.width = 0.55
_glyphs['S'] = shape


shape = circle(0.1625, 0.1625, 0.1625)
shape -= scale_x(circle(0.165, 0.165, 0.0625), 0.165, 1.5)
shape -= rectangle(0, 0.1625, 0.1625, 0.325)
shape += reflect_x(reflect_y(shape, 0.275), 0.1625)
shape = scale_x(shape, 0, 1.5)
shape.width = 0.4875
_glyphs['s'] = shape


shape = rectangle(0, 0.6, 0.9, 1) + rectangle(0.25, 0.35, 0, 0.9)
shape.width = 0.6
_glyphs['T'] = shape


shape = circle(0.4, 0.25, 0.25) - circle(0.4, 0.25, 0.15)
shape &= rectangle(0, 0.4, 0, 0.25)
shape += rectangle(0, 0.4, 0.55, 0.65)
shape += rectangle(0.15, 0.25, 0.25, 1)
shape.width = 0.4
_glyphs['t'] = shape


shape = circle(0.3, 0.3, 0.3) - circle(0.3, 0.3, 0.2)
shape &= rectangle(0, 0.6, 0, 0.3)
shape += rectangle(0, 0.1, 0.3, 1)
shape += rectangle(0.5, 0.6, 0.3, 1)
shape.width = 0.6
_glyphs['U'] = shape


shape = circle(0.275, 0.275, 0.275) - circle(0.275, 0.275, 0.175)
shape &= rectangle(0, 0.55, 0, 0.275)
shape += rectangle(0, 0.1, 0.275, 0.55)
shape += rectangle(0.45, 0.55, 0, 0.55)
shape.width = 0.55
_glyphs['u'] = shape


shape = triangle(0, 1, 0.1, 1, 0.35, 0)
shape += triangle(0.35, 0, 0.25, 0, 0, 1)
shape += reflect_x(shape, 0.3)
shape.width = 0.6
_glyphs['V'] = shape


shape = triangle(0, 0.55, 0.1, 0.55, 0.35, 0)
shape += triangle(0.35, 0, 0.25, 0, 0, 0.55)
shape += reflect_x(shape, 0.3)
shape.width = 0.6
_glyphs['v'] = shape


shape = triangle(0, 1, 0.1, 1, 0.25, 0)
shape += triangle(0.25, 0, 0.15, 0, 0, 1)
shape += triangle(0.15, 0, 0.35, 1, 0.45, 1)
shape += triangle(0.45, 1, 0.25, 0, 0.15, 0)
shape += reflect_x(shape, 0.4)
shape.width = 0.8
_glyphs['W'] = shape


shape = triangle(0, 0.55, 0.1, 0.55, 0.25, 0)
shape += triangle(0.25, 0, 0.15, 0, 0, 0.55)
shape += triangle(0.15, 0, 0.35, 0.5, 0.45, 0.5)
shape += triangle(0.45, 0.5, 0.25, 0, 0.15, 0)
shape += reflect_x(shape, 0.4)
shape.width = 0.8
_glyphs['w'] = shape


shape = triangle(0, 1, 0.125, 1, 0.8, 0)
shape += triangle(0.8, 0, 0.675, 0, 0, 1)
shape += reflect_x(shape, 0.4)
shape.width = 0.8
_glyphs['X'] = shape


shape = triangle(0, 0.55, 0.125, 0.55, 0.55, 0)
shape += triangle(0.55, 0, 0.425, 0, 0, 0.55)
shape += reflect_x(shape, 0.275)
shape.width = 0.55
_glyphs['x'] = shape


shape = triangle(0, 1, 0.1, 1, 0.45, 0.5)
shape += triangle(0.45, 0.5, 0.35, 0.5, 0, 1)
shape += reflect_x(shape, 0.4)
shape += rectangle(0.35, 0.45, 0, 0.5)
shape.width = 0.8
_glyphs['Y'] = shape


shape = triangle(0, 0.55, 0.1, 0.55, 0.325, 0)
shape += triangle(0.325, 0, 0.225, 0, 0, 0.55)
shape += reflect_x(shape, 0.275) + move(reflect_x(shape, 0.275), -0.225, -0.55)
shape &= rectangle(0, 0.55, -0.375, 0.55)
shape.width = 0.55
_glyphs['y'] = shape


shape = rectangle(0, 0.6, 0, 1)
shape -= triangle(0, 0.1, 0, 0.9, 0.45, 0.9)
shape -= triangle(0.6, 0.1, 0.15, 0.1, 0.6, 0.9)
shape.width = 0.6
_glyphs['Z'] = shape


shape = rectangle(0, 0.6, 0, 0.55)
shape -= triangle(0, 0.1, 0, 0.45, 0.45, 0.45)
shape -= triangle(0.6, 0.1, 0.15, 0.1, 0.6, 0.45)
shape.width = 0.6
_glyphs['z'] = shape


shape = MathString('0')
shape.width = 0.55
_glyphs[' '] = shape


shape = circle(0.075, 0.075, 0.075)
shape = scale_y(shape, 0.075, 3)
shape &= rectangle(0.0, 0.15, -0.15, 0.075)
shape -= triangle(0.075, 0.075, 0.0, -0.15, -0.5, 0.075)
shape += circle(0.1, 0.075, 0.075)
shape.width = 0.175
_glyphs[','] = shape


shape = circle(0.075, 0.075, 0.075)
shape.width = 0.15
_glyphs['.'] = shape


shape = rectangle(0, 0.1, 0.55, 0.8)
shape.width = 0.1
_glyphs["'"] = shape

shape = rectangle(0, 0.1, 0.55, 0.8) + rectangle(0.2, 0.3, 0.55, 0.8)
shape.width = 0.3
_glyphs['"'] = shape


shape = circle(0.075, 0.15, 0.075) + circle(0.075, 0.45, 0.075)
shape.width = 0.15
_glyphs[':'] = shape


shape = circle(0.075, 0.15, 0.075)
shape = scale_y(shape, 0.15, 3)
shape &= rectangle(0.0, 0.15, -0.075, 0.15)
shape -= triangle(0.075, 0.15, 0.0, -0.075, -0.5, 0.15)
shape += circle(0.075, 0.45, 0.075)
shape += circle(0.1, 0.15, 0.075)
shape.width = 0.15
_glyphs[';'] = shape


shape = rectangle(0.025, 0.125, 0.3, 1)
shape += circle(0.075, 0.075, 0.075)
shape.width = 0.1
_glyphs['!'] = shape


shape = rectangle(0.05, 0.4, 0.35, 0.45)
shape.width = 0.45
_glyphs['-'] = shape


shape = circle(0, 0.4, 0.6) - scale_x(circle(0, 0.4, 0.5), 0, 0.7)
shape &= rectangle(0, 0.6, -0.2, 1)
shape = scale_x(shape, 0, 1/2.)
shape.width = 0.3
_glyphs[')'] = shape


shape = circle(0.6, 0.4, 0.6) - scale_x(circle(0.6, 0.4, 0.5), 0.6, 0.7)
shape &= rectangle(0, 0.6, -0.2, 1)
shape = scale_x(shape, 0, 1/2.)
shape.width = 0.3
_glyphs['('] = shape


shape = rectangle(0, 0.3, 0, 1)
shape -= circle(0, 1, 0.2)
shape -= rectangle(0, 0.2, 0, 0.7)
shape.width = 0.3
_glyphs['1'] = shape


shape = circle(0.275, .725, .275)
shape -= circle(0.275, 0.725, 0.175)
shape -= rectangle(0, 0.55, 0, 0.725)
shape += rectangle(0, 0.55, 0, 0.1)
shape += triangle(0, 0.1, 0.45, 0.775, 0.55, 0.725)
shape += triangle(0, 0.1, 0.55, 0.725, 0.125, 0.1)
shape.width = 0.55
_glyphs['2'] = shape


shape = circle(0.3, 0.725, 0.275)
shape -= circle(0.3, 0.725, 0.175)
shape += circle(0.3, 0.275, 0.275)
shape -= circle(0.3, 0.275, 0.175)
shape -= rectangle(0, 0.275, 0.275, 0.725)
shape.width = 0.55
_glyphs['3'] = shape


shape = triangle(-0.10, 0.45, 0.4, 1, 0.4, 0.45)
shape += rectangle(0.4, 0.5, 0, 1)
shape -= triangle(0.4, 0.85, 0.4, 0.55, 0.1, 0.55)
shape &= rectangle(0, 0.5, 0, 1)
shape.width = 0.5
_glyphs['4'] = shape


shape = circle(0.325, 0.325, 0.325) - circle(0.325, 0.325, 0.225)
shape -= rectangle(0, 0.325, 0.325, 0.65)
shape += rectangle(0, 0.325, 0.55, 0.65)
shape += rectangle(0, 0.1, 0.55, 1)
shape += rectangle(0.1, 0.65, 0.9, 1)
shape.width = 0.65
_glyphs['5'] = shape


shape = circle(0.275, 0.725, 0.275) - scale_y(circle(0.275, 0.725, 0.175), .725, 1.2)
shape &= rectangle(0, 0.55, 0.725, 1)
shape -= triangle(0.275, 0.925, 0.55, 0.9, 0.55, 0.725)
shape = scale_y(shape, 1, 2)
shape = scale_x(shape, 0, 1.1)
shape -= rectangle(0.275, 0.65, 0., 0.7)
shape += rectangle(0, 0.1, 0.275, 0.45)
shape += circle(0.275, 0.275, 0.275) - circle(0.275, 0.275, 0.175)
shape.width = 0.55
_glyphs['6'] = shape


shape = rectangle(0, 0.6, 0.9, 1)
shape += triangle(0, 0, 0.475, 0.9, 0.6, 0.9)
shape += triangle(0, 0, 0.6, 0.9, 0.125, 0)
shape.width = 0.6
_glyphs['7'] = shape


shape = circle(0.3, 0.725, 0.275)
shape -= circle(0.3, 0.725, 0.175)
shape += circle(0.3, 0.275, 0.275)
shape -= circle(0.3, 0.275, 0.175)
shape.width = 0.55
_glyphs['8'] = shape


shape = reflect_x(reflect_y(_glyphs['6'], 0.5), _glyphs['6'].width/2)
shape.width = _glyphs['6'].width
_glyphs['9'] = shape


shape = circle(0.5, 0.5, 0.5) - scale_x(circle(0.5, 0.5, 0.4), 0.5, 0.7**0.5)
shape = scale_x(shape, 0, 0.7)
shape.width = 0.7
_glyphs['0'] = shape


shape = rectangle(0., 0.5, 0.45, 0.55)
shape += rectangle(0.2, 0.3, 0.25, 0.75)
shape.width = 0.55
_glyphs['+'] = shape


shape = triangle(0, 0, 0.425, 1, 0.55, 1)
shape += triangle(0, 0, 0.55, 1, 0.125, 0)
shape.width = 0.55
_glyphs['/'] = shape


shape = circle(0.275, 0.725, 0.275) - circle(0.275, 0.725, 0.175)
shape -= rectangle(0, 0.275, 0.45, 0.725)
shape += rectangle(0.225, 0.325, 0.3, 0.55)
shape += circle(0.275, 0.075, 0.075)
shape.width = 0.55
_glyphs['?'] = shape

del shape