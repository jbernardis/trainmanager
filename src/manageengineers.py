import wx

class ManageEngineersDlg(wx.Dialog):
	def __init__(self, parent, allEngs, activeEngs):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Manage Engineers")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.parent = parent
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		st1 = wx.StaticText(self, wx.ID_ANY, "All Engineers")
		st2 = wx.StaticText(self, wx.ID_ANY, "Active Engineers")
		sz.Add(st1)
		sz.AddSpacer(125)
		sz.Add(st2)
		
		vsizer.Add(sz)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.availableEngs = sorted([x for x in allEngs if x not in activeEngs])
		self.activeEngs = [x for x in activeEngs]
		
		self.lbAll = wx.ListBox(self, wx.ID_ANY, choices=self.availableEngs, size=(100, 200))
		self.Bind(wx.EVT_LISTBOX, self.onLbAllSelect, self.lbAll)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.bRightPressed, self.lbAll)
		self.lbActive = wx.ListBox(self, wx.ID_ANY, choices=self.activeEngs, size=(100, 200))
		self.Bind(wx.EVT_LISTBOX, self.onLbActiveSelect, self.lbActive)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.bLeftPressed, self.lbActive)
		
		sz.Add(self.lbAll)
		
		sz.AddSpacer(10)
		
		btnsizer = wx.BoxSizer(wx.VERTICAL)
		btnsizer.AddSpacer(20)
		
		self.bRight = wx.Button(self, wx.ID_ANY, "->")
		btnsizer.Add(self.bRight)
		
		btnsizer.AddSpacer(10)
		
		self.bLeft = wx.Button(self, wx.ID_ANY, "<-")
		btnsizer.Add(self.bLeft)
		
		btnsizer.AddSpacer(30)
		
		self.bUp = wx.Button(self, wx.ID_ANY, "up")
		btnsizer.Add(self.bUp)
		
		btnsizer.AddSpacer(10)
		
		self.bDown = wx.Button(self, wx.ID_ANY, "down")
		btnsizer.Add(self.bDown)
		
		btnsizer.AddSpacer(20)
		self.Bind(wx.EVT_BUTTON, self.bRightPressed, self.bRight)
		self.Bind(wx.EVT_BUTTON, self.bLeftPressed, self.bLeft)
		self.Bind(wx.EVT_BUTTON, self.bUpPressed, self.bUp)
		self.Bind(wx.EVT_BUTTON, self.bDownPressed, self.bDown)
		
		sz.Add(btnsizer)
		
		sz.AddSpacer(10)
		
		sz.Add(self.lbActive)
		
		vsizer.Add(sz)
		vsizer.AddSpacer(20)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		
		sz.AddSpacer(20)
		self.bOk = wx.Button(self, wx.ID_ANY, "OK")
		sz.Add(self.bOk)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOk)
		
		sz.AddSpacer(20)
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		sz.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)

		sz.AddSpacer(20)
		vsizer.Add(sz, 1, wx.ALIGN_CENTER_HORIZONTAL)		
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
		
	def onLbAllSelect(self, _):
		sx = self.lbAll.GetSelection()
		self.setAllSelection(sx)
		
	def setAllSelection(self, sx):
		self.bRight.Enable(sx != wx.NOT_FOUND)
		
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
		
	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def getValues(self):
		return self.activeEngs
		
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

