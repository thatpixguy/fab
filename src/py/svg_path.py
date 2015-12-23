#!/usr/bin/env python

from lxml import etree
from optparse import OptionParser
import re
import math
import sys
import fab

        

svg_ns = "{http://www.w3.org/2000/svg}"


units_re = re.compile("(.*?)([a-zA-Z]*)$")

# allow floats with exponents
path_re = re.compile(r'(?P<num>[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)|(?P<cmd>[a-zA-Z])')

def parse_rect(element,path,transform):
    x = parse_to_mm(element.attrib["x"])
    y = parse_to_mm(element.attrib["y"])
    width = parse_to_mm(element.attrib["width"])
    height = parse_to_mm(element.attrib["height"])
    path.new_segment() 
    path.add_point(x,y,0,transform)
    path.add_point(x,y+height,0,transform)
    path.add_point(x+width,y+height,0,transform)
    path.add_point(x+width,y,0,transform)
    path.add_point(x,y,0,transform)

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def parse_path(element,path,transform):
    def process_command(cmd,args,x0,y0,path,transform):
        """
        process cmd and apply to path. 
        takes current point coordinates for relative commands.
        returns new current point (for future relative commands).
        """
        global options
        if cmd in ["m","l"]:
            if cmd=="m": path.new_segment()
            #for (x,y) in chunks(args,2):
            for chunk in chunks(args,2):
                if len(chunk)<2:
                    print "Ignoring undersized parameter chunk[{}] for command '{}':{}".format(len(chunk),cmd,chunk)
                    break
                (x,y) = chunk
                x0 += x
                y0 += y
                path.add_point(x0,y0,0,transform)
        elif cmd in ["M","L"]:
            if cmd=="M": path.new_segment()
            for (x,y) in chunks(args,2):
                x0 = x
                y0 = y
                path.add_point(x0,y0,0,transform)
        elif cmd in ["C","c"]:
            #for (x1,y1,x2,y2,x,y) in chunks(args,6):
            chunklist=[]
            for chunk in chunks(args,6):
                if len(chunk)<6:
                    print "Ignoring undersized parameter chunk[{}] for command '{}':{}".format(len(chunk),cmd,chunk)
                    break
                try:
                    chunklist.append(chunk)
                    (x1,y1,x2,y2,x,y) = chunk
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
                    for point in xrange(int(options.points)):
                        t = point / (int(options.points) - 1.0)
                        xt = ax*t*t*t + bx*t*t + cx*t + x0
                        yt = ay*t*t*t + by*t*t + cy*t + y0
                        path.add_point(xt,yt,0,transform)
                    x0 = x
                    y0 = y
                except ValueError as e:
                    print "ValueError: {}, (chunklist[{}]=={})".format(e,len(chunklist),chunklist)
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
                    path.add_point(xt,yt,0,transform)
                x0 = x
                y0 = y
        elif cmd in ["Z","z"]:
            (x0,y0,junk) = path.close_segment(transform)
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
                x0,y0 = process_command(current_command,args,x0,y0,path,transform)            
            current_command = cmd
            args = []
        elif match.group("num"):
            args.append(to_mm(float(num))) 
    # process any remaining commands
    if current_command:
        process_command(current_command,args,x0,y0,path,transform)

def parse_group(tree,path,transform):
    transform.push()
    for element in tree.iterchildren():
        if element.attrib.has_key("transform"):
            transform.parse_transform(element.attrib["transform"])

        if element.tag == "{}g".format(svg_ns):
            parse_group(element,path,transform)
        elif element.tag == "{}rect".format(svg_ns):
            parse_rect(element,path,transform)
        elif element.tag == "{}path".format(svg_ns):
            parse_path(element,path,transform)
        else:
            print >> sys.stderr, "ignored unsupported <{}> tag".format(element.tag)
    transform.pop()


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
    parser.add_option("-d", "--dpcm", help="resolution in dots per cm (optional, overrides resolution)",
                      action="store", dest="dpcm")
    parser.add_option("-z", "--zdepth", help="path depth (optional, mm, default %default)",
                      action="store", dest="zdepth")
    parser.add_option("-x", "--noviewbox", help="disable interpretation of viewBox attribute",
                      action="store_false", dest="viewbox")

    parser.set_defaults(resolution=1000,points=25,zdepth=0,viewbox=True,dpcm=None)

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
   
    path = fab.Path()

    transform = fab.Transform()

    path.dof = 3
    path.min = [0,0,options.zdepth]
    d = [parse_to_mm(svg.attrib["width"]),parse_to_mm(svg.attrib["height"]),0]

    if options.viewbox and svg.attrib.has_key("viewBox"):
        x,y,w,h = [to_mm(float(s)) for s in fab.split_on_whitespace_or_comma(svg.attrib["viewBox"])]
        transform.translate(-x,-y)
        transform.scale(d[0]/w,d[1]/h)

    path.d = transform.apply(d)

    if options.dpcm:
        path.n = map(lambda a: int(max(1,a*float(options.dpcm)/10.0)),path.d)
    else:
        path.n = map(int,[options.resolution,options.resolution*path.d[1]/path.d[0],1])

    parse_group(svg,path,transform)


    print >> file(out_file,"w"), path

if __name__ == "__main__":
    main()


#etree.parse()
