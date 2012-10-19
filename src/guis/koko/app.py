import wx

from koko.frame import MainFrame
from koko.about import AboutBox, NAME
import koko.dialogs as dialogs
import koko.cmd as cmd

import cPickle as pickle
import os
import Queue
import random
import sys
import threading


class App(wx.App):
    def OnInit(self):
        callbacks = {
            'New':     self.onNew,
            'Save':    self.onSave,
            'Save As': self.onSaveAs,
            'Reload':  self.onReload,
            'Open':    self.onOpen,
            'Exit':    self.onExit,
            'About':   AboutBox,
            'Show output':      self.show_output,
            'Show script':      self.show_script,
            'Snap to bounds':   self.snap_bounds,
            'Re-render':        self.onTextChange,
            'saved':   lambda e=None: self.savePoint(True),
            'unsaved': lambda e=None: self.savePoint(False),
            'text':    self.onTextChange,
            'view':    self.onViewChange,
            'idle':    self.idle,
            '.math':   self.export,
            '.png':    self.export,
            '.svg':    self.export,
            '.stl':    self.export,
            '.dot':    self.export,
            'Start fab modules': self.start_fab,
            'Update fab file':   self.update_fab,
            'koko.lib.shapes': self.show_library,
            'koko.lib.text':   self.show_library
            }
        
        self.threads = []
        
        # Math file and async queue to be given new math files
        # (from a worker thread)
        self.math = {}
        self.math_queue = Queue.Queue()
        
        # Subprocess containing the fab modules (for export)
        self.fab = None
        
        # Edit the system path to find things in the lib folder
        sys.path.append(os.path.join(sys.path[0], 'koko'))
        
        # Open a file from the command line
        if len(sys.argv) > 1:
            d, self.filename = os.path.split(sys.argv[1])
            self.directory = os.path.abspath(d)
        else:
            self.filename = ''
            self.directory = os.getcwd()
        
        # Create frame
        self.frame = MainFrame(callbacks)
        
        # Link to the canvas's point set
        self.shape_set = self.frame.canvas.shape_set
        
        if self.filename:
            self.load()
        

        
        # Update the window title
        self.savePoint(True)

        self.reeval_required = True
        self.render_required = True
        
        # Prevents interruptions during an export operation
        self.exporting = False
        
        # first_render causes the snaps the view to the cad file bounds.
        self.first_render = True
        
        # Render for the first time
        self.onTextChange()
        
        # Show the application!
        self.frame.Show()
        self.frame.canvas.SetFocus()
        
        return True
    
    
    @property
    def directory(self):
        return self._directory
    @directory.setter
    def directory(self, value):
        try:
            sys.path.remove(self._directory)
        except (AttributeError, ValueError):
            pass
        self._directory = value
        if self.directory != '':
            os.chdir(self.directory)
            sys.path.append(self.directory)

################################################################################
    
    def savePoint(self, value):
        '''Callback when a save point is reached in the editor.'''
        
        self.saved = value and not self.frame.canvas.unsaved

        s = '%s:  ' % NAME
        if self.filename:
            s += self.filename
        else:
            s += '[Untitled]'

        if not self.saved:
            s += '*'

        self.frame.SetTitle(s)


################################################################################

    def onNew(self, evt=None):
        '''Creates a new file from the default template.'''
        if self.saved or dialogs.warn_changes():
            self.filename = ''
            self.frame.editor.load_template()
            self.frame.canvas.shape_set.clear()
            if self.frame.canvas.edit_panel:
                self.frame.canvas.close_edit_panel()
            self.first_render = True

