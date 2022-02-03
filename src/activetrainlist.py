import wx

class ActiveTrainList(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(925, 240),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)
		
		font = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		self.SetFont(font)


		self.InsertColumn(0, "Train")
		self.InsertColumn(1, "Dir")
		self.InsertColumn(2, "Origin")
		self.InsertColumn(3, "Terminus")
		self.InsertColumn(4, "Engineer")
		self.InsertColumn(5, "Loco #")
		self.InsertColumn(6, "Train Description")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 120)
		self.SetColumnWidth(3, 120)
		self.SetColumnWidth(5, 80)
		self.SetColumnWidth(6, 360)

		self.SetItemCount(0)
		self.activeTrains = []

		self.attr1 = wx.ItemAttr()
		self.attr1.SetBackgroundColour(wx.Colour(164, 255, 214)) # light Blue
		self.attr2 = wx.ItemAttr()
		self.attr2.SetBackgroundColour(wx.Colour( 85, 255, 179)) # blue
		self.attr3 = wx.ItemAttr()
		self.attr3.SetBackgroundColour(wx.Colour(252, 169, 186)) # light red
		self.attr4 = wx.ItemAttr()
		self.attr4.SetBackgroundColour(wx.Colour(251, 145, 166)) # red
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)
			
	def clear(self):
		self.SetItemCount(0)
		self.activeTrains = []
		
	def count(self):
		return len(self.activeTrains)
			
	def getSelection(self):
		if self.selected is None:
			return None
		
		if self.selected < 0 or self.selected >= len(self.activeTrains):
			return None
		
		return self.activeTrains[self.selected]
			
	def setSelection(self, tx):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			
		self.parent.reportSelection(tx)
		
	def getTrains(self):
		return [tr["tid"] for tr in self.activeTrains]
	
	def getTrainByTid(self, tid):
		for tr in self.activeTrains:
			if tr["tid"] == tid:
				return tr
			
		return None
	
	def updateTrain(self, tid, loco, desc):
		for tx in range(len(self.activeTrains)):
			if self.activeTrains[tx]["tid"] == tid:
				self.activeTrains[tx]["loco"] = loco
				self.activeTrains[tx]["descr"] = desc
				self.RefreshItem(tx)
				return
		
	def addTrain(self, tr):
		self.activeTrains.append(tr)
		self.SetItemCount(len(self.activeTrains))
		
	def getEngineers(self):
		return [x["engineer"] for x in self.activeTrains if x["engineer"] != "ATC"]
	
	def setNewEngineer(self, neng):
		if self.selected is None:
			return False
		if self.selected < 0 or self.selected >= len(self.activeTrains):
			return False
		
		self.activeTrains[self.selected]["engineer"] = neng
		self.RefreshItem(self.selected)
		
		return True
		
	def delSelected(self):
		if self.selected is None:
			return False
		if self.selected < 0 or self.selected >= len(self.activeTrains):
			return False
		
		del self.activeTrains[self.selected]
		self.SetItemCount(len(self.activeTrains))
		self.setSelection(None)
		ct = self.GetItemCount()
		for x in range(0, ct):
			self.Select(x, on=0)
			self.RefreshItems(0, ct-1)
		return True
				
	def OnItemSelected(self, event):
		self.setSelection(event.Index)
		
	def OnItemActivated(self, event):
		self.setSelection(event.Index)

	def OnItemDeselected(self, evt):
		self.setSelection(None)

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)

	def OnGetItemText(self, item, col):
		if item < 0 or item >= len(self.activeTrains):
			return None
		
		tr = self.activeTrains[item]
		if col == 0:
			return tr["tid"]
		elif col == 1:
			return tr["dir"]
		elif col == 2:
			return tr["origin"]
		elif col == 3:
			return tr["terminus"]
		elif col == 4:
			return tr["engineer"]
		elif col == 5:
			return tr["loco"]
		elif col == 6:
			return tr["descr"]

	def OnGetItemAttr(self, item):
		tr = self.activeTrains[item]
		if tr["engineer"] == "ATC":
			if item % 2 == 1:
				return self.attr4
			else:
				return self.attr3
		else:
			if item % 2 == 1:
				return self.attr2
			else:
				return self.attr1
