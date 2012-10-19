import wx

import koko.editor
from koko.themes import DARK_THEME

def warn_changes():
    '''Check to see if the user is ok with abandoning unsaved changes.
       Returns True if we should proceed.'''
    dlg = wx.MessageDialog(None, "All unsaved changes will be lost.",
                           "Warning:",
                           wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION)
    result = dlg.ShowModal()
    dlg.Destroy()
    return result == wx.ID_OK

################################################################################

def warning(text):
    '''General-purpose warning box.'''
    dlg = wx.MessageDialog(None, text, "Warning:",
                           wx.OK | wx.ICON_EXCLAMATION)
    dlg.ShowModal()
    dlg.Destroy()

################################################################################
    
def save_as(directory, filename='', extension='.*'):
    '''Prompts a Save As dialog, returning directory, filename.'''
    
    dlg = wx.FileDialog(None, "Choose a file",
                        directory, '', '*%s' % extension,
                        wx.FD_SAVE)
                        
    if dlg.ShowModal() == wx.ID_OK:
        directory, filename = dlg.GetDirectory(), dlg.GetFilename()
            
    dlg.Destroy()
    return directory, filename
    
################################################################################

def open_file(directory, filename=''):
    '''Prompts an Open dialog, returning directory, filename.'''
    dlg = wx.FileDialog(None, "Choose a file", directory, style=wx.FD_OPEN)

    if dlg.ShowModal() == wx.ID_OK:    
        directory, filename = dlg.GetDirectory(), dlg.GetFilename()
        
    dlg.Destroy()
    return directory, filename

################################################################################

class ResolutionDialog(wx.Dialog):
    def __init__(self, res):
        wx.Dialog.__init__(self, parent=None, title='Export')
        self.value = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
        
        self.value.Bind(wx.EVT_CHAR, self.LimitToNumbers)
        self.value.Bind(wx.EVT_TEXT_ENTER, self.Done)
        
        self.value.ChangeValue(str(res))
        
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.value, flag=wx.ALL, border=10)
        okButton = wx.Button(self, label='OK')
        okButton.Bind(wx.EVT_BUTTON, self.Done)
        hbox.Add(okButton, flag=wx.ALL, border=10)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(wx.StaticText(self, -1, 'Resolution (pixels/mm):'),
                 flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(hbox)
        
        self.SetSizerAndFit(vbox)

    def LimitToNumbers(self, event):
        valid = '0123456789'
        if not '.' in self.value.GetValue():
            valid += '.'
            
        keycode = event.GetKeyCode()
        if keycode < 32 or keycode >= 127 or chr(keycode) in valid:
            event.Skip()


    def Done(self, event):
        self.result = self.value.GetValue()
        self.EndModal(wx.ID_OK)


def resolution(resolution):
    '''Create a resolution dialog and return the result.'''
    dlg = ResolutionDialog(resolution)
    result = dlg.ShowModal()
    if result == wx.ID_OK:
        resolution = dlg.result
    else:
        resolution = False
    dlg.Destroy()
    return resolution
    
################################################################################

class Library(wx.Frame):
    '''A simple text frame to display the contents of a standard library.'''
    def __init__(self, parent, title, filename):
        wx.Frame.__init__(self, parent, title=title)

        # Create text pane.
        txt = koko.editor.Editor(self, margins=False, style=wx.NO_BORDER,
                                 size=(600, 400))
        txt.SetCaretLineVisible(0)
        txt.SetReadOnly(True)
                
        with open(filename, 'r') as f:
            txt.text = f.read()

        
        DARK_THEME.apply(txt)
        DARK_THEME.apply(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(txt, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizerAndFit(sizer)
        self.Show()