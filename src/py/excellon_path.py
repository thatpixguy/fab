import fab
import re
import fractions
import math

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

def approximate_dyadic_fraction(r,max_denominator=128):
    return min([fractions.Fraction(n,2**d) for d in range(int(math.log(max_denominator,2))) for n in range(1,2**d,2)],key=lambda x:abs(x-r))

def pretty_print_tools(tools):
    for number, data in tools.items():
        print "tool T{}:".format(number)
        print "  diameter: {} mm, (approx. {} inch)".format(data["dia"],approximate_dyadic_fraction(data["dia"]/25.4)) 

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

    parser.set_defaults(resolution=1000,zdepth=0)

    (options, args) = parser.parse_args()

    units = "mm"
    header = False
    move_mode = "absolute"

    x,y = 0,0

    tools = {}

    for m in excellon_re.finditer(file("/home/pix/Projects/fab/tests/interface.drd").read()):
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
        elif m.group("tool"):
            # TODO: compensation index?
            tool = int(m.group("targ"))
        elif m.group("c"):
            print approximate_dyadic_fraction(float(m.group("dia")))
            dia = to_mm(m.group("dia"),units)
            tools.setdefault(tool,{})
            tools[tool]["dia"] = dia
        elif m.group("pair") or m.group("axis"):
            if m.group("pair"):
                x = to_mm(m.group("xarg"),units)
                y = to_mm(m.group("yarg"),units)
            elif m.group("axis"):
                arg = to_mm(m.group("xyarg"),units)
                if m.group("axis")=="X":
                    x = arg
                elif m.group("axis")=="Y":
                    y = arg
            #path.new_segment()
            #path.add_point(x,y,0)

    pretty_print_tools(tools)
                

if __name__ == "__main__":
    main()

