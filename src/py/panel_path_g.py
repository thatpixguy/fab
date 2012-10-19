#
# panel_path_g.py
#    make .g from .path
#
# Neil Gershenfeld
# CBA MIT 2/26/11
#
# (c) Massachusetts Institute of Technology 2011
# Permission granted for experimental and personal use;
# license for commercial sale available from MIT.
#
# imports
#
import wx,os
#
# panel class
#
class path_g_panel(wx.Panel):
   def __init__(self,parent):
      self.parent = parent
      self.parent.path_file = ''
      #
      # make file
      #
      def make_file(event):
         if (self.parent.path_file == ''):
            print 'panel_path_g: oops -- need path file'
            return
         self.parent.g_file = self.parent.tmp+self.parent.rootname+'.g'
         if (self.conv.GetValue()):
            direction = '0'
         else:
            direction = '1'
         self.parent.g_file = self.parent.tmp+self.parent.rootname+'.g'
         height = self.height.GetValue()
         plunge = self.plunge.GetValue()
         speed = self.speed.GetValue()
         spindle = self.spindle.GetValue()
         tool = self.tool.GetValue()
         if (self.on.GetValue()):
            coolant = '1'
         else:
            coolant = '0'
         command = 'path_g '+'\"'+self.parent.path_file+'\"'+' '+'\"'+self.parent.g_file+'\"'+' '+direction+' '+height+' '+speed+' '+plunge+' '+spindle+' '+tool+' '+coolant
         print command
         os.system(command)
         self.button.SetMaxSize((self.parent.xsize,self.parent.ysize))
         self.button.SetMinSize((self.parent.xsize,self.parent.ysize))
         self.button.Show()
         self.parent.Layout()
         self.parent.Fit()
      #
      # send
      #
      def fab_send(event):
         command = 'fab_send '+'\"'+self.parent.g_file+'\"'
         print command
         os.system(command)
      #
      # panel
      #
      wx.Panel.__init__(self,parent)
      self.sizer = wx.GridBagSizer(10,10)
      self.SetSizer(self.sizer)
      #
      # label
      #
      label = wx.StaticText(self,label='to: g')
      bold_font = wx.Font(10,wx.DEFAULT,wx.NORMAL,wx.BOLD)
      label.SetFont(bold_font)
      self.sizer.Add(label,(0,0),span=(1,2),flag=wx.ALIGN_CENTER_HORIZONTAL)
      #
      # send
      #
      self.button = wx.Button(self,label='send it!')
      self.button.Bind(wx.EVT_BUTTON,fab_send)
      self.button.SetFont(bold_font)
      self.sizer.Add(self.button,(1,0),span=(1,2),flag=(wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL))
      self.button.Hide()
      #
      # controls
      #
      make = wx.Button(self,label='make .g')
      make.Bind(wx.EVT_BUTTON,make_file)
      self.sizer.Add(make,(2,0),span=(1,2),flag=wx.ALIGN_CENTER_HORIZONTAL)
      #
      dir_panel = wx.Panel(self)
      dir_sizer = wx.GridBagSizer(10,10)
      dir_panel.SetSizer(dir_sizer)
      self.conv = wx.RadioButton(dir_panel,label='conventional',style=wx.RB_GROUP)
      dir_sizer.Add(self.conv,(0,0))
      self.climb = wx.RadioButton(dir_panel,label='climb')
      dir_sizer.Add(self.climb,(0,1))
      self.sizer.Add(dir_panel,(3,0),span=(1,2),flag=wx.ALIGN_CENTER_HORIZONTAL)
      #
      row4_panel = wx.Panel(self)
      row4_sizer = wx.GridBagSizer(10,10)
      row4_panel.SetSizer(row4_sizer)
      row4_sizer.Add(wx.StaticText(row4_panel,label='      cut speed (mm/s)'),(0,0),flag=(wx.ALIGN_RIGHT))
      row4_sizer.Add(wx.StaticText(row4_panel,label='plunge speed (mm/s)'),(0,1),flag=(wx.ALIGN_LEFT))
      self.sizer.Add(row4_panel,(4,0),span=(1,2),flag=(wx.ALIGN_CENTER_HORIZONTAL))
      #
      row5_panel = wx.Panel(self)
      row5_sizer = wx.GridBagSizer(10,10)
      row5_panel.SetSizer(row5_sizer)
      self.speed = wx.TextCtrl(row5_panel,-1,'5')
      row5_sizer.Add(self.speed,(0,0),flag=(wx.ALIGN_RIGHT))
      self.plunge = wx.TextCtrl(row5_panel,-1,'2.5')
      row5_sizer.Add(self.plunge,(0,1),flag=(wx.ALIGN_LEFT))
      self.sizer.Add(row5_panel,(5,0),span=(1,2),flag=(wx.ALIGN_CENTER_HORIZONTAL))
      #
      row6_panel = wx.Panel(self)
      row6_sizer = wx.GridBagSizer(10,10)
      row6_panel.SetSizer(row6_sizer)
      row6_sizer.Add(wx.StaticText(row6_panel,label='spindle speed (RPM)'),(0,0),flag=(wx.ALIGN_RIGHT))
      row6_sizer.Add(wx.StaticText(row6_panel,label='jog height (mm)     '),(0,1),flag=(wx.ALIGN_LEFT))
      self.sizer.Add(row6_panel,(6,0),span=(1,2),flag=(wx.ALIGN_CENTER_HORIZONTAL))
      #
      row7_panel = wx.Panel(self)
      row7_sizer = wx.GridBagSizer(10,10)
      row7_panel.SetSizer(row7_sizer)
      self.spindle = wx.TextCtrl(row7_panel,-1,'10000')
      row7_sizer.Add(self.spindle,(0,0),flag=(wx.ALIGN_RIGHT))
      self.height = wx.TextCtrl(row7_panel,-1,'5')
      row7_sizer.Add(self.height,(0,1),flag=(wx.ALIGN_LEFT))
      self.sizer.Add(row7_panel,(7,0),span=(1,2),flag=(wx.ALIGN_CENTER_HORIZONTAL))
      #
      row8_panel = wx.Panel(self)
      row8_sizer = wx.GridBagSizer(10,10)
      row8_panel.SetSizer(row8_sizer)
      row8_sizer.Add(wx.StaticText(row8_panel,label='tool number'),(0,0),flag=(wx.ALIGN_RIGHT))
      row8_sizer.Add(wx.StaticText(row8_panel,label='coolant        '),(0,1),flag=(wx.ALIGN_LEFT))
      self.sizer.Add(row8_panel,(8,0),span=(1,2),flag=(wx.ALIGN_CENTER_HORIZONTAL))
      #
      row9_panel = wx.Panel(self)
      row9_sizer = wx.GridBagSizer(10,10)
      row9_panel.SetSizer(row9_sizer)
      self.tool = wx.TextCtrl(row9_panel,-1,'1')
      row9_sizer.Add(self.tool,(0,0),flag=(wx.ALIGN_RIGHT))
      coolant_panel = wx.Panel(row9_panel)
      coolant_sizer = wx.GridBagSizer(10,10)
      coolant_panel.SetSizer(coolant_sizer)
      self.on = wx.RadioButton(coolant_panel,label='on',style=wx.RB_GROUP)
      coolant_sizer.Add(self.on,(0,0))
      self.off = wx.RadioButton(coolant_panel,label='no')
      coolant_sizer.Add(self.off,(0,1))
      row9_sizer.Add(coolant_panel,(0,1),flag=wx.ALIGN_LEFT)
      self.sizer.Add(row9_panel,(9,0),span=(1,2),flag=(wx.ALIGN_CENTER_HORIZONTAL))
      #
      # fit
      #
      self.Fit()
