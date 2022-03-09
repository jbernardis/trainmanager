import wx

class CompletedTrainList(wx.ListCtrl):
	def __init__(self, parent, ct):
		self.parent = parent
		self.completedTrains = ct
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(280, 700),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)
		
		font = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		self.SetFont(font)


		self.InsertColumn(0, "Train")
		self.InsertColumn(1, "Engineer")
		self.InsertColumn(2, "Loco #")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 120)
		self.SetColumnWidth(2, 80)

		self.SetItemCount(0)

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

	def clear(self):
		self.SetItemCount(0)
		
	def update(self):
		self.SetItemCount(self.completedTrains.count())
		
	def addTrain(self, tr):
		self.activeTrains.append(tr)
		self.highlight.append(0)
		self.SetItemCount(len(self.activeTrains))

	def OnGetItemText(self, item, col):
		if item < 0 or item >= self.completedTrains.count():
			return None
		
		tid, engineer, loco = self.completedTrains.getTrain(item)
		if tid is None:
			return ""
	
		if col == 0:
			return tid
		elif col == 1:
			return engineer
		elif col == 2:
			if loco is None:
				return ""
			else:
				return loco

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
