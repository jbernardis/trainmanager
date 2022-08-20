from configparser import NoSectionError
from re import L
import wx
import os

BTNSZ = (120, 46)

wildcardSch = "SCH file (*.sch)|*.sch|"	 \
			"All files (*.*)|*.*"

BASE_TITLE = "Manage Session Schedules"

class SessionScheduleDlg(wx.Dialog):
	def __init__(self, parent, order, sessionFile, sessionSched):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, BASE_TITLE)
		self.Bind(wx.EVT_CLOSE, self.onClose)

		self.order = order.getOrder()
		self.extra = order.getExtras()
		self.allTrains = [t for t in (self.order + self.extra)]
		self.currentSession = sessionSched

		self.parent = parent
		self.settings = parent.settings

		self.fileName = sessionFile
		self.modified = False

		if len(self.currentSession) == 0:
			self.schedule = [x for x in self.order]
		else:
			self.schedule = [x for x in self.currentSession]
		self.selectedTrain = None

		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)

		self.cbList = {}
		self.chList = {}

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Select extra trains to include:")
		st.SetFont(textFont)
		hsz.Add(st)
		hsz.AddSpacer(20)
		st = wx.StaticText(self, wx.ID_ANY, "And their position in the schedule:")
		st.SetFont(textFont)
		hsz.Add(st)
		vsizer.Add(hsz)
		vsizer.AddSpacer(10)

		self.clb = wx.CheckListBox(self, wx.ID_ANY, choices=self.extra, size=(100, 300))
		self.clb.SetFont(textFontBold)
		self.Bind(wx.EVT_CHECKLISTBOX, self.onCheckExtra, self.clb)

		self.sch = wx.ListBox(self, wx.ID_ANY, choices = self.schedule, size=(100, 300), style=wx.LB_SINGLE)
		self.sch.SetFont(textFontBold)
		self.Bind(wx.EVT_LISTBOX, self.onClickSchedule, self.sch)

		self.bUp = wx.Button(self, wx.ID_ANY, "Up", size=(80, 30))
		self.bUp.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bUpPressed, self.bUp);
		self.bUp.Enable(False)

		self.bDown = wx.Button(self, wx.ID_ANY, "Down", size=(80, 30))
		self.bDown.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bDownPressed, self.bDown);
		self.bDown.Enable(False)

		bsz = wx.BoxSizer(wx.VERTICAL)
		bsz.Add(self.bUp)
		bsz.AddSpacer(20)
		bsz.Add(self.bDown)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(50)
		hsz.Add(self.clb)
		hsz.AddSpacer(80)
		hsz.Add(self.sch)
		hsz.AddSpacer(10)
		hsz.Add(bsz, 0, wx.ALIGN_CENTER_VERTICAL)

		vsizer.Add(hsz)

		vsizer.AddSpacer(20)
		
		self.bLoad = wx.Button(self, wx.ID_ANY, "Load", size=BTNSZ)
		self.bLoad.SetFont(btnFont)
		self.bLoad.SetToolTip("Load a previously saved session schedule from a file")
		self.Bind(wx.EVT_BUTTON, self.bLoadPressed, self.bLoad)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNSZ)
		self.bSave.SetFont(btnFont)
		self.bSave.SetToolTip("Save the current session schedule information to the previously loaded file")
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		
		self.bSaveAs = wx.Button(self, wx.ID_ANY, "Save As", size=BTNSZ)
		self.bSaveAs.SetFont(btnFont)
		self.bSaveAs.SetToolTip("Save the current session schedule information to a different file")
		self.Bind(wx.EVT_BUTTON, self.bSaveAsPressed, self.bSaveAs)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.bOK.SetToolTip("Exit the dialog box, using the currently loaded session schedule")
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		
		self.bRevert = wx.Button(self, wx.ID_ANY, "Revert", size=BTNSZ)
		self.bRevert.SetFont(btnFont)
		self.bRevert.SetToolTip("Exit the dialog box, reverting to the base schedule for the currently loaded order")
		self.Bind(wx.EVT_BUTTON, self.bRevertPressed, self.bRevert)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.bCancel.SetToolTip("Cancel out of the dialog box without activating any session schedule")
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.Add(self.bLoad)
		btnSizer.AddSpacer(30)
		btnSizer.Add(self.bSave)
		btnSizer.AddSpacer(30)
		btnSizer.Add(self.bSaveAs)
		
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(10)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.Add(self.bOK)
		btnSizer.AddSpacer(30)
		btnSizer.Add(self.bRevert)
		btnSizer.AddSpacer(30)
		btnSizer.Add(self.bCancel)
		
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsizer.AddSpacer(20)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit()

		self.fixChecks()
		self.setTitle()

	def setTitle(self):
		ts = BASE_TITLE

		if self.fileName is not None:
			ts += " - %s" % self.fileName

		if self.modified:
			ts += " *"

		self.SetTitle(ts)

	def setModified(self, flag=True):
		if self.modified == flag:
			return

		self.modified = flag
		self.setTitle()

	def setFileName(self, nfn):
		self.fileName = nfn
		self.setTitle()

	def onCheckExtra(self, evt):
		tx = evt.GetSelection()
		self.setModified()
		train = self.extra[tx]
		if self.clb.IsChecked(tx):
			self.schedule.append(train)
		else:
			self.schedule.remove(train)
		
		self.sch.SetItems(self.schedule)

	def onClickSchedule(self, evt):
		self.selectedTrain = evt.GetString()
		if self.selectedTrain in self.order:
			self.bUp.Enable(False)
			self.bDown.Enable(False)
		else:
			try:
				ix = self.schedule.index(self.selectedTrain)
			except:
				ix = None
			if ix is None:
				self.bUp.Enable(False)
				self.bDown.Enable(False)
			elif ix <= 0:
				self.bUp.Enable(False)
				self.bDown.Enable(True)
			elif ix >= (len(self.schedule)-1):
				self.bUp.Enable(True)
				self.bDown.Enable(False)
			else:
				self.bUp.Enable(True)
				self.bDown.Enable(True)

	def bUpPressed(self, evt):
		try:
			ix = self.schedule.index(self.selectedTrain)
		except:
			return

		e1 = self.schedule[ix-1]
		e2 = self.schedule[ix]

		if ix == 1:
			nl = [e2, e1] + self.schedule[2:]
		elif ix == len(self.schedule)-1:
			nl = self.schedule[:-2] + [e2, e1]
		else:
			nl = self.schedule[:ix-1] + [e2, e1] +  self.schedule[ix+1:]

		self.schedule = [x for x in nl]
		self.sch.SetItems(self.schedule)
		self.sch.SetSelection(ix-1)
		self.setModified()

		if ix-1 == 0:
			self.bUp.Enable(False)
		self.bDown.Enable(True)

	def bDownPressed(self, evt):
		try:
			ix = self.schedule.index(self.selectedTrain)
		except:
			return

		e1 = self.schedule[ix]
		e2 = self.schedule[ix+1]
		
		if ix == 0:
			nl = [e2, e1] + self.schedule[2:]
		elif ix == len(self.schedule)-2:
			nl = self.schedule[:-2] + [e2, e1]
		else:
			nl = self.schedule[:ix] + [e2, e1] +  self.schedule[ix+2:]
			
		self.schedule = [x for x in nl]
		self.sch.SetItems(self.schedule)
		self.sch.SetSelection(ix+1)
		if ix+1 >= len(self.schedule)-1:
			self.bDown.Enable(False)
		self.bUp.Enable(True)
		self.setModified()

	def bLoadPressed(self, _):
		if self.modified:
			dlg = wx.MessageDialog(self, 'The current schedule has changed.\nPress "OK" to continue and lose changes, or\n"Cancel" to go back and save.',
					'Pending Changes will be lost',
					wx.OK  | wx.CANCEL | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc == wx.ID_CANCE:
				return

		dlg = wx.FileDialog(
			self, message="Choose a session schedule file",
			defaultDir=self.settings.scheduledir,
			defaultFile="",
			wildcard=wildcardSch,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return 

		path = dlg.GetPath()
		dlg.Destroy()
		try:
			with open(path, "r") as x:
				sch = [t.strip() for t in x.readlines()]
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, 'Unable to open Session Schedule file %s' % path,
					'File Not Found',
					wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			self.schedule = []
			return

		self.setFileName(os.path.basename(path))
		self.setModified(False)

		self.schedule = [t for t in sch if t in self.allTrains]
		invalidTrains = [t for t in sch if t not in self.allTrains]
		if len(invalidTrains) != 0:
			dlg = wx.MessageDialog(self, "The following train(s) from the schedule\ndo not exist in the current roster:\n\n%s\n\nThey have been removed." % ", ".join(invalidTrains),
							'Invalid Trains in Schedule', wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()

			self.setModified(True)

		self.sch.SetItems(self.schedule)
		self.fixChecks()

	def fixChecks(self):
		ex = [t for t in self.schedule if t in self.extra]
		ct = self.clb.GetCount()
		for i in range(ct):
			self.clb.Check(i, self.clb.GetString(i) in ex)

	def bSavePressed(self, evt):
		self.doSave()

	def doSave(self):
		if self.fileName is None:
			self.doSaveAs()
		else:
			self.saveToFile(os.path.join(self.settings.scheduledir, self.fileName))

	def bSaveAsPressed(self, _):
		if not os.path.exists(self.settings.scheduledir):
			os.mkdir(self.settings.scheduledir)

		self.doSaveAs()

	def doSaveAs(self):
		dlg = wx.FileDialog(self, message="Save session schedule to file", defaultDir=self.settings.scheduledir,
			defaultFile="", wildcard=wildcardSch, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False
		
		path = dlg.GetPath()
		dlg.Destroy()

		if not path.lower().endswith(".sch"):
			path += ".sch"
		self.saveToFile(path)
		self.setFileName(os.path.basename(path))
		return True

	def saveToFile(self, fn):
		with open(fn, "w") as ofp:
			for t in self.schedule:
				ofp.write(t + "\n")

		self.setModified(False)

	def bOKPressed(self, _):
		ct = len(self.clb.GetCheckedItems())
		if self.modified and ct != 0: 
			if not self.doSaveAs():
				return
		if ct == 0:
			self.fileName = None
			
		self.EndModal(wx.ID_OK)

	def bRevertPressed(self, _):
		if self.modified:
			dlg = wx.MessageDialog(self, 'The current schedule has changed.\nPress "OK" to continue and lose changes, or\n"Cancel" to go back and save.',
					'Pending Changes will be lost',
					wx.OK  | wx.CANCEL | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc == wx.ID_CANCEL:
				return
		self.fileName = None
		self.schedule = self.order
		self.EndModal(wx.ID_OK)
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'The current schedule has changed.\nPress "OK" to continue and lose changes, or\n"Cancel" to go back and save.',
					'Pending Changes will be lost',
					wx.OK  | wx.CANCEL | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc == wx.ID_CANCEL:
				return
		self.EndModal(wx.ID_CANCEL)

	def getResults(self):
		return self.fileName, self.schedule
		