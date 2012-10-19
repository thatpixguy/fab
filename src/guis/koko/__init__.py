import wx
from koko.app import App

def run():
    wx.Log.EnableLogging(False)
    app = App()
    app.MainLoop()