import numpy
import re

whitespace_or_comma_re = re.compile("[\s,]")

transform_re = re.compile("(\w+)(?:\((.*?)\))?")

def split_on_whitespace_or_comma(string):
    #return [n for s in string for n in s.split(",")] 
    return whitespace_or_comma_re.split(string)

class Transform:


    def __init__(self):
        self.stack = []
        self.matrix = numpy.matrix(numpy.identity(3))
        
    def push(self):
        self.stack.append(self.matrix)

    def pop(self):
        self.matrix = self.stack.pop()

    def apply(self,matrix):
        self.matrix=self.matrix*matrix

    def translate(self,x,y):
        self.matrix*=numpy.matrix([[1,0,x],[0,1,y],[0,0,1]])
    
    def scale(self,x,y):
        self.matrix*=numpy.matrix([[x,0,0],[0,y,0],[0,0,1]])

    def rotate(self,a):
        r = math.radians(a)
        self.matrix*=numpy.matrix([[math.cos(r),-math.sin(r),0],[math.sin(r),math.cos(r),0],[0,0,1]])

    def set(self,matrix):
        #maybe take the params in svg style?
        self.matrix=matrix

    def apply(self,point):
        " return the result of applying this matrix to a point (a 3-element list) "
        return (self.matrix * numpy.matrix(point).transpose()).transpose().tolist()[0]

    def parse_transform(self,string):
        for (transform,args) in transform_re.findall(string):
            axes = [float(axis) for axis in split_on_whitespace_or_comma(args)]
            if transform == "translate":
                self.translate(*axes)
            elif transform == "rotate":
                self.rotate(args)
            elif transform == "scale":
                self.scale(*axes)
            else:
                print >> sys.stderr, "ignored unsupported transform {}({})".format(transform,args)

class Path:
    
    def __init__(self):
        self.dof = 3
        self.units = "mm"
        self.nx = self.ny = self.nz = 0
        self.dx = self.dy = self.dz = 0
        self.xmin = self.ymin = self.zmin = 0
        # list of lists(segments) of dof-tuples
        self.segments = []
       
 
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
        self.segment_start = None

    def add_point(self,*args):

        #if args[-1] is a matrix, apply it (and then pop it from the list of axes abviously)
        if isinstance(args[-1],Transform):
            transform=args[-1]
            axes=args[:-1]
        else:
            # default to the identity matrix
            transform=Transform()
            axes=args[:]

        if len(axes) != self.dof:
            raise ValueError("expected point with {} degress-of-freedom, got {}".format(self.dof,len(axes)))

        # implied new_segment if not yet called (ie. segments == [])
        if not self.segments:
            self.new_segment()

        if not self.segments[-1]:
            # store the first point, untransformed
            self.segment_start = axes

        self.segments[-1].append(transform.apply(axes))

    def close_segment(self,transform):
        self.add_point(*(self.segment_start+(transform,)))
        return self.segment_start
