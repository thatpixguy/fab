#!/usr/bin/env python
import fab
import re
import fractions
import math
import StringIO
import sys

from optparse import OptionParser

# a problem of doing it this way is that unimplemented syntax will be silently ignored
excellon_re = re.compile(
    r'|'.join(["({})".format(r) for r in [
        r'(?P<m>M)(?P<marg>\d+)',
        r'(?P<pair>X(?P<xarg>\d+(\.\d*)?|\.\d+)Y(?P<yarg>\d+(\.\d*)?|\.\d+))',
        r'(?P<axis>[XY])(?P<xyarg>\d+(\.\d*)?|\.\d+)',
        r'(?P<c>C)(?P<dia>\d+(\.\d*)?|\.\d+)',
        r'(?P<stop>%)',
        r'(?P<tool>T)(?P<targ>\d+)'
    ]]))

# TODO something to parse LZ/TZ modes?
def to_mm(n,units):
    if units=="inch":
        return float(n)*25.4
    elif units=="mm":
        return float(n)
    raise ValueError("unknown units {}".format(units))

def approximate_dyadic_fraction(r,max_denominator=64):
    return min([fractions.Fraction(n,max_denominator) for n in range(0,max_denominator+1)],key=lambda x:abs(x-r))

def pretty_print_tools(tools):
    s = StringIO.StringIO() 
    for number, data in tools.items():
        print >>s, "tool T{}:".format(number)
        dia = float(data["dia"])
        # code to deal with the unlikely case of diameters over 1 inch
        f,i = math.modf(dia/25.4) 
        if i: 
            istr="{}-".format(int(i))
        else:
            istr=""
        print >>s, "  diameter: {} mm, (approx. {} inch)".format(dia,istr+str(approximate_dyadic_fraction(f))) 
    return s.getvalue()
    

def parse_tool_list(tool_list):
    tools = set()
    for l in (map(int,block.split("-")) for block in tool_list.split(",")):
        if len(l)==1:
            tools.update(l)
        elif len(l)==2:
            tools.update(range(l[0],l[1]+1))
        else:
            raise ValueError("too many -'s in range")
    return tools

def parse_number(number_string,units,lz):
    #print >>sys.stderr, "parse_number({},{},{})".format(number_string,units,lz)
    if number_string.find(".")>=0:
        return float(number_string)
    elif lz:
        padded = number_string.ljust(6,"0")
    else:
        padded = number_string.rjust(6,"0")

    if units == "inch":
        decimal = padded[:2]+"."+padded[2:]
    elif units == "mm":
        # what command changes the decimal format in mm?
        decimal = padded[:3]+"."+padded[3:]
    else:
        raise ValueError("unknown units {}".format(units))

    #print >>sys.stderr, "= {}".format(decimal)

    return float(decimal)    
        

def main():

    global options

    usage = "usage: %prog [options] in.drc out.path tool[,tool[,tool]] [resolution [zdepth]]"
    parser = OptionParser(usage)

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose")
    parser.add_option("-r", "--resolution", help="path resolution (optional, default %default)",
                      action="store", dest="resolution")
    parser.add_option("-z", "--zdepth", help="path depth (optional, mm, default %default)",
                      action="store", dest="zdepth")
    parser.add_option("-d", "--dpcm", help="resolution in dots per cm (optional, overrides resolution)",
                      action="store", dest="dpcm")
    parser.add_option("-x", "--debug", help="output drill positions as an + mark for debugging output (optional, DON'T RUN THIS PATH WITH A DRILL BIT!)",
                      action="store_true", dest="debug")



    parser.set_defaults(resolution=1000,zdepth=0)

    (options, args) = parser.parse_args()

    in_file = args[0]

    out_file = args[1]

    tool_filter = parse_tool_list(args[2])
    
    
    

    path = fab.Path()

    units = "mm"
    header = False
    move_mode = "absolute"
    lz = False 

    x,y = 0,0

    maxx,maxy = 0,0

    tool_defs = {}
    current_tool = None

    for m in excellon_re.finditer(file(in_file).read()):
        if m.group("stop"):
            header = False
        elif m.group("m"):
            arg = int(m.group("marg"))
            if arg==48:
                header = True
            elif arg==71:
                units = "mm"
            elif arg==72:
                units = "inch"
            elif arg==30:
                break
            else:
                print >>sys.stderr, "ignoring unknown M{}".format(arg)
        elif m.group("tool"):
            # TODO: compensation index?
            current_tool = int(m.group("targ"))
        elif m.group("c"):
            dia = to_mm(parse_number(m.group("dia"),units,lz),units)
            tool_defs.setdefault(current_tool,{})
            tool_defs[current_tool]["dia"] = dia
        elif m.group("pair") or m.group("axis"):
            if m.group("pair"):
                x = to_mm(parse_number(m.group("xarg"),units,lz),units)
                y = to_mm(parse_number(m.group("yarg"),units,lz),units)
            elif m.group("axis"):
                arg = to_mm(parse_number(m.group("xyarg"),units,lz),units)
                if m.group("axis")=="X":
                    x = arg
                elif m.group("axis")=="Y":
                    y = arg
            maxx = max(maxx,x)
            maxy = max(maxy,y)
            if current_tool in tool_filter:
                if options.debug:
                    path.new_segment()
                    path.add_point(x-1,y,0)
                    path.add_point(x+1,y,0)
                    path.new_segment()
                    path.add_point(x,y-1,0)
                    path.add_point(x,y+1,0)
                else:
                    path.new_segment()
                    path.add_point(x,y,0)
        else:
            print >>sys.stderr, "ignoring unknown command: {}".format(m.group(0)) 

    print >>sys.stderr, pretty_print_tools(tool_defs)

    path.d = [maxx,maxy,0]
    path.n = [options.resolution,int(options.resolution*path.d[1]/path.d[0]),1]
    

    print >>file(out_file,"w"), path
                

if __name__ == "__main__":
    main()

