# Functions to run various command-line executables
# These should be called in a separate thread.
from datetime import datetime
import subprocess
import Queue

import os
import re
import StringIO
import sys
import threading
import traceback

import wx

BUNDLED = False

import koko.globals

def export_math(filename, event=threading.Event()):
    '''Exports a .math file.
    
       Updates the UI in case of success.
    '''
    export_xyz('math_math', filename, event=event)

################################################################################

def export_stl(filename, resolution=1, event=threading.Event()):
    '''Exports a .stl file.
    
       Updates the UI in case of success.
    '''
    export_xyz('math_stl', filename, resolution=resolution, event=event)

################################################################################

def export_png(filename, resolution=10, event=threading.Event()):
    '''Exports a .png file.
    
       Updates the UI in case of success.
    '''
    export_xyz('math_png', filename, resolution=resolution, event=event)

################################################################################

def export_svg(filename, resolution=10, event=threading.Event()):
    '''Exports a .svg file.
    
       Updates the UI in case of success.
    '''
    export_xyz('math_svg', filename, resolution=resolution, event=event)
 
################################################################################
       
def export_dot(filename, event=threading.Event()):
    '''Exports a .dot file.
    
       Updates the UI in case of success.
    '''
    export_xyz('math_dot', filename, event=event)

################################################################################

def export_xyz(program, filename, resolution=None, event=threading.Event):
    '''Exports a generic file produced by math_xyz, where xyz is
       stl, png, svg, or dot.'''
    
    extension = program.replace('math_','.')
    output = "####    Exporting %s file     ####\n"  % extension
    
    koko.globals.CANVAS.border = None
    del koko.globals.EDITOR.error_marker
    
    koko.globals.FRAME.status = "Converting to math string (%s export)" % extension
    
    # Save math file with custom filename for .math export
    if extension == '.math':
        success, output, math = cad_math(filename=filename,
                                         output=output, event=event)
    else: # otherwise use default filename
        success, output, math = cad_math(output=output, event=event)
    
    # Check return code from cad_math
    if success is None:
        return
    elif success is False:
        frame.output = output
        return

    # Run math_xyz
    if extension != '.math':
        success, output = math_xyz(program, filename, resolution=resolution,
                                   event=event, output=output)
                  
    if success is True:
        koko.globals.CANVAS.border = None
        koko.globals.FRAME.status = "%s export complete" % extension
    
    if success is not None:
        koko.globals.OUTPUT = output

################################################################################

def render(queue=None, math=None, event=threading.Event()):
    ''' Renders an image and loads it in the display panel.
    
        This function should be called in an independent thread.
        
        If called with a queue, it will calculate the math file and store it
        in the queue.  If called with a math file, it will evaluate the
        provided math file.
    '''
    start_time = datetime.now()
    del koko.globals.EDITOR.error_marker
    
    output = "####       Rendering image      ####\n"
    koko.globals.CANVAS.border = None
    
    # If we were not provided with a math file, then recalculate it.
    if math is None:
        koko.globals.FRAME.status = "Converting to math string"
    
        # Create math file with default filename
        now = datetime.now()
        success, output, math = cad_math(output=output, event=event)
        dT = datetime.now() - now
        output += "#   cad_math time: %f s\n\n" % (dT.seconds +
                                                   dT.microseconds / 1.0e6)
                                                   
        # Return the math dictionary
        queue.put(math)
        
        if success is False:
            koko.globals.FRAME.output = output
        if not success:
            return


    else:
        output += """Modifying saved .math file
   type: %s
   units: %f
   dx: 0, dy: 0, dz: 0
   xmin: 0, ymin: 0, zmin: 0

""" % (math['format'], math['mm/unit'])

    if event.is_set(): return

    # Figure out the current view
    view = koko.globals.CANVAS.view.copy()
    output = rewrite_math(math, view, output)

    if event.is_set(): return
    
    # Calculate arguments to math_png
    resolution  = view['pixels/unit'] / math['mm/unit']

    # Call math_png.  If it fails, then return early.
    koko.globals.FRAME.status = "Parsing math string"
    
    if event.is_set(): return
    
    now = datetime.now()
    success, output = math_png(resolution=resolution, output=output,
                               event=event)
    dT = datetime.now() - now
    output += "#   math_png time: %f s\n\n#\n" % (dT.seconds +
                                             dT.microseconds / 1.0e6)

    if success is False:
        koko.globals.FRAME.output = output
    if not success:
        return
        
    koko.globals.CANVAS.border = None
    koko.globals.FRAME.status = ''
    
    if event.is_set(): return
    
    wx.CallAfter(lambda: koko.globals.CANVAS.load_image('_cad_ui_tmp.png', view))
    
    dT = datetime.now() - start_time
    output += "# #    Total time: %f s\n#" % (dT.seconds +
                                                   dT.microseconds / 1.0e6)
    koko.globals.FRAME.output = output



