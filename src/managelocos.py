import wx
import json
import os

wildcard = "JSON file (*.json)|*.json|"	 \
		   "All files (*.*)|*.*"
wildcardTxt = "TXT file (*.txt)|*.txt|"	 \
		   "All files (*.*)|*.*"

BTNSZ = (120, 46)

class ManageLocosDlg(wx.Dialog):
	def __init__(self, parent, locos, settings):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.titleString = "Manage Locomotives"
		self.settings = settings
		
		self.modified = None
		self.selectedLx = None
		self.selectedLoco = None
		self.selectesDesc = None
		self.modifiedLocos = []
		self.deletedLocos = []

		self.setModified(False)
	
		self.locoObj = locos
		self.locoOrder = sorted(self.locoObj.getLocoList())
		self.locos = {}
		for lId in self.locoOrder:
			self.locos[lId] = self.locoObj.getLoco(lId)
			
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		self.locoList = LocoList(self)
		self.locoList.SetFont(textFont)
		self.locoList.setData(self.locos, self.locoOrder)
		self.locoOrder = self.locoList.getLocoOrder()
		vsizer.Add(self.locoList)

		vsizer.AddSpacer(20)
		
		
		self.teDesc = wx.TextCtrl(self, wx.ID_ANY, "", size=(300, -1))
		self.teDesc.SetFont(textFont)
		vsizer.Add(self.teDesc, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsizer.AddSpacer(20)

		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.AddSpacer(10)
		
		self.bAdd = wx.Button(self, wx.ID_ANY, "Add", size=BTNSZ)
		self.bAdd.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bAddPressed, self.bAdd)
		btnSizer.Add(self.bAdd)
		
		btnSizer.AddSpacer(10)
		
		self.bMod = wx.Button(self, wx.ID_ANY, "Modify", size=BTNSZ)
		self.bMod.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bModPressed, self.bMod)
		btnSizer.Add(self.bMod)
		self.bMod.Enable(False)
		
		btnSizer.AddSpacer(10)
		
		self.bDel = wx.Button(self, wx.ID_ANY, "Delete", size=BTNSZ)
		self.bDel.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bDelPressed, self.bDel)
		btnSizer.Add(self.bDel)
		self.bDel.Enable(False)
		
		btnSizer.AddSpacer(10)
		
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsizer.AddSpacer(20)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.AddSpacer(10)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNSZ)
		self.bSave.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		btnSizer.Add(self.bSave)
		
		btnSizer.AddSpacer(20)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		btnSizer.Add(self.bOK)
		
		btnSizer.AddSpacer(10)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		btnSizer.Add(self.bCancel)

		btnSizer.AddSpacer(10)
		
		vsizer.Add(btnSizer, 0, wx.ALIGN_RIGHT)

		vsizer.AddSpacer(20)
		
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)	   
		hsizer.AddSpacer(20)
		
		self.setModified(False)
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit();
		
	def setTitle(self):
		title = self.titleString
		
		if self.modified:
			title += ' *'
			
		self.SetTitle(title)
		
	def bAddPressed(self, _):
		dlg = wx.TextEntryDialog(self, 'Enter Locomotive ID', 'Loco ID', '')
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			locoID = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		if locoID in self.locoOrder:
			dlg = wx.MessageDialog(self, "Loco ID \"%s\" is already in use" % locoID, 
		                               "Duplicate Name",
		                               wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		if locoID not in self.modifiedLocos:
			self.modifiedLocos.append(locoID)
		if locoID in self.deletedLocos:
			self.deletedLocos.remove(locoID)			
		
		self.locoList.add(locoID, self.teDesc.GetValue())
		self.locoOrder = self.locoList.getLocoOrder()
		self.setModified()
		
	def bModPressed(self, _):
		if self.selectedLx is None:
			return
		if self.selectedLoco is None:
			return
		
		if self.selectedLoco not in self.modifiedLocos:
			self.modifiedLocos.append(self.selectedLoco)
				
		self.locoList.modify(self.selectedLx, self.teDesc.GetValue())
		self.locoOrder = self.locoList.getLocoOrder()
		self.setModified()
		
	def bDelPressed(self, _):
		if self.selectedLx is None:
			return
		if self.selectedLoco is None:
			return
		
		if self.selectedLoco not in self.deletedLocos:
			self.deletedLocos.append(self.selectedLoco)	
		if self.selectedLoco in self.modifiedLocos:
			self.modifiedLocos.remove(self.selectedLoco)			
		
		self.locoList.delete(self.selectedLx)
		self.locoOrder = self.locoList.getLocoOrder()
		self.setModified()
		
	def reportSelection(self, lx):
		self.bMod.Enable(lx is not None)
		self.bDel.Enable(lx is not None)
		self.selectedLx = lx
		if lx is None:
			self.selectedLoco = None
			self.selectesDesc = None
			return

		self.selectedLoco = self.locoOrder[lx]
		self.selectedDesc = self.locos[self.selectedLoco]
		self.teDesc.SetValue(self.selectedDesc)
		
	def setModified(self, flag=True):
		if self.modified == flag:
			return
		
		self.modified = flag
		self.setTitle()
		
	def bSavePressed(self, _):
		dlg = wx.FileDialog(self, message="Save Locomotive list to file", defaultDir=self.settings.locodir,
			defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False
		
		path = dlg.GetPath()
		dlg.Destroy()
	
		with open(path, "w") as fp:
			json.dump(self.locos, fp, indent=4, sort_keys=True)
		
	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def getValues(self):
		retval = {}
		for lid in self.modifiedLocos:
			retval[lid] = self.locos[lid]
			
		return retval, self.deletedLocos
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Locomotive list has been changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
		                               'Changes will be lost',
		                               wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)

		
class LocoList(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(440, 240),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.InsertColumn(0, "Loco")
		self.InsertColumn(1, "Description")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 360)

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
		
	def setData(self, locos, locoOrder):
		self.locos = locos
		self.locoOrder = sorted(locoOrder)
		self.SetItemCount(len(self.locoOrder))
			
	def getSelection(self):
		if self.selected is None:
			return None
		
		if self.selected < 0 or self.selected >= self.GetItemCount():
			return None
		
		return self.order[self.selected]
	
	def getLocoOrder(self):
		return self.locoOrder
			
	def setSelection(self, tx):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			
		self.parent.reportSelection(tx)
		
	def add(self, lid, desc):
		lo = sorted(self.locoOrder + [lid])
		self.locoOrder = lo
		self.locos[lid] = desc
		ct = len(self.locoOrder)
		self.SetItemCount(ct)
		self.RefreshItems(0, ct-1)
		
	def delete(self, lx):
		lid = self.locoOrder[lx]		
		del (self.locos[lid])
		del (self.locoOrder[lx])
		
		ct = len(self.locoOrder)
		self.SetItemCount(ct)
		if ct == 0:
			self.setSelection(None)
			return

		first = lx
		last = len(self.locoOrder)-1
		
		if last <= first:
			self.RefreshItem(last)
			self.setSelection(last)
		else:
			self.RefreshItems(first, last)
			self.setSelection(first)
			
	def modify(self, lx, desc):
		loco = self.locoOrder[lx]
		self.locos[loco] = "%s" % desc

		self.RefreshItem(lx)
				
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
		if item < 0 or item >= len(self.locoOrder):
			return None
		
		lid = self.locoOrder[item]
		if col == 0:
			return lid
		elif col == 1:
			return self.locos[lid]

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return self.attr1
