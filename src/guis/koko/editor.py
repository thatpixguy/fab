import wx
import wx.py

import re
import inspect

from koko.themes import DARK_THEME
from koko.template import TEMPLATE

class Editor(wx.py.editwindow.EditWindow):
    '''Derived class for editing design scripts.'''
    
    def __init__(self, parent, margins=True, **kwargs):
        wx.py.editwindow.EditWindow.__init__(
            self, parent, **kwargs)

        if margins:
            # Margin for numbers
            self.SetMarginWidth(2, 16)
            self.SetMarginType(2,wx.stc.STC_MARGIN_NUMBER)
        
            # Margin for error marks
            self.SetMarginWidth(1, 16)
            self.SetMarginType(1, wx.stc.STC_MARGIN_SYMBOL)
            self.MarkerDefine(0, wx.stc.STC_MARK_SHORTARROW, 'black','red')

            # Margin for spacing
            self.SetMarginWidth(3, 4)

        # Line ending mode
        self.SetEOLMode(wx.stc.STC_EOL_LF)
        
        # Disable text editor callback on line marker changes,
        # to prevent infinite recursion
        self.SetModEventMask(wx.stc.STC_MODEVENTMASKALL &                         
                            ~wx.stc.STC_MOD_CHANGEMARKER &
                            ~wx.stc.STC_MOD_CHANGESTYLE)
        
        # Make cmd+left and cmd+right home and end
        self.CmdKeyAssign(wx.stc.STC_KEY_LEFT, 
                          wx.stc.STC_SCMOD_CTRL,
                          wx.stc.STC_CMD_VCHOME)
        self.CmdKeyAssign(wx.stc.STC_KEY_RIGHT,
                          wx.stc.STC_SCMOD_CTRL,
                          wx.stc.STC_CMD_LINEEND)
        self.CmdKeyAssign(wx.stc.STC_KEY_UP, 
                          wx.stc.STC_SCMOD_CTRL,
                          wx.stc.STC_CMD_DOCUMENTSTART)
        self.CmdKeyAssign(wx.stc.STC_KEY_DOWN,
                          wx.stc.STC_SCMOD_CTRL,
                          wx.stc.STC_CMD_DOCUMENTEND)

        self.CmdKeyAssign(wx.stc.STC_KEY_LEFT, 
                          wx.stc.STC_SCMOD_CTRL | wx.stc.STC_SCMOD_SHIFT,
                          wx.stc.STC_CMD_VCHOMEEXTEND)
        self.CmdKeyAssign(wx.stc.STC_KEY_RIGHT,
                          wx.stc.STC_SCMOD_CTRL | wx.stc.STC_SCMOD_SHIFT,
                          wx.stc.STC_CMD_LINEENDEXTEND)
        self.CmdKeyAssign(wx.stc.STC_KEY_UP, 
                          wx.stc.STC_SCMOD_CTRL | wx.stc.STC_SCMOD_SHIFT,
                          wx.stc.STC_CMD_DOCUMENTSTARTEXTEND)
        self.CmdKeyAssign(wx.stc.STC_KEY_DOWN,
                          wx.stc.STC_SCMOD_CTRL | wx.stc.STC_SCMOD_SHIFT,
                          wx.stc.STC_CMD_DOCUMENTENDEXTEND)


        # Apply a dark theme to the editor
        self.SetCaretForeground('#888888')
        
        # Add a faint highlight to the selected line
        self.SetCaretLineVisible(True)
        self.SetCaretLineBack('#303030')
        
        # Don't show horizontal scroll bar
        self.SetUseHorizontalScrollBar(False)

    def bind_callbacks(self, callbacks):
        '''Binds callbacks.'''
        self.Bind(wx.stc.EVT_STC_SAVEPOINTLEFT,
                  callbacks['unsaved'])
        self.Bind(wx.stc.EVT_STC_SAVEPOINTREACHED,
                  callbacks['saved'])
        self.Bind(wx.stc.EVT_STC_CHANGE, callbacks['text'])
            
        self.Bind(wx.EVT_ENTER_WINDOW, lambda e: self.SetFocus())

################################################################################
    
    def load_template(self):
        self.text = TEMPLATE
        
################################################################################
    
    def syntax_helper(self):
        line, pos = self.GetCurLine()
        line = line[:pos + 1]
        
        # Find all "import" statements in the text and run them
        imports = filter(lambda L: 'import' in L, self.text.split('\n'))
        imported = {}
        for i in imports:
            try:
                exec(i, imported)
            except (SyntaxError, ImportError):
                continue
        
        # Filter the functions to only include those that are callable
        # and can be analyzed with inspect.
        for k in imported.keys():
            if not callable(imported[k]):
                del imported[k]
            else:
                try:
                    inspect.getargspec(imported[k])
                except TypeError:
                    del imported[k]
        
        # Pick out valid symbols in the line of code
        symbols = re.findall('[a-zA-Z_][0-9a-zA-Z_]*', line)
        
        # Sort through defined functions in cad_shapes and cad_text
        # for matches with our found symbols.
        matches = []
        for sym in symbols[::-1]:
            for k in imported.keys():
                if k.startswith(sym):
                    score = float(len(sym)) / float(len(k))
                    matches += [(score, k)]
            if matches:
                break
        
        # If we found no valid matches, then stop searching.
        if matches == []:
            return ''
        
        # Find the match with the highest score.
        match = reduce(lambda x,y: x if x[0] >= y[0] else y, matches)
        
        # Get the function
        f = imported[match[1]]
        
        # Get its arguments and defaults
        args = inspect.getargspec(f)
        
        # Format them nicely
        args = inspect.formatargspec(args.args, args.varargs,
                                     args.keywords, args.defaults)
        
        # And return them to the hint
        return match[1] + args

################################################################################

    @property
    def text(self):
        return self.GetText()
    @text.setter
    def text(self, t):
        '''Loads a body of text into the editor, locking and unlocking
           if necessary.'''
        if self.GetReadOnly():
            readonly = True
            wx.CallAfter(self.SetReadOnly, False)
        else:
            readonly = False
        wx.CallAfter(self.SetText, t)
        wx.CallAfter(self.EmptyUndoBuffer)
        wx.CallAfter(self.SetSavePoint)
        if readonly:
            wx.CallAfter(self.SetReadOnly, True)
    
################################################################################
    
    @property
    def error_marker(self):
        return None
    @error_marker.setter
    def error_marker(self, line):
        wx.CallAfter(self.MarkerDeleteAll, 0)
        wx.CallAfter(self.MarkerAdd, line, 0)
    @error_marker.deleter
    def error_marker(self):
        wx.CallAfter(self.MarkerDeleteAll, 0)