def read_math(filename='_cad_ui_tmp.math'):
    '''Parses a provided math file, returning a dictionary containing
       math file details.'''

    with open(filename, 'r') as f:
        lines = f.readlines()
        
    math = {}
    for line in lines:
        if 'format: ' in line:
            math['format'] = line[8:-1]
        elif 'mm per unit:' in line:
            math['mm/unit'] = float(line[12:])
        elif 'dx dy dz:' in line:
            [math['dx'], math['dy'], math['dz']] = \
                [float(v) for v in line[10:].split(' ')]
        elif 'xmin ymin zmin:' in line:
            [math['xmin'], math['ymin'], math['zmin']] = \
                [float(v) for v in line[16:].split(' ')]
        elif 'expression: ' in line:
            math['expression'] = line[12:]
    
    return math

def write_math(math, filename):
    '''Saves a math file with a given filename.'''
    
    new = '''format: %s
mm per unit: %f
dx dy dz: %f %f %f
xmin ymin zmin: %f %f %f
expression: %s''' %  (
    math['format'],
    math['mm/unit'],
    math['dx'], math['dy'], math['dz'],
    math['xmin'], math['ymin'], math['zmin'],
    math['expression'])

    with open(filename,'w') as f:
        f.write(new)

def rewrite_math(math, view, output='', filename='_cad_ui_tmp.math'):
    '''Saves a modified math file with bounds equal to the provided view.
    
       Returns edited output text.'''

    new = '''format: %s
mm per unit: %f
dx dy dz: %f %f %f
xmin ymin zmin: %f %f %f
expression: %s''' %  (
    math['format'],
    math['mm/unit'],
    view['xmax'] - view['xmin'], view['ymax'] - view['ymin'], math['dz'],
    view['xmin'], view['ymin'], math['zmin'],
    math['expression'])

    with open(filename,'w') as f:
        f.write(new)
        
    output = re.sub(
        'dx: [0-9.]+, dy: [0-9.]+, dz: [0-9.]+',
        'dx: %f, dy: %f, dz: %f' % (view['xmax'] - view['xmin'],
                                    view['ymax'] - view['ymin'],
                                    math['dz']),
        output)

    output = re.sub(
        'xmin: [-0-9.]+, ymin: [-0-9.]+, zmin: [-0-9.]+',
        'xmin: %f, ymin: %f, zmin: %f' %
        (view['xmin'], view['ymin'], math['zmin']), output)

    return output


################################################################################

class cad_variables(object):
    #
    # cad variables
    #
    def __init__(self):
        self.xmin = -1 # minimum x value to render
        self.xmax =  1 # maximum x value to render
        self.ymin = -1 # minimum y value to render
        self.ymax =  1 # maximum y value to render
        self.zmin =  0 # minimum z value to render
        self.zmax =  0 # maximum z value to render
        self.function = '' # cad function
        self.mm_per_unit = 1.0 # file units
        self.type = 'Boolean' # math string type
        
    @property
    def xmin(self): return self._xmin
    @xmin.setter
    def xmin(self, value): self._xmin = float(value)
    @property
    def xmax(self): return self._xmax
    @xmax.setter
    def xmax(self, value): self._xmax = float(value)
    
    @property
    def ymin(self): return self._ymin
    @ymin.setter
    def ymin(self, value): self._ymin = float(value)
    @property
    def ymax(self): return self._ymax
    @ymax.setter
    def ymax(self, value): self._ymax = float(value)
      
    @property
    def zmin(self): return self._zmin
    @zmin.setter
    def zmin(self, value): self._zmin = float(value)
    @property
    def zmax(self): return self._zmax
    @zmax.setter
    def zmax(self, value): self._zmax = float(value)
      
    @property
    def function(self): return self._function
    @function.setter
    def function(self, value): self._function = str(value)
        
    @property
    def mm_per_unit(self): return self._mm_per_unit
    @mm_per_unit.setter
    def mm_per_unit(self, value): self._mm_per_unit = float(value)
      
    @property
    def type(self): return self._type
    @type.setter
    def type(self, value): self._type = str(value)
    
################################################################################

def cad_math(filename=None, output='', event=threading.Event()):
    ''' Converts a cad file into a math file.  This should happen in a
        separate thread.
    
        Returns a tuple in the form (Success, Output), where success is
        None if interrupted, False if failed, True if success; Output
        is a string of output from the command.
        
        In case of failure, updates UI accordingly.
       
        Deletes the source .cad file on success.
    '''

    vars = {}
    exec('from string import *; from math import *', vars)
    vars.update(koko.globals.SHAPES.dict)
    vars['cad'] = cad_variables()
    
    output += '>>  Compiling to math file\n'
    
    math = {}
    buffer = StringIO.StringIO()
    sys.stdout = buffer

    try:
        exec(koko.globals.EDITOR.text.replace('koko.lib','lib'), vars)
    except:
        sys.stdout = sys.__stdout__
        koko.globals.CANVAS.border = (255, 0, 0)
        
        errors = traceback.format_exc()
        errors = errors[0] + ''.join(errors[3:])

        
        # Go through the set of errors and modify line numbers to match
        # the displayed file (since we may be adding lines to the beginning
        # to maintain backwards compatibility)
        for m in re.findall(r'line (\d+)', errors):
            error_line = int(m)
            
        output += buffer.getvalue()
        output += errors
        
        # Update the status line
        try:
            koko.globals.EDITOR.error_marker = error_line - 1
            koko.globals.FRAME.status = "cad_math failed (line %i)" % error_line
        except NameError:
            koko.globals.FRAME.status = "cad_math failed"

        return (False, output, math)

    sys.stdout = sys.__stdout__
    output += buffer.getvalue()
    
    cad = vars['cad']
    math['format'] = cad.type
    math['mm/unit'] = cad.mm_per_unit
    math['dx'], math['dy'], math['dz'] = (cad.xmax - cad.xmin,
                                          cad.ymax - cad.ymin,
                                          cad.zmax - cad.zmin)
    math['xmin'], math['ymin'], math['zmin'] = cad.xmin, cad.ymin, cad.zmin
    math['expression'] = cad.function
    
    if filename:
        write_math(math, filename)
    else:
        write_math(math, '_cad_ui_tmp.math')
    return (True, output, math)

