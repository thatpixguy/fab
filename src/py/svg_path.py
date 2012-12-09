#!/usr/bin/env python

from lxml import etree
from optparse import OptionParser
import re
import numpy
import math
import sys

def translate_matrix(x,y):
    return numpy.matrix([[1,0,x],[0,1,y],[0,0,1]])

def scale_matrix(x,y):
    return numpy.matrix([[x,0,0],[0,y,0],[0,0,1]])

def rotate_matrix(a):
    r = math.radians(a)
    return numpy.matrix([[math.cos(r),-math.sin(r),0],[math.sin(r),math.cos(r),0],[0,0,1]])

class Path:
    
    def __init__(self):
        self.dof = 3
        self.units = "mm"
        self.nx = self.ny = self.nz = 0
        self.dx = self.dy = self.dz = 0
        self.xmin = self.ymin = self.zmin = 0
        # list of lists(segments) of dof-tuples
        self.segments = []
        self.transform = numpy.matrix(numpy.identity(3))
        # it would be nice to not wedge this state machine behaviour in here
        self.transform_stack = [] 
       
    def push_transform(self):
        self.transform_stack.append(self.transform)

    def pop_transform(self):
        self.transform = self.transform_stack.pop()

    def apply_transform(self,matrix):
        self.transform=self.transform*matrix
 
    def __str__(self):
        s= "dof: {}\n".format(self.dof)
        s+="units:"
        for d in range(self.dof):
            s+=" {}".format(self.units)
        s+="\n"
        s+="nx ny nz: {} {} {}\n".format(self.nx,self.ny,self.nz)
        s+="dx dy dz: {} {} {}\n".format(self.dx,self.dy,self.dz)
        s+="xmin ymin zmin: {} {} {}\n".format(self.minx,self.miny,self.minz)
       
        s+="path start:\n" 
        for segment in self.segments:
            s+="segment start:\n"
            for point in segment:
                # each segment would be a list of dof-tuples?
                s+=" ".join(str(int(axis*self.nx/self.dx)) for axis in point)+"\n"
            s+="segment end:\n"
        s+="path end:\n" 
        
        return s
    
    def new_segment(self):
        if self.segments: 
            if self.segments[-1]:
                self.segments.append([])
        else:
            self.segments.append([])

    def add_point(self,*args):
        #thought: if args[-1] is a matrix, apply it (and then pop it from the list of axes abviously)
        def transform_point(matrix,point):
            return (matrix * numpy.matrix(point).transpose()).transpose().tolist()[0]

        if len(args) != self.dof:
            raise ValueError("expected point with {} degress-of-freedom, got {}".format(self.dof,len(args)))

        # implied new_segment if not yet called (ie. segments == [])
        if not self.segments:
            self.new_segment()

        if not self.segments[-1]:
            # store the first point, untransformed
            self.segment_start = args

        self.segments[-1].append(transform_point(self.transform,args))

    def close_segment(self):
        self.add_point(*self.segment_start)
        return self.segment_start
        

svg_ns = "{http://www.w3.org/2000/svg}"

whitespace_or_comma_re = re.compile("[\s,]")

units_re = re.compile("(.*?)([a-zA-Z]*)$")

transform_re = re.compile("(\w+)(?:\((.*?)\))?")

path_re = re.compile(r'(?P<num>[+-]?[0-9.]+)|(?P<cmd>[a-zA-Z])')

def parse_transform(string):
    m = numpy.identity(3)
    for (transform,args) in transform_re.findall(string):
        axes = [float(axis) for axis in split_on_whitespace_or_comma(args)]
        if transform == "translate":
            m = m*translate_matrix(*axes)
        elif transform == "rotate":
            m = m*rotate_matrix(args)
        elif transform == "scale":
            m = m*scale_matrix(*axes)
        else:
            print >> sys.stderr, "ignored unsupported transform {}({})".format(transform,args)
    return m
   