################################################################################        

    def onSave(self, evt=None):  
        '''Save callback from main menu.'''
        
        # If we don't have a filename, perform Save As instead
        if self.filename == '':
            self.onSaveAs()
        else:
            # Write out the file
            path = os.path.join(self.directory, self.filename)
            
            if '.cad' in path:
                if self.frame.canvas.shape_set.reconstructor() != []:
                    dialogs.warning(
'''Must save as .ko file, as .cad files do not include
interactive geometry features.

Please pick a new filename.''')
                    self.onSaveAs()
                    return
                with open(path, 'w') as f:
                    f.write(self.frame.editor.text)
            else:            
                with open(path, 'w') as f:               
                    text = self.frame.editor.text
                    shapes = self.frame.canvas.shape_set.reconstructor()
                    pickle.dump({'text': text, 'shapes': shapes}, f)
        
            # Tell the canvas and editor that we've saved
            # (this invokes the callback to change title text)
            self.frame.canvas.unsaved = False
            self.frame.editor.SetSavePoint()
            
            # Update the status box.
            self.frame.status = 'Saved file %s' % self.filename
        
################################################################################
        
    def onSaveAs(self, evt=None):
        '''Save As callback from main menu.'''
        
        # Open a file dialog to get target
        df = dialogs.save_as(self.directory, extension='.ko')
        
        if df[1] != '':    
            self.directory, self.filename = df
            self.onSave()
        
################################################################################

    def onReload(self, evt=None):
        '''Reloads the current file, warning if necessary.'''
        if self.filename != ''  and (self.saved or dialogs.warn_changes()):
            self.load()
    
################################################################################

    def load(self):
        '''Loads text from the current file.'''
        
        # Forget the old math file
        self.math = {}
        
        path = os.path.join(self.directory, self.filename)
        
        self.frame.canvas.shape_set.clear()
        if self.frame.canvas.edit_panel:
            self.frame.canvas.close_edit_panel()
        self.frame.canvas.Refresh()
        
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
        except:
            with open(path, 'r') as f:
                self.frame.editor.text = f.read()
                self.frame.status = 'Loaded .cad file'
        else:
            self.frame.editor.text = data['text']
            self.shape_set.reconstruct(data['shapes'])
            self.frame.status = 'Loaded .ko file'
            
        self.frame.canvas.unsaved = False
        self.first_render = True
            
    
################################################################################

    def onOpen(self, evt=None):
        ''' Open callback from main menu.'''
        # Open a file dialog to get target
        if self.saved or dialogs.warn_changes():
            df = dialogs.open_file(self.directory)
            if df[1] != '':
                self.directory, self.filename = df
                self.load()
       
################################################################################

    def onExit(self, evt=None):
        '''Exits after warning of unsaved changes.'''
        if self.saved or dialogs.warn_changes():
            self.frame.Destroy()

################################################################################

    def show_output(self, evt):
        if evt.Checked():
            self.frame.show_output()
        else:
            self.frame.hide_output()

################################################################################

    def show_script(self, evt):
        if evt.Checked():
            self.frame.show_script()
        else:
            self.frame.hide_script()

################################################################################

    def snap_bounds(self, evt=None):
        if self.math:
            self.frame.canvas.snap_bounds(self.math)

################################################################################

    def onTextChange(self, evt=None):
        # Mark that we need to run cad_math again
        self.reeval_required = True
                
        # Set a syntax hint in the frame
        self.frame.hint = self.frame.editor.syntax_helper()

    
    def onViewChange(self):
        self.render_required = True
        
