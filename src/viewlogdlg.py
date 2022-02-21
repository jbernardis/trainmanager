import wx

BTNSZ = (120, 46)

class ViewLogDlg(wx.Dialog):
	def __init__(self, parent, log):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Log Viewer")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.parent = parent
		self.index = 0
		self.textToFind = None
		
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))

		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		self.teLog = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_NOHIDESEL, size=(800, 800))
		self.teLog.SetFont(textFont)
		self.logData = ""
		for ln in log:
			line = "%s\n" % ln
			self.teLog.AppendText(line)
			self.logData += line + "\r"
			
		vsizer.Add(self.teLog)
		
		vsizer.AddSpacer(20)

		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)	   
		hsizer.AddSpacer(20)
		
		bsizer = wx.BoxSizer(wx.HORIZONTAL)

		self.teTextToFind = wx.TextCtrl(self, wx.ID_ANY, "")
		self.teTextToFind.SetFont(textFont)
		bsizer.Add(self.teTextToFind, 0, wx.TOP, 8)	
		bsizer.AddSpacer(20)	
		self.bFind = wx.Button(self, wx.ID_ANY, "Find", size=BTNSZ)
		self.bFind.SetFont(btnFont)
		bsizer.Add(self.bFind)
		bsizer.AddSpacer(20)	
		self.bNext = wx.Button(self, wx.ID_ANY, "Next", size=BTNSZ)
		self.bNext.SetFont(btnFont)
		bsizer.Add(self.bNext)
		self.Bind(wx.EVT_BUTTON, self.onBFind, self.bFind)
		self.Bind(wx.EVT_BUTTON, self.onBNext, self.bNext)
		
		
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.Add(hsizer)
		sz.Add(bsizer, 1, wx.ALIGN_CENTER_HORIZONTAL)
		sz.AddSpacer(30)
		
		self.SetSizer(sz)
		self.Layout()
		self.Fit();		
		
	def onBFind(self, _):
		self.textToFind = self.teTextToFind.GetValue()
		if not self.findText(self.textToFind, 0):
			dlg = wx.MessageDialog(self, 'Search string not found.',
	                               'Not Found',
	                               wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()

		
	def onBNext(self, _):
		if self.textToFind is None:
			return
		
		if not self.findText(self.textToFind, self.index+1):
			dlg = wx.MessageDialog(self, 'Search string not found.\nPress "Next" again to wrap to the start of the log',
	                               'Not Found',
	                               wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
		
	def findText(self, text, start):
		self.index = self.logData.find(text, start)
		if self.index == -1:
			self.index = 0
			return False
		else:
			self.teLog.ShowPosition(self.index)
			self.teLog.SetSelection(self.index, self.index+len(text))
			return True
		
	def onClose(self, _):
		self.EndModal(wx.ID_OK)
