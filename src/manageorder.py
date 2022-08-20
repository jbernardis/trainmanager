import wx

BTNSZ = (120, 46)
wildcardJson = "JSON file (*.json)|*.json|"	 \
		   "All files (*.*)|*.*"

class ManageOrderDlg(wx.Dialog):
	def __init__(self, parent, order, alltrains, settings):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.titleString = "Manage Train Order"
		self.order = order
		self.settings = settings
		
		self.orderTrains = order.getOrder()
		self.extraTrains = order.getExtras()
		self.allTrains = sorted([t for t in alltrains])
		self.availableTrains = [t for t in self.allTrains if t not in self.orderTrains and t not in self.extraTrains]
		
		self.modified = None
		self.everModified = False
		self.setModified(False)

		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		
		self.lbAll = wx.ListBox(self, wx.ID_ANY, choices=self.availableTrains, size=(120, 330))
		self.lbAll.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbAllSelect, self.lbAll)
		
		self.lbSchedule = wx.ListBox(self, wx.ID_ANY, choices=self.orderTrains, size=(120, 150))
		self.lbSchedule.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbScheduleSelect, self.lbSchedule)
			
		self.lbExtra = wx.ListBox(self, wx.ID_ANY, choices=self.extraTrains, size=(120, 150))
		self.lbExtra.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbExtraSelect, self.lbExtra)
		
		self.bRightSch = wx.Button(self, wx.ID_ANY, ">>>")
		self.bRightSch.SetFont(btnFont)
		self.bRightSch.SetToolTip("Move the selected train to the right, from the all/available list to the scheduled list")
		self.Bind(wx.EVT_BUTTON, self.bRightSchPressed, self.bRightSch)
		
		self.bLeftSch = wx.Button(self, wx.ID_ANY, "<<<")
		self.bLeftSch.SetFont(btnFont)
		self.bLeftSch.SetToolTip("Move the selected train to the left, from the scheduled list to the all/available list")
		self.Bind(wx.EVT_BUTTON, self.bLeftSchPressed, self.bLeftSch)
		
		self.bRightExt = wx.Button(self, wx.ID_ANY, ">>>")
		self.bRightExt.SetFont(btnFont)
		self.bRightExt.SetToolTip("Move the selected train to the right, from the all/available list to the extra list")
		self.Bind(wx.EVT_BUTTON, self.bRightExtPressed, self.bRightExt)
		
		self.bLeftExt = wx.Button(self, wx.ID_ANY, "<<<")
		self.bLeftExt.SetFont(btnFont)
		self.bLeftExt.SetToolTip("Move the selected train to the left, from the extra list to the all/available list")
		self.Bind(wx.EVT_BUTTON, self.bLeftExtPressed, self.bLeftExt)
		
		self.bUp = wx.Button(self, wx.ID_ANY, "Up")
		self.bUp.SetFont(btnFont)
		self.bUp.SetToolTip("Move the selected train up to be earlier in the schedule")
		self.Bind(wx.EVT_BUTTON, self.bUpPressed, self.bUp)
		
		self.bDown = wx.Button(self, wx.ID_ANY, "Down")
		self.bDown.SetFont(btnFont)
		self.bDown.SetToolTip("Move the selected train down to be later in the schedule")
		self.Bind(wx.EVT_BUTTON, self.bDownPressed, self.bDown)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		st = wx.StaticText(self, wx.ID_ANY, "Available:")
		st.SetFont(textFont)
		vsz.Add(st)
		vsz.AddSpacer(5)
		vsz.Add(self.lbAll)
		vsz.AddSpacer(10)
		hsizer.Add(vsz)
		
		hsizer.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(60)
		vsz.Add(self.bRightSch)
		vsz.AddSpacer(20)
		vsz.Add(self.bLeftSch)
		vsz.AddSpacer(110)
		vsz.Add(self.bRightExt)
		vsz.AddSpacer(20)
		vsz.Add(self.bLeftExt)
		hsizer.Add(vsz)
		
		hsizer.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		st = wx.StaticText(self, wx.ID_ANY, "Scheduled:")
		st.SetFont(textFont)
		vsz.Add(st)
		vsz.AddSpacer(5)
		vsz.Add(self.lbSchedule)
		
		vsz.AddSpacer(5)
		st = wx.StaticText(self, wx.ID_ANY, "Extra:")
		st.SetFont(textFont)
		vsz.Add(st)
		vsz.AddSpacer(5)
		vsz.Add(self.lbExtra)
		vsz.AddSpacer(10)
		
		hsizer.Add(vsz)
		hsizer.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(60)
		vsz.Add(self.bUp)
		vsz.AddSpacer(20)
		vsz.Add(self.bDown)
		hsizer.Add(vsz)
		
		hsizer.AddSpacer(20)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.AddSpacer(10)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNSZ)
		self.bSave.SetFont(btnFont)
		self.bSave.SetToolTip("Save the train order to the currently loaded file")
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		btnSizer.Add(self.bSave)
		
		btnSizer.AddSpacer(10)
		
		self.bSaveAs = wx.Button(self, wx.ID_ANY, "Save As", size=BTNSZ)
		self.bSaveAs.SetFont(btnFont)
		self.bSaveAs.SetToolTip("Save the train order to a named file")
		self.Bind(wx.EVT_BUTTON, self.bSaveAsPressed, self.bSaveAs)
		btnSizer.Add(self.bSaveAs)
		
		btnSizer.AddSpacer(20)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.bOK.SetToolTip("Exit the dialog box saving any pending changes to the currently loaded file")
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		btnSizer.Add(self.bOK)
		
		btnSizer.AddSpacer(10)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.bCancel.SetToolTip("Exit the dialog box discarding any pending changes (since last save)")
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		btnSizer.Add(self.bCancel)

		btnSizer.AddSpacer(10)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)		
		vsizer.AddSpacer(20)
		vsizer.Add(hsizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		
		self.SetSizer(vsizer)
		self.Layout()
		self.Fit();
		
		self.setButtons()

		
	def setTitle(self):
		title = self.titleString
		
		if self.modified:
			title += ' *'
			
		self.SetTitle(title)
		
	def setModified(self, flag=True):
		if flag:
			self.everModified = True
			
		if self.modified == flag:
			return
		
		self.modified = flag
		self.setTitle()
		
		
	def onLbAllSelect(self, _):
		self.setButtons()
		
	def setButtons(self):
		ix = self.lbAll.GetSelection()
		if ix == wx.NOT_FOUND:
			self.bRightSch.Enable(False)
			self.bRightExt.Enable(False)
		else:
			self.bRightSch.Enable(True)
			self.bRightExt.Enable(True)
			
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND:
			self.bUp.Enable(False)
			self.bDown.Enable(False)
			self.bLeftSch.Enable(False)
		else:
			self.bUp.Enable(ix != 0)
			self.bDown.Enable(ix != len(self.orderTrains)-1)
			self.bLeftSch.Enable(True)
		
		ix = self.lbExtra.GetSelection()
		if ix == wx.NOT_FOUND:
			self.bLeftExt.Enable(False)
		else:
			self.bLeftExt.Enable(True)
		
	def onLbScheduleSelect(self, _):
		self.setButtons()
		
	def onLbExtraSelect(self, _):
		self.setButtons()
		
	def bUpPressed(self, _):
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND or ix == 0:
			return
		
		s = self.orderTrains[ix]
		self.orderTrains[ix] = self.orderTrains[ix-1]
		self.orderTrains[ix-1] = s
		
		self.lbSchedule.SetItems(self.orderTrains)
		self.lbSchedule.SetSelection(ix-1)
		
		self.setButtons()
		self.setModified()
		
	def bDownPressed(self, _):
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND or ix >= len(self.orderTrains)-1:
			return
		
		s = self.orderTrains[ix]
		self.orderTrains[ix] = self.orderTrains[ix+1]
		self.orderTrains[ix+1] = s
		
		self.lbSchedule.SetItems(self.orderTrains)
		self.lbSchedule.SetSelection(ix+1)
		
		self.setButtons()
		self.setModified()
		
	def bRightSchPressed(self, _):
		avx = self.lbAll.GetSelection()
		if avx == wx.NOT_FOUND:
			return
		
		tid = self.availableTrains[avx]
		self.orderTrains.append(tid)
		self.lbSchedule.SetItems(self.orderTrains)
		self.setAvailableTrains()
		if avx >= len(self.availableTrains):
			avx = len(self.availableTrains)-1
		if avx < 0:
			self.lbAll.SetSelection(wx.NOT_FOUND)
		else:
			self.lbAll.SetSelection(avx)

		self.bRightSch.Enable(False)
		self.setModified()
		ix = len(self.orderTrains)-1
		self.lbSchedule.EnsureVisible(ix)
		self.lbSchedule.SetSelection(ix)
		self.setButtons()


	def bLeftSchPressed(self, _):
		ix = self.lbSchedule.GetSelection()
		if ix == wx.NOT_FOUND:
			return

		tid = self.orderTrains[ix]		
		del(self.orderTrains[ix])
		self.lbSchedule.SetItems(self.orderTrains)
		if ix >= len(self.orderTrains):
			ix = len(self.orderTrains)-1
		if ix < 0:
			self.lbSchedule.SetSelection(wx.NOT_FOUND)
		else:
			self.lbSchedule.SetSelection(ix)
		self.setAvailableTrains()
		try:
			ix = self.availableTrains.index(tid)
		except:
			ix = None
			
		self.bLeftSch.Enable(False)
		self.setModified()
		if ix is not None:
			self.lbAll.EnsureVisible(ix)
			self.lbAll.SetSelection(ix)
		self.setButtons()
	
	def bRightExtPressed(self, _):
		avx = self.lbAll.GetSelection()
		if avx == wx.NOT_FOUND:
			return
		
		tid = self.availableTrains[avx]
		self.extraTrains = sorted(self.extraTrains + [tid])
		ix = self.extraTrains.index(tid)
		self.lbExtra.SetItems(self.extraTrains)
		self.setAvailableTrains()
		if avx >= len(self.availableTrains):
			avx = len(self.availableTrains)-1
		if avx < 0:
			self.lbAll.SetSelection(wx.NOT_FOUND)
		else:
			self.lbAll.SetSelection(avx)
		self.bRightExt.Enable(False)
		self.setModified()
		if ix is not None:
			self.lbExtra.EnsureVisible(ix)
			self.lbExtra.SetSelection(ix)
		self.setButtons()

	def bLeftExtPressed(self, _):
		ix = self.lbExtra.GetSelection()
		if ix == wx.NOT_FOUND:
			return
		
		tid = self.extraTrains[ix]		
		del(self.extraTrains[ix])
		self.lbExtra.SetItems(self.extraTrains)
		if ix >= len(self.extraTrains):
			ix = len(self.extraTrains)-1
		if ix < 0:
			self.lbExtra.SetSelection(wx.NOT_FOUND)
		else:
			self.lbExtra.SetSelection(ix)
		self.setAvailableTrains()
		ix = self.availableTrains.index(tid)
		self.bLeftExt.Enable(False)
		self.setModified()
		if ix is not None:
			self.lbAll.EnsureVisible(ix)
			self.lbAll.SetSelection(ix)
		self.setButtons()
		
	def setAvailableTrains(self):
		self.availableTrains = [t for t in self.allTrains if t not in self.orderTrains and t not in self.extraTrains]
		self.lbAll.SetItems(self.availableTrains)

	def bSavePressed(self, _):
		self.doSave()
		
	def bSaveAsPressed(self, _):
		dlg = wx.FileDialog(self, message="Save train order to file", defaultDir=self.settings.orderdir,
			defaultFile="", wildcard=wildcardJson, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return
		
		path = dlg.GetPath()
		dlg.Destroy()

		self.order.saveas(path, self.orderTrains, self.extraTrains)
		self.setModified(False)

	def bOKPressed(self, _):
		if self.modified:
			self.doSave()
			self.EndModal(wx.ID_OK)
		elif self.everModified:
			self.EndModal(wx.ID_OK)
		else:
			self.EndModal(wx.ID_EXIT)
		
	def doSave(self):
		self.order.setNewOrder(self.orderTrains)
		self.order.setNewExtras(self.extraTrains)
		self.order.save()
		self.setModified(False)

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
		
	def getValues(self):
		return self.orderTrains, self.extraTrains

