import wx
import os

import koko.about as about
from koko.canvas import Canvas
from koko.editor import Editor
from koko.themes import DARK_THEME


class MainFrame(wx.Frame):
    def __init__(self, callbacks):
        wx.Frame.__init__(self, parent=None)
        
        # Bind menu callbacks        
        self.Bind(wx.EVT_MENU_HIGHLIGHT, self.OnMenuHighlight)
        self.Bind(wx.EVT_MENU_CLOSE, self.OnMenuClose)
        
        # Bind menu callbacks
        self.build_menus(callbacks)
        
        # Bind idle callback
        self.Bind(wx.EVT_IDLE, callbacks['idle'])
        
        #######################################################################

        
        #######################################################################
        # Create a canvas with a border and status text below
        canvasPanel = wx.Panel(self)
        canvasSizer = wx.BoxSizer(wx.VERTICAL)

        version = wx.StaticText(canvasPanel, label='%s %s ' % 
                                (about.NAME, about.VERSION))
        canvasSizer.Add(version, flag=wx.ALIGN_RIGHT)
        
        self.canvas = Canvas(canvasPanel, callbacks, size=(300, 300))
        canvasSizer.Add(self.canvas, proportion=2,
                        flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND,
                        border=20)
        
        # Add status text
        canvasSizer.Add((0,0), border=5, flag=wx.BOTTOM)
        self._status = wx.StaticText(
            canvasPanel, style=wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)
        canvasSizer.Add(self._status, border=20, flag=wx.EXPAND | wx.RIGHT)
        canvasSizer.Add((0,0), border=15, flag=wx.BOTTOM)
        
        # Add output panel for error messages, etc.
        self._output = Editor(canvasPanel, margins=False, style=wx.NO_BORDER, size=(300, 100))
        self._output.SetReadOnly(True)
        self._output.SetCaretLineVisible(False)
        self._output.SetWrapMode(wx.stc.STC_WRAP_WORD)
        
        self.hide_output = lambda: (self._output.Hide(), canvasPanel.Layout())
        self.show_output = lambda: (self._output.Show(), canvasPanel.Layout())
        
        canvasSizer.Add(self._output, border=20, proportion=1,
                        flag=wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT)
        canvasPanel.SetSizerAndFit(canvasSizer)
        #######################################################################
        
        
        #######################################################################
        # Pack everything into the window        

        editorPanel = wx.Panel(self)
        editorSizer = wx.BoxSizer(wx.VERTICAL)
        
        editorSizer.Add((0,0), border=15, flag=wx.TOP)
        self.editor = Editor(editorPanel, style=wx.NO_BORDER, size=(300, 400))
        self.editor.load_template()
        self.editor.bind_callbacks(callbacks)
        
        editorSizer.Add(self.editor, proportion=1, flag=wx.EXPAND)

        self._hint = wx.StaticText(editorPanel)
        editorSizer.Add(self._hint, border=5, flag=wx.ALL)

        editorPanel.SetSizerAndFit(editorSizer)
        
        #######################################################################
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(editorPanel, proportion=2, flag=wx.EXPAND)
        sizer.Add(canvasPanel, proportion=3, flag=wx.EXPAND)
        
        self.hide_script = lambda: (editorPanel.Hide(), self.Layout())
        self.show_script = lambda: (editorPanel.Show(), self.Layout())
        
        self.SetSizerAndFit(sizer)
        #######################################################################
        
        
        DARK_THEME.apply(self)
        DARK_THEME.apply(canvasPanel)
        DARK_THEME.apply(editorPanel)
        DARK_THEME.apply(version)
        DARK_THEME.apply(self._hint)
        DARK_THEME.apply(self._status)
        DARK_THEME.apply(self._output)
        DARK_THEME.apply(self.editor)
        
        self._status.SetForegroundColour(wx.Colour(100, 100, 100))

        self.hide_output()
        self.Maximize()