################################################################################

def math_xyz(program, filename, resolution=None, monitor=None,
             output='', event=threading.Event(), frame=None):
    
    ''' Generic function to run math_png, math_svg, math_stl, etc.
    
        Returns tuple of (status, new output)
        
        where status is None if interrupted, False if failed, True otherwise
        and new output is the provided output plus new relevant lines.
    
    '''
    
    if BUNDLED:
        xyz_path = './%s' % program
    else:
        xyz_path = program
    
    
    if event.is_set(): return (None, output)

    command = [xyz_path] + ['_cad_ui_tmp.math', filename]
    if resolution: command += [str(resolution)]
    
    output += '>>  ' + ' '.join(command) + '\n'
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    
    # Run the monitor subprocess (which does things like producing
    # progress bars and updating the image)
    if monitor is None:
        monitor = progress_bar
    output += monitor(process, event=event, frame=frame)
    
    success = (process.returncode == 0)
    errors = process.stderr.read()
    
    # One more chance to abort before updating the GUI
    if event.is_set(): return (None, output)

    if not success:
        output += errors
        koko.globals.CANVAS.border = (255, 0, 0)
        koko.globals.FRAME.status = "%s failed" % program
        return (False, output)
    
    # If everything worked, then we delete the temporary file
    # and return True
    os.remove('_cad_ui_tmp.math')
    return (True, output)

################################################################################

def math_png(filename=None, resolution=10, output='',
             event=threading.Event(), frame=None):
    '''Invoke math_png.'''

    # If we aren't saving to a particular file, use the default
    if filename is None:
        filename = '_cad_ui_tmp.png'
    
    return math_xyz('math_png', filename, resolution=resolution,
                    output=output, event=event, frame=frame)

################################################################################

def math_stl(filename, resolution=1, output='',
             event=threading.Event(), frame=None):

    return math_xyz('math_stl', filename, output=output,
                    resolution=resolution, event=event, frame=frame)
    
################################################################################

def math_svg(filename, resolution=10, output='',
             event=threading.Event(), frame=None):

    return math_xyz('math_svg', filename, output=output,
                    resolution=resolution, event=event, frame=frame)

################################################################################

def math_dot(filename, output='', event=threading.Event(), frame=None):

    return math_xyz('math_dot', filename, output=output,
                    event=event, frame=frame)

################################################################################

def progress_bar(process, output='', event=threading.Event(), frame=None):
    ''' Waits for a process to finish, drawing a progress bar.
    
        Halts when the progress finishes or the event is set.
        
    '''
    
    # Helper function to read stdout without blocking.
    def enqueue_output(out, queue):
        c = out.read(1)
        while c:
            queue.put(c)
            c = out.read(1)
        
    q = Queue.Queue()
    t = threading.Thread(target=enqueue_output, args=(process.stdout, q))
    t.daemon = True
    t.start()
    
    line = ''
    while process.poll() is None:
        if event.is_set():
            process.terminate()
            process.wait()
            return output
        
        try:
            c = q.get_nowait()
        except Queue.Empty:
            continue
            
        if c == '\n' or c == '\r':
            if '[|' in line:
                line = line[4:]
                percent = (line.count('|') * 100) / (len(line) - 2)
                if percent < 100:
                    koko.globals.FRAME.status = "Rendering (%i%%)" % percent
                else:
                    koko.globals.FRAME.status = "Writing output file"
            else:
                output += line+'\n'
            line = ''
        else:
            line = line + c
    return output
    
################################################################################

def run_fab(filename='', event=threading.Event(), frame=None,
            set_fab=None):

    output = "####  Exporting to fab modules  ####\n"

    filename = filename.replace(' ','_')
    filename = 'fab_' + filename.replace('.cad','.math')
    if filename[-4:] != '.math':
        filename += '.math'
        
    success, output, math = cad_math(filename=filename, output=output,
                                     event=event, frame=frame)
                               
    # Check return code from cad_math
    if success is None:
        return
    elif success is False:
        koko.globals.FRAME.output = output
        return
    
    koko.globals.FRAME.output = output
    fab = subprocess.Popen(['fab',filename])
    fab.filename = filename
    
    set_fab(fab)
