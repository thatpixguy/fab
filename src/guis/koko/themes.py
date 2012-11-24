import wx
import wx.py
import wx.stc

class Theme:
    def __init__(self, txt, background, foreground, txtbox):
        self.txt = txt
        self.background = background
        self.foreground = foreground
        self.txtbox = txtbox
    
    def apply(self, target):
        if issubclass(target.__class__, wx.py.editwindow.EditWindow):
            for s in self.txt:
                target.StyleSetBackground(s[0], s[1])
                target.StyleSetForeground(s[0], s[2])
        elif issubclass(target.__class__, wx.TextCtrl):
            target.SetBackgroundColour(self.txtbox)
            target.SetForegroundColour(self.foreground)
        else:
            try:
                target.SetBackgroundColour(self.background)
                target.SetForegroundColour(self.foreground)
            except:
                pass
        return target

DARK_THEME = Theme(
    txt=[(wx.stc.STC_STYLE_DEFAULT,    '#000000', '#000000'),
         (wx.stc.STC_STYLE_LINENUMBER, '#303030', '#c8c8c8'),
         (wx.stc.STC_P_CHARACTER,      '#000000', '#ff73fd'),
         (wx.stc.STC_P_CLASSNAME,      '#000000', '#96cbfe'),
         (wx.stc.STC_P_COMMENTBLOCK,   '#000000', '#7f7f7f'),
         (wx.stc.STC_P_COMMENTLINE,    '#000000', '#a8ff60'),
         (wx.stc.STC_P_DEFAULT,        '#000000', '#ffffff'),
         (wx.stc.STC_P_DEFNAME,        '#000000', '#96cbfe'),
         (wx.stc.STC_P_IDENTIFIER,     '#000000', '#ffffff'),
         (wx.stc.STC_P_NUMBER,         '#000000', '#ffffff'),
         (wx.stc.STC_P_OPERATOR,       '#000000', '#ffffff'),
         (wx.stc.STC_P_STRING,         '#000000', '#ff73fd'),
         (wx.stc.STC_P_STRINGEOL,      '#000000', '#ffffff'),
         (wx.stc.STC_P_TRIPLE,         '#000000', '#ff6c60'),
         (wx.stc.STC_P_TRIPLEDOUBLE,   '#000000', '#96cbfe'),
         (wx.stc.STC_P_WORD,           '#000000', '#b5dcff')],
    background='#252525',
    foreground='#c8c8c8',
    txtbox='#353535')