################################################################################
        
    def build_menus(self, callbacks):
        '''Build a set of menus and attach associated callbacks.'''
    
        def attach(menu, command, shortcut='', help='', wxID=wx.ID_ANY,
                   attach_function = None):
            '''Helper function to add an item to a menu and bind the
               associated callback.'''
            if shortcut:
                menu_text = '%s\t%s' % (command, shortcut)
            else:
                menu_text = command

            if not command in callbacks.keys():
                raise KeyError('Could not find callback for menu item "%s"' %
                               command)
                               
            if attach_function is None:
                item = menu.Append(wxID, menu_text, help)
            else:
                item = attach_function(wxID, menu_text, help)
                
            self.Bind(wx.EVT_MENU, callbacks[command], item)
            
            return item
        
        menu_bar = wx.MenuBar()
        
        file = wx.Menu()
        attach(file, 'New', 'Ctrl+N', 'Start a new design file', wx.ID_NEW)
        file.AppendSeparator()

        attach(file, 'Open', 'Ctrl+O', 'Open a design file', wx.ID_OPEN)
        attach(file, 'Reload', 'Ctrl+R', 'Reload the current file')
        
        file.AppendSeparator()
        
        attach(file, 'Save', 'Ctrl+S', 'Save the current file', wx.ID_SAVE)
        attach(file, 'Save As', 'Ctrl+Shift+S', 'Save the current file',
               wx.ID_SAVEAS)
        
        if not 'Darwin' in os.uname():
            file.AppendSeparator()
        
        attach(file, 'About', '', 'Display an About box', wx.ID_ABOUT)
        attach(file, 'Exit', 'Ctrl+Q', 'Terminate the program', wx.ID_EXIT)
        
        menu_bar.Append(file, 'File')
        
        view = wx.Menu()
        output = attach(view, 'Show output', '',
                        'Display errors in a separate pane',
                         attach_function=view.AppendCheckItem)
        script = attach(view, 'Show script', 'Ctrl+T',
                        'Display Python script',
                         attach_function=view.AppendCheckItem)
        script.Toggle()
        
        view.AppendSeparator()
        attach(view, 'Snap to bounds', '', 'Snap view to cad file bounds.')
        view.AppendSeparator()
        attach(view, 'Re-render', 'Ctrl+Enter', 'Re-render the output image')        
        
        menu_bar.Append(view, 'View')
        
        export = wx.Menu()
        attach(export, '.math', '', 'Export to .math file')
        attach(export, '.png', '', 'Export to image file')
        attach(export, '.svg', '', 'Export to svg file')
        attach(export, '.stl', '', 'Export to stl file')
        attach(export, '.dot', '', 'Export to dot / Graphviz file')
        export.AppendSeparator()
        self.start_fab = attach(export, 'Start fab modules', '',
                                'Load in fab modules')
        self.update_fab = attach(export, 'Update fab file', '',
                                 'Updates the file exported to the fab modules')
        self.update_fab.Enable(False)
        
        libraries = wx.Menu()
        attach(libraries, 'koko.lib.shapes', 'Standard shape library')
        attach(libraries, 'koko.lib.text', 'Standard text library')
        
    
        menu_bar.Append(export, 'Export')
        menu_bar.Append(libraries, 'Libraries')
        self.SetMenuBar(menu_bar)
        
################################################################################
    
    @property
    def status(self):
        return self._status.GetLabel()
    @status.setter
    def status(self, value):
        wx.CallAfter(self._status.SetLabel, value)
    
################################################################################
    
    @property
    def hint(self):
        return self._hint.GetLabel()
    @hint.setter
    def hint(self, value):
        wx.CallAfter(self._hint.SetLabel, value)
    
################################################################################
    
    @property
    def output(self):
        return self._output.text
    @output.setter
    def output(self, value):
        self._output.text = value
        
################################################################################

    def OnMenuHighlight(self, event):
        '''Sets an appropriate hint based on the highlighted menu item.'''
        id = event.GetMenuId()
        item = self.GetMenuBar().FindItemById(id)
        if not item or not item.GetHelp():
            self.hint = ''
        else:
            self.hint = item.GetHelp()
    
    def OnMenuClose(self, event):
        '''Clears the menu item hint.'''
        self.hint = ''