import wx

import pprint

class AssignLocosDlg(wx.Dialog):
	def __init__(self, parent, trains, order, locos):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.titleString = "Assign Locos"
		self.modified = None
		self.setModified(False)
		
		self.parent = parent
		
		self.trains = trains
		self.order = order
		self.locos = locos
		
		self.selectedTx = None
		
		self.currentLoco = {}
		for tid in order:
			tinfo = trains.getTrain(tid)
			self.currentLoco[tid] = tinfo["loco"]

		self.allLocos = locos.getLocoList()
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		vsizer.AddSpacer(20)
		
		self.currentLocoList = CurrentLocoList(self)
		self.currentLocoList.setData(self.currentLoco, order, locos)
		
		vsizer.Add(self.currentLocoList)

		vsizer.AddSpacer(20)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		
		self.bUnassign = wx.Button(self, wx.ID_ANY, "Unassign")
		self.Bind(wx.EVT_BUTTON, self.onBUnassign, self.bUnassign)
		self.bUnassign.Enable(False)
		hsizer.Add(self.bUnassign)
		
		hsizer.AddSpacer(10)
				
		self.bAssign = wx.Button(self, wx.ID_ANY, "Assign")
		self.Bind(wx.EVT_BUTTON, self.onBAssign, self.bAssign)
		self.bAssign.Enable(False)
		hsizer.Add(self.bAssign)
		
		hsizer.AddSpacer(10)
		self.chAvail = wx.Choice(self, wx.ID_ANY, choices=[])
		self.Bind(wx.EVT_CHOICE, self.onChAvail, self.chAvail)
		hsizer.Add(self.chAvail)
		
		hsizer.AddSpacer(50)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		hsizer.Add(self.bOK)
		hsizer.AddSpacer(20)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		hsizer.Add(self.bCancel)

		vsizer.Add(hsizer);

		vsizer.AddSpacer(20)

		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)	   
		hsizer.AddSpacer(20)
		
		self.determineAvailability()
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit();

	def determineAvailability(self):
		self.locosInUse = [self.currentLoco[x] for x in self.currentLoco.keys() if self.currentLoco[x] is not None]
		self.availLocos = [x for x in self.allLocos if x not in self.locosInUse]
		self.chAvail.SetItems(self.availLocos)
		if len(self.availLocos) == 0:
			self.chAvail.Enable(False)
		else:
			self.chAvail.Enable(True)
			self.chAvail.SetSelection(0)
		
	def reportSelection(self, tx):
		self.selectedTx = tx
		if tx is None:
			self.bUnassign.Enable(False)
			self.bAssign.Enable(False)
		else:
			self.bAssign.Enable(len(self.availLocos) > 0) 
			tid = self.order[tx]
			lId = self.currentLoco[tid]
			self.bUnassign.Enable(lId is not None)
			
	def onBUnassign(self, _):
		if self.selectedTx is None:
			return
		tid = self.order[self.selectedTx]
		self.currentLoco[tid] = None
		self.determineAvailability()
		self.currentLocoList.RefreshItem(self.selectedTx)
		self.bUnassign.Enable(False)
		self.setModified()
		
	def onBAssign(self, _):
		if self.selectedTx is None:
			return
		tid = self.order[self.selectedTx]
		
		lx = self.chAvail.GetSelection()
		if lx == wx.NOT_FOUND:
			return
		
		lid = self.chAvail.GetString(lx)
		self.currentLoco[tid] = lid
		self.determineAvailability()
		self.currentLocoList.RefreshItem(self.selectedTx)
		self.bUnassign.Enable(True)
		self.bAssign.Enable(len(self.availLocos) > 0)
		self.setModified()
		
	def onChAvail(self, _):
		pass
		
	def setModified(self, flag=True):
		if self.modified == flag:
			return
		
		self.modified = flag
		title = self.titleString
		if self.modified:
			title += " *"
			
		self.SetTitle(title)
		
	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def getValues(self):
		return self.currentLoco
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Locomotive assignments have changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
		                               'Changes will be lost',
		                               wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)
		
		
class CurrentLocoList(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(520, 240),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.InsertColumn(0, "Train")
		self.InsertColumn(1, "Loco")
		self.InsertColumn(2, "Description")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 360)

		self.SetItemCount(0)
		self.selected = None

		self.attr1 = wx.ItemAttr()
		self.attr1.SetBackgroundColour(wx.Colour(164, 255, 214)) # light Blue
		self.attr2 = wx.ItemAttr()
		self.attr2.SetBackgroundColour(wx.Colour( 85, 255, 179)) # blue
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)
		
	def setData(self, currentLocos, order, locos):
		self.currentLocos = currentLocos
		self.order = order
		self.locos = locos
		self.SetItemCount(len(self.order))
			
	def getSelection(self):
		if self.selected is None:
			return None
		
		if self.selected < 0 or self.selected >= self.GetItemCount():
			return None
		
		return self.order[self.selected]
			
	def setSelection(self, tx):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			
		self.parent.reportSelection(tx)
		
				
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
		if item < 0 or item >= len(self.order):
			return None
		
		tid = self.order[item]
		lId = self.currentLocos[tid]
		if col == 0:
			return tid
		elif col == 1:
			if lId is None:
				return "<none>"
			else:
				return self.currentLocos[tid]
		elif col == 2:
			if lId is None:
				return ""
			else:
				return self.locos.getLoco(lId)

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return self.attr1