def parse_rect(element,path):
    x = parse_to_mm(element.attrib["x"])
    y = parse_to_mm(element.attrib["y"])
    width = parse_to_mm(element.attrib["width"])
    height = parse_to_mm(element.attrib["height"])
    path.new_segment() 
    path.add_point(x,y,0)
    path.add_point(x,y+height,0)
    path.add_point(x+width,y+height,0)
    path.add_point(x+width,y,0)
    path.add_point(x,y,0)

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def parse_path(element,path):
    def process_command(cmd,args,path,x0,y0):
        """
        process cmd and apply to path. 
        takes current point coordinates for relative commands.
        returns new current point (for future relative commands).
        """
        global options
        if cmd in ["m","l"]:
            if cmd=="m": path.new_segment()
            for (x,y) in chunks(args,2):
                x0 += x
                y0 += y
                path.add_point(x0,y0,0)
        elif cmd in ["M","L"]:
            if cmd=="M": path.new_segment()
            for (x,y) in chunks(args,2):
                x0 = x
                y0 = y
                path.add_point(x0,y0,0)
        elif cmd in ["C","c"]:
            for (x1,y1,x2,y2,x,y) in chunks(args,6):
                if cmd=="c":
                    x1+=x0
                    y1+=y0
                    x2+=x0
                    y2+=y0
                    x+=x0
                    y+=y0 
                cx = 3 * (x1 - x0)
                bx = 3 * (x2 - x1) - cx
                ax = x - x0 - cx - bx
                cy = 3 * (y1 - y0)
                by = 3 * (y2 - y1) - cy
                ay = y - y0 - cy - by
                for point in xrange(options.points):
                    t = point / (options.points - 1.0)
                    xt = ax*t*t*t + bx*t*t + cx*t + x0
                    yt = ay*t*t*t + by*t*t + cy*t + y0
                    path.add_point(xt,yt,0)
                x0 = x
                y0 = y
        elif cmd in ["A","a"]:
            for (rx,ry,rotation,large_arc,sweep,x,y) in chunks(args,7):
                if cmd=="a":
                    x+=x0
                    y+=y0
                tdiff = 1-((x-x0)*(x-x0)/(rx*rx) + (y-y0)*(y-y0)/(ry*ry))/2
                if tdiff > 1:
                    tdiff = 1
                if tdiff < -1:
                    tdiff = -1
                tdiff = acos(tdiff)
                tsum = (x-x0)/(-2*rx*sin(tdiff/2))
                if tsum > 1:
                    tsum = 1
                if tsum < -1:
                    tsum = -1
                tsum = 2*asin(tsum)
                t1 = (tsum+tdiff)/2
                t0 = tsum-t1
                cx = x0 - rx*cos(t0)
                cy = y0 - ry*sin(t0)
                for point in option.points:
                    t = t0 + (t1-t0) * point / (option.points - 1.0)
                    xt = cx + rx*cos(t)
                    yt = cy + ry*sin(t)
                    path.add_point(xt,yt,0)
                x0 = x
                y0 = y
        elif cmd in ["Z","z"]:
            (x0,y0,junk) = path.close_segment()
        else:
            print >> sys.stderr, "ignoring unknown path command {} with args {}".format(cmd,args)
        return (x0,y0) 
                 
    x0 = y0 = 0
    current_command = ""
 
    for match in path_re.finditer(element.attrib["d"]):
        cmd = match.group("cmd")
        num = match.group("num")
        if cmd:
            # at a new command, execute the last one
            if current_command:
                x0,y0 = process_command(current_command,args,path,x0,y0)            
            current_command = cmd
            args = []
        elif match.group("num"):
            args.append(to_mm(float(num))) 
    # process any remaining commands
    if current_command:
        process_command(current_command,args,path,x0,y0)

def parse_group(tree,path):
    path.push_transform()
    for element in tree.iterchildren():
        if element.attrib.has_key("transform"):
            path.apply_transform(parse_transform(element.attrib["transform"]))

        if element.tag == "{}g".format(svg_ns):
            parse_group(element,path)
        elif element.tag == "{}rect".format(svg_ns):
            parse_rect(element,path)
        elif element.tag == "{}path".format(svg_ns):
            parse_path(element,path)
        else:
            print >> sys.stderr, "ignored unsupported <{}> tag".format(element.tag)
    path.pop_transform()

def split_on_whitespace_or_comma(string):
    #return [n for s in string for n in s.split(",")] 
    return whitespace_or_comma_re.split(string)

def to_mm(base,units=""):
    if units in ["px",""]:
        return float(base)*25.4/90.0 #assumption about dpi?
    elif units == "pt":
        return float(base)*25.4/72.0
    elif units == "in":
        return float(base)*25.4
    elif units == "mm":
        return float(base)
    elif units == "cm":
        return float(base)*10.0
    else:
        raise ValueError("units {} unknown".format(units))

def parse_to_mm(string):
    (base,units) = units_re.match(string).groups()
    return to_mm(base,units)


def main():
    global options

    usage = "usage: %prog [options] in.svg out.path [points [resolution [z]]] "
    parser = OptionParser(usage)

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose")
    parser.add_option("-r", "--resolution", help="path resolution (optional, default %default)",
                      action="store", dest="resolution")
    parser.add_option("-p", "--points", help="points per curve segment (optional, default %default)",
                      action="store", dest="points")
    parser.add_option("-z", "--zdepth", help="path depth (optional, mm, default %default)",
                      action="store", dest="zdepth")
    parser.add_option("-x", "--noviewbox", help="disable interpretation of viewBox attribute",
                      action="store_false", dest="viewbox")

    parser.set_defaults(resolution=1000,points=25,zdepth=0,viewbox=True)

    (options, args) = parser.parse_args()


    if len(args) < 2:
        parser.error("incorrect number of arguments")

    svg_file = args[0]
    out_file = args[1]
    if len(args) >= 3:
        options.points = args[2]
    if len(args) >= 4:
        options.resolution = args[3]
    if len(args) >= 5:
        options.zdepth = args[4]

    root = etree.parse(svg_file).getroot()

    # perhaps more complete: if root is an svg tag, start, otherwise find the first svg tag

    if root.tag == "{}svg".format(svg_ns):
        svg = root
    else:
        svg = root.find("{}svg".format(svg_ns))
   
    path = Path()

    path.minz = options.zdepth
    path.minx = path.miny = 0
    path.dx  = parse_to_mm(svg.attrib["width"]) 
    path.dy = parse_to_mm(svg.attrib["height"])

    if options.viewbox and svg.attrib.has_key("viewBox"):
        # according to svg_path.c this is the openoffice default of 100units/mm
        x,y,w,h = [to_mm(float(s)) for s in split_on_whitespace_or_comma(svg.attrib["viewBox"])]
        path.apply_transform(translate_matrix(-x,-y))
        path.apply_transform(scale_matrix(path.dx/w,path.dy/h))


    path.nx = options.resolution
    path.ny = int(options.resolution*path.dy/path.dx)

    parse_group(svg,path)


    print >> file(out_file,"w"), path

if __name__ == "__main__":
    main()


#etree.parse()
