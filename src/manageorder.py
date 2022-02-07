import wx

wildcardTxt = "TXT file (*.txt)|*.txt|"	 \
		   "All files (*.*)|*.*"

BTNSZ = (120, 46)

class ManageOrderDlg(wx.Dialog):
	def __init__(self, parent, order, roster, settings):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.titleString = "Manage Train Order"
		self.settings = settings
		
		self.modified = None

		self.setModified(False)
	
		self.trainOrder = [x for x in order]
		self.trainRoster = roster
		self.allTrains = sorted(self.trainRoster.getTrainList())
		
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		
		self.lbOrder = wx.ListBox(self, wx.ID_ANY, choices=self.trainOrder, size=(120, 300))
		self.lbOrder.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbOrderSelect, self.lbOrder)
		
		hsizer.Add(self.lbOrder)

		hsizer.AddSpacer(20)
		
		btnSizer = wx.BoxSizer(wx.VERTICAL)
		btnSizer.AddSpacer(20)
		
		self.bUp = wx.Button(self, wx.ID_ANY, "Up", size=BTNSZ)
		self.bUp.SetFont(btnFont)
		self.bUp.SetToolTip("Move the selected train up in the order")
		self.Bind(wx.EVT_BUTTON, self.bUpPressed, self.bUp)
		btnSizer.Add(self.bUp)
		self.bUp.Enable(False)
			
		btnSizer.AddSpacer(20)
		
		self.bDown = wx.Button(self, wx.ID_ANY, "Down", size=BTNSZ)
		self.bDown.SetFont(btnFont)
		self.bDown.SetToolTip("Move the selected train down in the order")
		self.Bind(wx.EVT_BUTTON, self.bDownPressed, self.bDown)
		btnSizer.Add(self.bDown)
		self.bDown.Enable(False)
		
		btnSizer.AddSpacer(20)
		
		hsizer.Add(btnSizer)
		hsizer.AddSpacer(40)
		
		
		btnSizer = wx.BoxSizer(wx.VERTICAL)
		btnSizer.AddSpacer(20)
		
		self.bAdd = wx.Button(self, wx.ID_ANY, "Add", size=BTNSZ)
		self.bAdd.SetFont(btnFont)
		self.bAdd.SetToolTip("Add the selected train to the end of the order list")
		self.Bind(wx.EVT_BUTTON, self.bAddPressed, self.bAdd)
		btnSizer.Add(self.bAdd)
		
		btnSizer.AddSpacer(10)
		
		self.chAvail = wx.Choice(self, wx.ID_ANY, choices=[], size=(100, -1))
		self.chAvail.SetFont(textFont)
		btnSizer.Add(self.chAvail)
		
		btnSizer.AddSpacer(20)
		
		self.bDel = wx.Button(self, wx.ID_ANY, "Delete", size=BTNSZ)
		self.bDel.SetFont(btnFont)
		self.bDel.SetToolTip("Delete the currently selected train from the train order")
		self.Bind(wx.EVT_BUTTON, self.bDelPressed, self.bDel)
		btnSizer.Add(self.bDel)
		self.bDel.Enable(False)
		
		btnSizer.AddSpacer(80)

		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNSZ)
		self.bSave.SetFont(btnFont)
		self.bSave.SetToolTip("Save the train order list to a named file")
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		btnSizer.Add(self.bSave)
		
		btnSizer.AddSpacer(10)
		
		hsizer.Add(btnSizer)
		
		hsizer.AddSpacer(20)
		
		hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
		hsizer2.AddSpacer(10)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.bOK.SetToolTip("Exit the dialog box and update the loaded train order.  No file will be saved")
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		hsizer2.Add(self.bOK)
		
		hsizer2.AddSpacer(10)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.bCancel.SetToolTip("Exit the dialog box discarding any pending changes")
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		hsizer2.Add(self.bCancel)

		hsizer2.AddSpacer(10)

		vsizer = wx.BoxSizer(wx.VERTICAL)		
		vsizer.AddSpacer(20)
		vsizer.Add(hsizer)	   
		vsizer.AddSpacer(20)
		vsizer.Add(hsizer2, 0, wx.ALIGN_RIGHT)	   
		vsizer.AddSpacer(20)
		
		self.setArrays()
		self.setModified(False)
		
		self.SetSizer(vsizer)
		self.Layout()
		self.Fit();
		
	def setArrays(self):
		self.availableTrains = [x for x in self.allTrains if x not in self.trainOrder]
		self.bAdd.Enable(len(self.availableTrains) > 0)
		self.chAvail.SetItems(self.availableTrains)
		if len(self.availableTrains) > 0:
			self.chAvail.Enable(True)
			if self.chAvail.GetSelection() == wx.NOT_FOUND:
				self.chAvail.SetSelection(0)
		else:
			self.chAvail.Enable(False)
		
	def setTitle(self):
		title = self.titleString
		
		if self.modified:
			title += ' *'
			
		self.SetTitle(title)
		
	def onLbOrderSelect(self, _):
		self.setButtons()
		
	def setButtons(self):
		ix = self.lbOrder.GetSelection()
		if ix == wx.NOT_FOUND:
			self.bUp.Enable(False)
			self.bDown.Enable(False)
			self.bDel.Enable(False)
			return 
		
		self.bDel.Enable(True)
		self.bUp.Enable(ix != 0)
		self.bDown.Enable(ix != len(self.trainOrder)-1)
		
	def bAddPressed(self, _):
		tx = self.chAvail.GetSelection()
		if tx == wx.NOT_FOUND:
			return
		
		tid = self.availableTrains[tx]
		del(self.availableTrains[tx])
		
		self.trainOrder.append(tid)
		self.lbOrder.SetItems(self.trainOrder)
		self.lbOrder.SetSelection(len(self.trainOrder)-1)
		
		self.setArrays()
		self.setButtons()
		
		self.setModified()
		
	def bDelPressed(self, _):
		ix = self.lbOrder.GetSelection()
		if ix == wx.NOT_FOUND:
			return
		
		del(self.trainOrder[ix])
		if ix >= len(self.trainOrder):
			ix = len(self.trainOrder)-1
			if ix < 0:
				ix = wx.NOT_FOUND
			
		self.lbOrder.SetItems(self.trainOrder)
		self.lbOrder.SetSelection(ix)

		self.setArrays()		
		self.setButtons()
			
		self.setModified()
		
	def bUpPressed(self, _):
		ix = self.lbOrder.GetSelection()
		if ix == wx.NOT_FOUND or ix == 0:
			return
		
		s = self.trainOrder[ix]
		self.trainOrder[ix] = self.trainOrder[ix-1]
		self.trainOrder[ix-1] = s
		
		self.lbOrder.SetItems(self.trainOrder)
		self.lbOrder.SetSelection(ix-1)
		
		self.setButtons()

		self.setModified()
		
	def bDownPressed(self, _):
		ix = self.lbOrder.GetSelection()
		if ix == wx.NOT_FOUND or ix >= len(self.trainOrder)-1:
			return
		
		s = self.trainOrder[ix]
		self.trainOrder[ix] = self.trainOrder[ix+1]
		self.trainOrder[ix+1] = s
		
		self.lbOrder.SetItems(self.trainOrder)
		self.lbOrder.SetSelection(ix+1)
		
		self.setButtons()

		self.setModified()
		
	def setModified(self, flag=True):
		if self.modified == flag:
			return
		
		self.modified = flag
		self.setTitle()
		
	def bSavePressed(self, _):
		dlg = wx.FileDialog(self, message="Save train order list to file", defaultDir=self.settings.orderdir,
			defaultFile="", wildcard=wildcardTxt, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False
		
		path = dlg.GetPath()
		dlg.Destroy()
	
		with open(path, "w") as ofp:
			for ln in self.trainOrder:
				ofp.write("%s\n" % ln)
		
	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def getValues(self):
		return self.trainOrder
	
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Train order has been changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
								'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)

