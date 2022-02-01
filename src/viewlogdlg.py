import wx

class ViewLogDlg(wx.Dialog):
	def __init__(self, parent, log):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Log Viewer")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.parent = parent
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		te = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY | wx.TE_MULTILINE, size=(400, 400))
		for ln in log:
			te.AppendText("%s\n" % ln)
			
		vsizer.Add(te)
		
		vsizer.AddSpacer(20)

		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)	   
		hsizer.AddSpacer(20)
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit();
		
		
	def onClose(self, _):
		self.EndModal(wx.ID_OK)