################################################################################

    def start_thread(self, callable, *args, **kwargs):
        '''Starts a new thread.  The called function must accept
           an event argument (used to interrupt) and a frame argument
           (which it will use to update the GUI)'''
        e = threading.Event()
        kwargs.update({'event':e, 'frame':self.frame})
        t = threading.Thread(target=callable, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
        self.threads += [(t, e)]
        
################################################################################

    def stop_threads(self):
        ''' Tells all threads to stop at their earliest convenience.
        '''
        for thread, event in self.threads:
            event.set()
            
################################################################################

    def idle(self, evt=None):

        # Check the threads and clear out any that are dead
        self.monitor_threads()
        
        # Re-evaluate the geometry if necessary.  This may lead to
        # a full expression re-eval.
        if self.shape_set.reeval_required:
            self.reeval_required = True
            self.shape_set.reeval_required = False
        
        # Pull the latest math file from the queue
        while True:
            try:
                self.math = self.math_queue.get_nowait()
            except Queue.Empty:
                break

            # Snap the bounds to the math file if this was the first render.
            if self.math and self.first_render:
                self.frame.canvas.snap_bounds(self.math)
                self.first_render = False
                self.reeval_required = True
        
        
        # If the fab modules were invoked but are now dead, then
        # remove the temporary file and set self.fab to None
        if self.fab and self.fab.poll() is not None:
            os.remove(self.fab.filename)
            self.fab = None
            self.frame.start_fab.SetText('Start fab modules')
            self.frame.start_fab.Enable(True)
            self.frame.update_fab.Enable(False)

        # Re-render if necessary
        if not self.exporting:        
            # We can't render until we have a valid math file
            if self.render_required and not self.math:
                self.render_required = False
                self.reeval_required = True
            
            # Recalculate math file then render
            if self.reeval_required:
                self.reeval_required = False
                self.render_required = False
                self.reeval()
                
            # Render given valid math file
            if self.render_required:
                self.render_required = False
                self.render()

################################################################################

    def monitor_threads(self, evt=None):
        ''' Monitor the list of active threads, joining those that are dead.
        
            This function runs in the wx IDLE callback, so it is continuously
            checking in the background.
        '''
        
        dead_threads = filter(lambda (thread, event): not thread.is_alive(),
                              self.threads)
        
        for thread, event in dead_threads:
            thread.join()
        
        self.threads = filter(lambda t: t not in dead_threads, self.threads)
        
        # If we're exporting, then clear the marker once all threads are done
        if self.exporting and self.threads == []:
            self.exporting = False
            
################################################################################

    def render(self):
        ''' Render the image, given the existing math file.'''
        # Tell all of the existing threads to stop (politely)
        self.stop_threads()
        
        # Start up a new thread to render and load the image.
        self.start_thread(cmd.render, math=self.math)
    
    def reeval(self):
        ''' Render the image, calculating a new math file.'''
        # Tell all of the existing threads to stop (politely)
        self.stop_threads()

        # Start up a new thread to render and load the image.
        self.start_thread(cmd.render, queue=self.math_queue)
            
################################################################################

    def export(self, event):
        ''' General-purpose export callback.  Decides which export
            command to call based on the menu item text.'''
        
        item = self.frame.GetMenuBar().FindItemById(event.GetId())
        filetype = item.GetLabel()
        
        if filetype in ['.png', '.svg', '.stl']:
            resolution = dialogs.resolution(10)
            if resolution is False:
                return
        
        df = dialogs.save_as(self.directory, extension=filetype)
        if df[1] == '':
            return
        path = os.path.join(*df)
        
        self.exporting = True
        if filetype   == '.math':
            self.start_thread(cmd.export_math, path)
        elif filetype == '.dot':
            self.start_thread(cmd.export_dot, path)
        elif filetype == '.png':
            self.start_thread(cmd.export_png, path,
                              resolution=resolution)
        elif filetype == '.svg':
            self.start_thread(cmd.export_svg, path,
                              resolution=resolution)
        elif filetype == '.stl':
            self.start_thread(cmd.export_stl, path,
                              resolution=resolution)
        
################################################################################
    
    def start_fab(self, event=None):
        ''' Starts the fab modules.'''
            
        self.exporting = True
    
        self.frame.start_fab.Enable(False)
        self.frame.start_fab.SetText('fab modules are running')
        self.frame.update_fab.Enable(True)
        
        self.start_thread(cmd.run_fab, filename=self.filename,
                          set_fab=self.set_fab)
    
    def update_fab(self, event=None):
        '''Re-exports the file being accessed by the fab modules.'''
        self.start_thread(cmd.export_math, self.fab.filename)
    
################################################################################
    
    def set_fab(self, fab):
        ''' Informs the app of the subprocess containing the fab modules. '''
        self.fab = fab

################################################################################
    
    def show_library(self, event):
    
        item = self.frame.GetMenuBar().FindItemById(event.GetId())
        
        name = item.GetLabel().replace('koko.','')
        v = {}
        exec('import %s as module' % name, v)
        path = v['module'].__file__.replace('.pyc','.py')
        
        dialogs.Library(self.frame, name, path)