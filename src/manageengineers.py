import wx

wildcardTxt = "TXT file (*.txt)|*.txt|"	 \
		   "All files (*.*)|*.*"

BTNSZ = (120, 46)

class ManageEngineersDlg(wx.Dialog):
	def __init__(self, parent, allEngs, actEngs, busyEngs, settings):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Manage Engineers")
		self.Bind(wx.EVT_CLOSE, self.onClose)
	
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		
		self.busyEngs = busyEngs
		
		self.parent = parent
		self.settings = settings
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		st1 = wx.StaticText(self, wx.ID_ANY, "All Engineers")
		st1.SetFont(textFontBold)
		st2 = wx.StaticText(self, wx.ID_ANY, "Active Engineers")
		st2.SetFont(textFontBold)
		sz.Add(st1)
		sz.AddSpacer(210)
		sz.Add(st2)
		
		vsizer.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.allEngs = [x for x in allEngs]
		self.activeEngs = [x for x in actEngs]
		self.updateArrays()
		
		self.lbAll = wx.ListBox(self, wx.ID_ANY, choices=self.availableEngs, size=(160, 200))
		self.lbAll.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbAllSelect, self.lbAll)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.bRightPressed, self.lbAll)
		self.lbActive = wx.ListBox(self, wx.ID_ANY, choices=self.activeEngs, size=(160, 200))
		self.lbActive.SetFont(textFont)
		self.Bind(wx.EVT_LISTBOX, self.onLbActiveSelect, self.lbActive)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.bLeftPressed, self.lbActive)
		
		sz.Add(self.lbAll)
		
		sz.AddSpacer(40)
		
		btnsizer = wx.BoxSizer(wx.VERTICAL)
		btnsizer.AddSpacer(20)
		
		self.bRight = wx.Button(self, wx.ID_ANY, ">>>")
		self.bRight.SetFont(btnFont)
		self.bRight.SetToolTip("Move the selected engineer to the right, from the all/available list to the active list")
		btnsizer.Add(self.bRight)
		
		btnsizer.AddSpacer(10)
		
		self.bLeft = wx.Button(self, wx.ID_ANY, "<<<")
		self.bLeft.SetFont(btnFont)
		self.bLeft.SetToolTip("Move the selected engineer to the left, from the active list to the all/available list")
		btnsizer.Add(self.bLeft)
		
		btnsizer.AddSpacer(30)
		
		self.bUp = wx.Button(self, wx.ID_ANY, "up")
		self.bUp.SetFont(btnFont)
		self.bUp.SetToolTip("Move the selected engineer up in the active list")
		btnsizer.Add(self.bUp)
		
		btnsizer.AddSpacer(10)
		
		self.bDown = wx.Button(self, wx.ID_ANY, "down")
		self.bDown.SetFont(btnFont)
		self.bDown.SetToolTip("Move the selected engineer down in the active list")
		btnsizer.Add(self.bDown)
		
		btnsizer.AddSpacer(20)
		self.Bind(wx.EVT_BUTTON, self.bRightPressed, self.bRight)
		self.Bind(wx.EVT_BUTTON, self.bLeftPressed, self.bLeft)
		self.Bind(wx.EVT_BUTTON, self.bUpPressed, self.bUp)
		self.Bind(wx.EVT_BUTTON, self.bDownPressed, self.bDown)
		
		sz.Add(btnsizer)
		
		sz.AddSpacer(40)
		
		sz.Add(self.lbActive)
		
		vsizer.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		vsizer.AddSpacer(20)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		self.bAddEng = wx.Button(self, wx.ID_ANY, "Add\nEngineer", size=BTNSZ)
		self.bAddEng.SetFont(btnFont)
		self.bAddEng.SetToolTip("Add a new engineer to the all/available list")
		sz.Add(self.bAddEng)
		self.Bind(wx.EVT_BUTTON, self.bAddEngPressed, self.bAddEng)
		
		sz.AddSpacer(20)
		self.bDelEng = wx.Button(self, wx.ID_ANY, "Delete\nEngineer", size=BTNSZ)
		self.bDelEng.SetFont(btnFont)
		self.bDelEng.SetToolTip("Delete the selected engineer from the all/available list")
		sz.Add(self.bDelEng)
		self.Bind(wx.EVT_BUTTON, self.bDelEngPressed, self.bDelEng)
		self.bDelEng.Enable(False)
		
		sz.AddSpacer(20)
		self.bSaveAll = wx.Button(self, wx.ID_ANY, "Save\nAll As", size=BTNSZ)
		self.bSaveAll.SetFont(btnFont)
		self.bSaveAll.SetToolTip("Save the full list of ALL engineers, including active engineers, to a named file")
		sz.Add(self.bSaveAll)
		self.Bind(wx.EVT_BUTTON, self.bSaveAllPressed, self.bSaveAll)
		
		sz.AddSpacer(20)
		self.bSaveAct = wx.Button(self, wx.ID_ANY, "Save\nActive As", size=BTNSZ)
		self.bSaveAct.SetFont(btnFont)
		self.bSaveAct.SetToolTip("Save the list of active engineers to a named file")
		sz.Add(self.bSaveAct)
		self.Bind(wx.EVT_BUTTON, self.bSaveActPressed, self.bSaveAct)

		sz.AddSpacer(20)
		
		vsizer.Add(sz)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		
		sz.AddSpacer(20)
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.bOK.SetToolTip("Exit the dialog box and replace the loaded engineer list with the above active list")
		sz.Add(self.bOK)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		
		sz.AddSpacer(20)
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.bCancel.SetToolTip("Exit the dialog box discarding any pending changes")
		sz.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)

		sz.AddSpacer(20)
		
		vsizer.AddSpacer(20)
		vsizer.Add(sz, 1, wx.ALIGN_RIGHT)		
		vsizer.AddSpacer(20)
		
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)	   
		hsizer.AddSpacer(20)
		
		self.bRight.Enable(False)
		self.bLeft.Enable(False)
		self.bUp.Enable(False)
		self.bDown.Enable(False)
		
		self.setModified(False)
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit();
		
	def setModified(self, flag=True):
		self.modified = flag

	def updateArrays(self):
		self.availableEngs = sorted([x for x in self.allEngs if x not in self.activeEngs])
		
	def onLbAllSelect(self, _):
		sx = self.lbAll.GetSelection()
		self.setAllSelection(sx)
		
	def setAllSelection(self, sx):
		self.bRight.Enable(sx != wx.NOT_FOUND)
		self.bDelEng.Enable(sx != wx.NOT_FOUND)
		
	def onLbActiveSelect(self, _):
		sx = self.lbActive.GetSelection()
		self.setActiveSelection(sx)
		
	def setActiveSelection(self, sx):
		if sx == wx.NOT_FOUND:
			self.bLeft.Enable(False)
			self.bUp.Enable(False)
			self.bDown.Enable(False)
		else:
			self.bLeft.Enable(True)
			if len(self.activeEngs) == 1:
				self.bDown.Enable(False)
				self.bUp.Enable(False)
			elif sx == 0:
				self.bDown.Enable(True)
				self.bUp.Enable(False)
			elif sx == len(self.activeEngs)-1:
				self.bDown.Enable(False)
				self.bUp.Enable(True)
			else:
				self.bDown.Enable(True)
				self.bUp.Enable(True)

		
	def bRightPressed(self, _):
		sx = self.lbAll.GetSelection()
		if sx == wx.NOT_FOUND:
			return
		
		self.setModified()
		
		eng = self.lbAll.GetString(sx)
		self.availableEngs.remove(eng)
		self.activeEngs.append(eng)
		
		self.lbAll.SetItems(self.availableEngs)
		self.lbActive.SetItems(self.activeEngs)
		
		self.setActiveSelection(wx.NOT_FOUND)
		self.setAllSelection(wx.NOT_FOUND)
		
	def bLeftPressed(self, _):
		sx = self.lbActive.GetSelection()
		if sx == wx.NOT_FOUND:
			return
		
		self.setModified()
		
		eng = self.lbActive.GetString(sx)
		self.activeEngs.remove(eng)
		newAvl = self.availableEngs + [eng]
		self.availableEngs = sorted(newAvl)
		
		self.lbAll.SetItems(self.availableEngs)
		self.lbActive.SetItems(self.activeEngs)
		
		self.setActiveSelection(wx.NOT_FOUND)
		self.setAllSelection(wx.NOT_FOUND)
		
	def bUpPressed(self, _):
		sx = self.lbActive.GetSelection()
		if sx == wx.NOT_FOUND or sx == 0:
			return
		
		e1 = self.activeEngs[sx-1]
		e2 = self.activeEngs[sx]

		if sx == 1:
			nl = [e2, e1] + self.activeEngs[2:]
		elif sx == len(self.activeEngs)-1:
			nl = self.activeEngs[:-2] + [e2, e1]
		else:
			nl = self.activeEngs[:sx-1] + [e2, e1] +  self.activeEngs[sx+1:]
			
		self.activeEngs = nl
		self.lbActive.SetItems(self.activeEngs)
		self.lbActive.SetSelection(sx-1)
		
		self.setActiveSelection(sx-1)
		self.setModified()
		
	def bDownPressed(self, _):
		sx = self.lbActive.GetSelection()
		if sx == wx.NOT_FOUND or sx == len(self.activeEngs)-1:
			return
		
		e1 = self.activeEngs[sx]
		e2 = self.activeEngs[sx+1]
		
		if sx == 0:
			nl = [e2, e1] + self.activeEngs[2:]
		elif sx == len(self.activeEngs)-2:
			nl = self.activeEngs[:-2] + [e2, e1]
		else:
			nl = self.activeEngs[:sx] + [e2, e1] +  self.activeEngs[sx+2:]
			
		self.activeEngs = nl
		self.lbActive.SetItems(self.activeEngs)
		self.lbActive.SetSelection(sx+1)
		
		self.setActiveSelection(sx+1)
		self.setModified()
		
	def bAddEngPressed(self, _):
		dlg = wx.TextEntryDialog(
				self, 'Enter Name of new engineer',
				'Add Engineer', '')

		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			eng = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		if eng in self.allEngs or eng in self.busyEngs:
			dlg = wx.MessageDialog(self, "Engineer \"%s\" is already in the list" % eng, 
		                               "Duplicate Name",
		                               wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		newAvl = self.availableEngs + [eng]
		self.availableEngs = sorted(newAvl)
		self.allEngs.append(eng)
		
		self.lbAll.SetItems(self.availableEngs)
		ix = self.availableEngs.index(eng)

		self.lbAll.SetSelection(ix)		
		
	def bDelEngPressed(self, _):
		sx = self.lbAll.GetSelection()
		if sx == wx.NOT_FOUND or sx == len(self.activeEngs)-1:
			return
		
		eng = self.lbAll.GetString(sx)
		self.lbAll.Delete(sx)
		self.allEngs.remove(eng)
		self.availableEngs.remove(eng)
		sx = self.lbAll.GetSelection()
		self.setAllSelection(sx)
		self.setModified()
		
	def bSaveAllPressed(self, _):
		self.saveEngineers(sorted(self.allEngs), "ALL engineers")
		
	def bSaveActPressed(self, _):
		self.saveEngineers(self.activeEngs, "Active engineers")
		
	def saveEngineers(self, engList, label):
		dlg = wx.FileDialog(self, message="Save %s list to file" % label, defaultDir=self.settings.engineerdir,
			defaultFile="", wildcard=wildcardTxt, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False
		
		path = dlg.GetPath()
		dlg.Destroy()
	
		with open(path, "w") as ofp:
			for ln in engList:
				ofp.write("%s\n" % ln)
		
	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def getValues(self):
		return self.activeEngs, self.allEngs+self.busyEngs
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Engineer list has been changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
		                               'Changes will be lost',
		                               wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)
