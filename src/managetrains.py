import wx
import os
import json

wildcardTxt = "TXT file (*.txt)|*.txt|"	 \
		   "All files (*.*)|*.*"
wildcard = "JSON file (*.json)|*.json|"	 \
		   "All files (*.*)|*.*"

BTNSZ = (120, 46)
BTNSZSMALL = (80, 30)

class ManageTrainsDlg(wx.Dialog):
	def __init__(self, parent, roster, locos, settings):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.titleString = "Manage Trains"
		self.settings = settings
		
		self.modified = None
		self.everModified = False
		
		self.selectedTid = None
		self.selectedStep = None
	
		self.trains = roster
		self.locos = locos
		
		self.trainList = [t for t in self.trains]
		
		self.roster = {}
		for t in self.trainList:
			ti = self.trains.getTrain(t)
			info = {"dir": ti["dir"],
				"loco": ti["loco"],
				"desc": ti["desc"],
				"block": ti["block"],
				}
			
			steps = [[s[0], s[1], s[2]] for s in ti["steps"]]
			info["steps"] = steps
			
			self.roster[t] = info
		
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		labelFontBold = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)		
		st = wx.StaticText(self, wx.ID_ANY, "Train:")
		st.SetFont(textFontBold)
		hsz.Add(st, 0, wx.TOP, 5)
		hsz.AddSpacer(5)
		self.cbTrains = wx.ComboBox(self, wx.ID_ANY, choices=self.trainList)
		self.cbTrains.SetFont(textFont)
		self.Bind(wx.EVT_COMBOBOX, self.onChTrains, self.cbTrains)
		hsz.Add(self.cbTrains)
		
		hsizer.Add(hsz)
		
		sz = wx.BoxSizer(wx.VERTICAL)
		
		self.stDirection = wx.StaticText(self, wx.ID_ANY, "", size=(200, -1))
		self.stDirection.SetFont(textFontBold)
		self.stDescription = wx.StaticText(self, wx.ID_ANY, "", size=(200, -1))
		self.stDescription.SetFont(textFontBold)
		
		sz.AddSpacer(5)
		sz.Add(self.stDirection)
		sz.AddSpacer(10)
		sz.Add(self.stDescription)
		sz.AddSpacer(50)
		
		boxModify = wx.StaticBox(self, wx.ID_ANY, "Modify")
		boxModify.SetFont(labelFontBold)
		topBorder = boxModify.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder+5)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(boxModify, wx.ID_ANY, "Eastbound:", size=(120, -1))
		st.SetFont(textFont)
		hsz.Add(st)
		hsz.AddSpacer(5)
		self.cbEast = wx.CheckBox(boxModify, wx.ID_ANY, "", style=wx.ALIGN_RIGHT)
		self.cbEast.SetFont(textFont)
		hsz.Add(self.cbEast)
		
		bsizer.Add(hsz)
		bsizer.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(boxModify, wx.ID_ANY, "Description:", size=(120, -1))
		st.SetFont(textFont)
		hsz.Add(st, 0, wx.TOP, 5)
		hsz.AddSpacer(5)
		self.teDesc = wx.TextCtrl(boxModify, wx.ID_ANY, "", size=(200, -1))
		self.teDesc.SetFont(textFont)
		hsz.Add(self.teDesc)
		
		bsizer.Add(hsz)
		bsizer.AddSpacer(20)
		
		self.bMod = wx.Button(boxModify, wx.ID_ANY, "Apply", size=BTNSZ)
		self.bMod.SetFont(btnFont)
		self.bMod.SetToolTip("Update the currently selected train with the above direction/description/loco number")
		self.Bind(wx.EVT_BUTTON, self.bModPressed, self.bMod)
		bsizer.Add(self.bMod, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.bMod.Enable(False)
		
		bsizer.AddSpacer(10)

		bhsizer = wx.BoxSizer(wx.HORIZONTAL)
		bhsizer.AddSpacer(20)
		bhsizer.Add(bsizer)
		bhsizer.AddSpacer(20)
		boxModify.SetSizer(bhsizer)

		sz.Add(boxModify)

		hsizer.AddSpacer(10)		
		hsizer.Add(sz)

		hsizer.AddSpacer(20)
		
		sz = wx.BoxSizer(wx.VERTICAL)
				
		self.lcSteps = StepsList(self)
		self.lcSteps.SetFont(textFont)
		sz.Add(self.lcSteps)
		sz.AddSpacer(10)
		
		self.teTower = wx.TextCtrl(self, wx.ID_ANY, "", size=(100, -1))
		self.teTower.SetFont(textFont)
		
		self.teLoc = wx.TextCtrl(self, wx.ID_ANY, "", size=(40, -1))
		self.teLoc.SetFont(textFont)
		
		self.teStop = wx.TextCtrl(self, wx.ID_ANY, "", size=(240, -1))
		self.teStop.SetFont(textFont)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Tower: ")
		st.SetFont(textFontBold)
		hsz.Add(st, 0, wx.TOP, 5)
		hsz.AddSpacer(5)
		hsz.Add(self.teTower)
		
		hsz.AddSpacer(5)
		
		st = wx.StaticText(self, wx.ID_ANY, "Loc: ")
		st.SetFont(textFontBold)
		hsz.Add(st, 0, wx.TOP, 5)
		hsz.AddSpacer(5)
		hsz.Add(self.teLoc)
		
		hsz.AddSpacer(5)
		
		st = wx.StaticText(self, wx.ID_ANY, "Stop: ")
		st.SetFont(textFontBold)
		hsz.Add(st, 0, wx.TOP, 5)
		hsz.AddSpacer(5)
		hsz.Add(self.teStop)
		
		sz.Add(hsz)
		sz.AddSpacer(10)
		
		stepBtnSz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bAddStep = wx.Button(self, wx.ID_ANY, "Add\nStep", size=BTNSZ)
		self.bAddStep.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bAddStepPressed, self.bAddStep)
		stepBtnSz.Add(self.bAddStep)
		stepBtnSz.AddSpacer(20)
		
		self.bModStep = wx.Button(self, wx.ID_ANY, "Modify\nStep", size=BTNSZ)
		self.bModStep.SetFont(btnFont)
		self.bModStep.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.bModStepPressed, self.bModStep)
		stepBtnSz.Add(self.bModStep)
		stepBtnSz.AddSpacer(20)
		
		self.bDelStep = wx.Button(self, wx.ID_ANY, "Delete\nStep", size=BTNSZ)
		self.bDelStep.SetFont(btnFont)
		self.bDelStep.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.bDelStepPressed, self.bDelStep)
		stepBtnSz.Add(self.bDelStep)
		
		sz.Add(stepBtnSz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		sz.AddSpacer(10)
		
		hsizer.Add(sz)
		
		hsizer.AddSpacer(10)
		
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(40)
		
		self.bUp = wx.Button(self, wx.ID_ANY, "Up", size=BTNSZSMALL)
		self.bUp.SetFont(btnFont)
		self.bUp.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.bUpPressed, self.bUp)
		
		sz.Add(self.bUp)
		
		sz.AddSpacer(80)
		
		self.bDown = wx.Button(self, wx.ID_ANY, "Down", size=BTNSZSMALL)
		self.bDown.SetFont(btnFont)
		self.bDown.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.bDownPressed, self.bDown)
		
		sz.Add(self.bDown)
		
		hsizer.Add(sz)
		
		hsizer.AddSpacer(20)	
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bAdd = wx.Button(self, wx.ID_ANY, "Add\nTrain", size=BTNSZ)
		self.bAdd.SetFont(btnFont)
		self.bAdd.SetToolTip("Add a new train to the list")
		self.Bind(wx.EVT_BUTTON, self.bAddPressed, self.bAdd)
		btnSizer.Add(self.bAdd)
		
		btnSizer.AddSpacer(10)
		
		self.bModID = wx.Button(self, wx.ID_ANY, "Change\nTrain ID", size=BTNSZ)
		self.bModID.SetFont(btnFont)
		self.bModID.SetToolTip("Change the ID of the currently selected train")
		self.Bind(wx.EVT_BUTTON, self.bModIDPressed, self.bModID)
		btnSizer.Add(self.bModID)
		self.bModID.Enable(False)
		
		btnSizer.AddSpacer(10)
		
		self.bCopy = wx.Button(self, wx.ID_ANY, "Copy\nTrain", size=BTNSZ)
		self.bCopy.SetFont(btnFont)
		self.bCopy.SetToolTip("Copy the currently selected train to a new train")
		self.Bind(wx.EVT_BUTTON, self.bCopyPressed, self.bCopy)
		btnSizer.Add(self.bCopy)
		self.bCopy.Enable(False)
		
		btnSizer.AddSpacer(10)
		
		self.bDel = wx.Button(self, wx.ID_ANY, "Delete\nTrain", size=BTNSZ)
		self.bDel.SetFont(btnFont)
		self.bDel.SetToolTip("Delete the currently selected train from the list")
		self.Bind(wx.EVT_BUTTON, self.bDelPressed, self.bDel)
		btnSizer.Add(self.bDel)
		self.bDel.Enable(False)
		
		btnSizer.AddSpacer(50)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNSZ)
		self.bSave.SetFont(btnFont)
		self.bSave.SetToolTip("Save the train list to the currently loaded file")
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		btnSizer.Add(self.bSave)
		
		btnSizer.AddSpacer(10)
		
		self.bSaveAs = wx.Button(self, wx.ID_ANY, "Save As", size=BTNSZ)
		self.bSaveAs.SetFont(btnFont)
		self.bSaveAs.SetToolTip("Save the train list to a named file")
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

		vsizer = wx.BoxSizer(wx.VERTICAL)		
		vsizer.AddSpacer(20)
		vsizer.Add(hsizer)	   
		vsizer.AddSpacer(20)
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)	   
		vsizer.AddSpacer(20)
		
		self.setModified(False)
		
		self.SetSizer(vsizer)
		self.Layout()
		self.Fit();
		
		if len(self.trainList) > 0:
			self.cbTrains.SetSelection(0)
			self.setSelectedTrain(self.trainList[0])
		
	def onChTrains(self, _):
		tx = self.cbTrains.GetSelection()
		if tx == wx.NOT_FOUND:
			self.selectedTid = None
			return
		
		self.setSelectedTrain(self.trainList[tx])
		
	def reportSelection(self, tx):
		self.selectedStep = tx
		if tx is None:
			self.teTower.SetValue("")
			self.teStop.SetValue("")
			self.bUp.Enable(False)
			self.bDown.Enable(False)
			self.bModStep.Enable(False)
			self.bDelStep.Enable(False)
			return
		
		self.bModStep.Enable(True)
		self.bDelStep.Enable(True)
		self.bUp.Enable(tx > 0)
		self.bDown.Enable(tx < len(self.selectedTrainInfo["steps"])-1)
		
		self.teTower.SetValue(self.selectedTrainInfo["steps"][tx][0])
		vloc = self.selectedTrainInfo["steps"][tx][2]
		if vloc == 0:
			loc = ""
		else:
			loc = "%d" % vloc
		self.teLoc.SetValue(loc)
		self.teStop.SetValue(self.selectedTrainInfo["steps"][tx][1])
		
	def bAddPressed(self, _):
		dlg = wx.TextEntryDialog(self, 'Enter New Train Number/Name', 'Train ID', '')
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			trainID = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		if trainID in self.trainList:
			dlg = wx.MessageDialog(self, "A train with the ID/Name \"%s\" already exists" % trainID, 
		                               "Duplicate Name",
		                               wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		self.trainList = sorted(self.trainList + [trainID])
		self.roster[trainID] = {
			'dir': "East" if self.cbEast.IsChecked() else "West",
			'desc': self.teDesc.GetValue(),
			'loco': None,
			'steps': [],
			'block': None
			}
		
		self.cbTrains.SetItems(self.trainList)
		self.cbTrains.SetSelection(self.trainList.index(trainID))
		self.setSelectedTrain(trainID)
		self.setModified()
		
	def bCopyPressed(self, _):
		if self.selectedTid is None:
			return
		if self.selectedTrainInfo is None:
			return
		
		dlg = wx.TextEntryDialog(self, 'Enter New Train Number/Name', 'Train ID', '')
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			trainID = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		if trainID in self.trainList:
			dlg = wx.MessageDialog(self, "A train with the ID/Name \"%s\" already exists" % trainID, 
		                               "Duplicate Name",
		                               wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return

		steps = []
		for s in self.selectedTrainInfo["steps"]:
			step = [st for st in s]
			steps.append(step)
					
		self.trainList = sorted(self.trainList + [trainID])
		self.roster[trainID] = {
			'dir': "East" if self.cbEast.IsChecked() else "West",
			'desc': self.teDesc.GetValue(),
			'loco': None,
			'steps': steps,
			'block': None
			}
		
		self.cbTrains.SetItems(self.trainList)
		self.cbTrains.SetSelection(self.trainList.index(trainID))
		self.setSelectedTrain(trainID)
		self.setModified()
		
	def bModPressed(self, _):
		if self.selectedTid is None:
			return
		if self.selectedTrainInfo is None:
			return
		
		self.selectedTrainInfo["dir"] = "East" if self.cbEast.IsChecked() else "West"
		self.stDirection.SetLabel("%sbound" % self.selectedTrainInfo["dir"])
		
		self.selectedTrainInfo["desc"] = self.teDesc.GetValue()
		self.stDescription.SetLabel(self.selectedTrainInfo["desc"])

		self.setSelectedTrain(self.selectedTid)
		self.setModified()
		
	def bModIDPressed(self, _):
		if self.selectedTid is None:
			return
		if self.selectedTrainInfo is None:
			return

		oldID = self.selectedTid
		newID = None
		while newID is None:
			dlg = wx.TextEntryDialog(self, "Enter New Train Number/Name for train %s" % oldID, 'Train ID', '')
			rc = dlg.ShowModal()
			if rc == wx.ID_OK:
				newID = dlg.GetValue()
	
			dlg.Destroy()
			
			if rc != wx.ID_OK:
				return
			
			if newID in self.trainList:
				dlg = wx.MessageDialog(self, "A train with the ID/Name \"%s\" already exists" % newID, 
			                               "Duplicate Name",
			                               wx.OK | wx.ICON_WARNING)
				dlg.ShowModal()
				dlg.Destroy()
				newID = None
				
		t = self.roster[oldID]
		self.roster[newID] = t

		tx = self.trainList.index(oldID)
		del(self.trainList[tx])
		del(self.roster[oldID])

		self.trainList = sorted(self.trainList + [newID])
		self.cbTrains.SetItems(self.trainList)
		self.cbTrains.SetSelection(self.trainList.index(newID))
		self.setSelectedTrain(newID)
		self.setModified()
		
	def bDelPressed(self, _):
		if self.selectedTid is None:
			return
		if self.selectedTrainInfo is None:
			return
		
		dlg = wx.MessageDialog(self, "This will delete train %s from the roster.\n\nAre you sure?\n\nYes to Delete, No to Cancel" % self.selectedTid, 
	                               "Confirm Delete",
	                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		
		dlg.Destroy()
		if rc != wx.ID_YES:
			return
		
		tx = self.trainList.index(self.selectedTid)
		del(self.trainList[tx])
		del(self.roster[self.selectedTid])
		
		self.cbTrains.SetItems(self.trainList)
		
		if tx >= len(self.trainList):
			tx = len(self.trainList)-1
			
		if tx < 0:
			self.setSelectedTrain(None)
			self.cbTrains.SetSelection(wx.NOT_FOUND)
		else:
			self.setSelectedTrain(self.trainList[tx])
			self.cbTrains.SetSelection(tx)
			
		self.setModified()
	
	def bAddStepPressed(self, _):
		steps = self.selectedTrainInfo["steps"]
		loc = self.teLoc.GetValue()
		if loc.strip() == "":
			vloc = 0
		else:
			try:
				vloc = int(loc)
			except:
				vloc = 0
			
		steps.append([self.teTower.GetValue(), self.teStop.GetValue(), vloc])
		oldct = self.lcSteps.GetItemCount()
		self.lcSteps.SetItemCount(oldct+1)
		self.lcSteps.setSelection(oldct)
		self.setModified()
		
	def bModStepPressed(self, _):
		if self.selectedStep is None:
			return
		step = self.selectedTrainInfo["steps"][self.selectedStep]
		step[0] = self.teTower.GetValue()
		step[1] = self.teStop.GetValue()
		loc = self.teLoc.GetValue()
		if loc.strip() == "":
			step[2] = 0
		else:
			try:
				step[2] = int(loc)
			except:
				step[2] = 0
		
		self.lcSteps.RefreshItem(self.selectedStep)
		self.setModified()
		
	def bDelStepPressed(self, _):
		if self.selectedStep is None:
			return
		
		del(self.selectedTrainInfo["steps"][self.selectedStep])
		newlen = len(self.selectedTrainInfo["steps"])
		self.lcSteps.SetItemCount(newlen)
		if self.selectedStep >= newlen:
			self.lcSteps.setSelection(newlen-1 if newlen > 0 else None)
		self.setModified()		
		
	def bUpPressed(self, _):
		if self.selectedStep is None:
			return
		i1 = self.selectedStep
		i2 = i1 - 1
		self.swapSteps(i1, i2)
	
	def bDownPressed(self, _):
		if self.selectedStep is None:
			return
		i1 = self.selectedStep
		i2 = i1 + 1
		self.swapSteps(i1, i2)
		
	def swapSteps(self,i1, i2):
		steps = self.selectedTrainInfo["steps"]
		tower = steps[i1][0]
		stop = steps[i1][1]
		loc = steps[i1][2]
		steps[i1][0] = steps[i2][0]
		steps[i1][1] = steps[i2][1]
		steps[i1][2] = steps[i2][2]
		steps[i2][0] = tower
		steps[i2][1] = stop
		steps[i2][2] = loc
		
		self.lcSteps.RefreshItems(i2, i1)
		self.lcSteps.setSelection(i2)
		self.setModified()
		
	def setSelectedTrain(self, tid):
		if tid == wx.NOT_FOUND or tid is None:
			self.selectedTid = None
			self.selectedTrainInfo = None
			self.bMod.Enable(False)
			self.bCopy.Enable(False)
			self.bModID.Enable(False)
			self.bDel.Enable(False)
			self.cbEast.SetValue(False)
			self.teDesc.SetValue("")
			self.lcSteps.setData([])
			return
		
		self.bMod.Enable(True)
		self.bCopy.Enable(True)
		self.bModID.Enable(True)
		self.bDel.Enable(True)
		self.selectedTid = tid
		self.selectedTrainInfo = self.roster[tid]
		
		self.cbEast.SetValue(self.selectedTrainInfo['dir'].lower() == 'east')
		self.stDirection.SetLabel("%sbound" % self.selectedTrainInfo["dir"])
		
		self.teDesc.SetValue(self.selectedTrainInfo["desc"])
		self.stDescription.SetLabel(self.selectedTrainInfo["desc"])
		
		self.lcSteps.setData(self.selectedTrainInfo["steps"])
		
		
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
		
	def bSaveAsPressed(self, _):
		dlg = wx.FileDialog(self, message="Save Train list to file", defaultDir=self.settings.traindir,
			defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False
		
		path = dlg.GetPath()
		dlg.Destroy()
		
		self.saveTrains(path)
		
		if os.path.basename(path) == self.settings.trainfile: # same as "Save"
			self.setModified(False)
		
	def bSavePressed(self, _):
		path = os.path.join(self.settings.traindir, self.settings.trainfile)
		self.saveTrains(path)
		self.setModified(False)
		
	def saveTrains(self, path):	
		with open(path, "w") as fp:
			json.dump(self.roster, fp, indent=4, sort_keys=True)
		
	def bOKPressed(self, _):
		if self.modified:
			path = os.path.join(self.settings.traindir, self.settings.trainfile)
			self.saveTrains(path)
			self.setModified(False)
			
		if self.everModified:
			self.EndModal(wx.ID_OK)
		else:
			self.EndModal(wx.ID_EXIT)
		
	def getValues(self):
		return self.roster
	
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'The train roster has been changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
								'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)

		
class StepsList(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(550, 240),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.InsertColumn(0, "Tower")
		self.InsertColumn(1, "Loc")
		self.InsertColumn(2, "Stop")
		self.SetColumnWidth(0, 150)
		self.SetColumnWidth(1, 50)
		self.SetColumnWidth(2, 400)

		self.SetItemCount(0)
		self.selected = None

		self.attr1 = wx.ItemAttr()
		self.attr2 = wx.ItemAttr()
		self.attr1.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.attr2.SetBackgroundColour(wx.Colour(138, 255, 197))
		
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)
		
	def setData(self, steps):
		self.steps = steps
		self.SetItemCount(0)
		self.SetItemCount(len(self.steps))
			
	def getSelection(self):
		if self.selected is None:
			return None
		
		if self.selected < 0 or self.selected >= self.GetItemCount():
			return None
		
		return self.selected
	
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
		if item < 0 or item >= len(self.steps):
			return None
		
		if col == 0:
			return self.steps[item][0]
		elif col == 1:
			return "%2d" % self.steps[item][2] if self.steps[item][2] != 0 else ""
		elif col == 2:
			return self.steps[item][1]

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return self.attr1
