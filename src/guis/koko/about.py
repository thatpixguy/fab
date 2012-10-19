NAME = 'kokopelli'
VERSION = '0.05'

import wx
class AboutBox():
    def __init__(self, evt=None):
        '''Displays an About box with information about this program.'''
        info = wx.AboutDialogInfo()
        info.SetName(NAME)
        info.SetVersion(VERSION)
        info.SetDescription('An interactive design tool for .cad files.')
        info.SetWebSite('http://kokompe.cba.mit.edu')
        info.SetCopyright('(C) 2012 Matthew Keeter')
        wx.AboutBox(info)