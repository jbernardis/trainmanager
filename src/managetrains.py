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
				"desc": ti["desc"]
				}
			
			steps = [[s[0], s[1]] for s in ti["steps"]]
			info["steps"] = steps
			
			self.roster[t] = info
		
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		
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
		self.stLocomotive = wx.StaticText(self, wx.ID_ANY, "", size=(200, -1))
		self.stLocomotive.SetFont(textFontBold)
		
		sz.AddSpacer(5)
		sz.Add(self.stDirection)
		sz.AddSpacer(10)
		sz.Add(self.stDescription)
		sz.AddSpacer(10)
		sz.Add(self.stLocomotive)
		sz.AddSpacer(50)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Eastbound:", size=(120, -1))
		st.SetFont(textFont)
		hsz.Add(st, 0, wx.TOP, 5)
		hsz.AddSpacer(5)
		self.cbEast = wx.CheckBox(self, wx.ID_ANY, "", style=wx.ALIGN_RIGHT)
		self.cbEast.SetFont(textFont)
		hsz.Add(self.cbEast)
		
		sz.Add(hsz)
		sz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Description:", size=(120, -1))
		st.SetFont(textFont)
		hsz.Add(st, 0, wx.TOP, 5)
		hsz.AddSpacer(5)
		self.teDesc = wx.TextCtrl(self, wx.ID_ANY, "", size=(200, -1))
		self.teDesc.SetFont(textFont)
		hsz.Add(self.teDesc)
		
		sz.Add(hsz)
		sz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Locomotive:", size=(120, -1))
		st.SetFont(textFont)
		hsz.Add(st, 0, wx.TOP, 5)
		hsz.AddSpacer(5)
		self.teLoco = wx.TextCtrl(self, wx.ID_ANY, "", size=(100, -1))
		self.teLoco.SetFont(textFont)
		hsz.Add(self.teLoco)
		
		sz.Add(hsz)
		
		hsizer.AddSpacer(20)
		
		hsizer.Add(sz)
		

		hsizer.AddSpacer(20)
		
		sz = wx.BoxSizer(wx.VERTICAL)
				
		self.lcSteps = StepsList(self)
		self.lcSteps.SetFont(textFont)
		sz.Add(self.lcSteps)
		sz.AddSpacer(10)
		
		self.teTower = wx.TextCtrl(self, wx.ID_ANY, "", size=(100, -1))
		self.teTower.SetFont(textFont)
		
		self.teStop = wx.TextCtrl(self, wx.ID_ANY, "", size=(300, -1))
		self.teStop.SetFont(textFont)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Tower: ")
		st.SetFont(textFontBold)
		hsz.Add(st, 0, wx.TOP, 5)
		hsz.AddSpacer(5)
		hsz.Add(self.teTower)
		
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
		
		self.bMod = wx.Button(self, wx.ID_ANY, "Modify\nTrain", size=BTNSZ)
		self.bMod.SetFont(btnFont)
		self.bMod.SetToolTip("Update the currently selected train with the above direction/description/loco number")
		self.Bind(wx.EVT_BUTTON, self.bModPressed, self.bMod)
		btnSizer.Add(self.bMod)
		self.bMod.Enable(False)
		
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
			'dir': "East",
			'desc': "",
			'loco': "",
			'steps': []
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
		
		loco = self.teLoco.GetValue().strip()
		self.stLocomotive.SetLabel("Loco: %s" % loco)
		if loco == "":
			loco = None
		self.selectedTrainInfo["loco"] = loco
		
		self.setSelectedTrain(self.selectedTid)
		self.setModified()
		
	def bDelPressed(self, _):
		if self.selectedTid is None:
			return
		if self.selectedTrainInfo is None:
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
		steps.append([self.teTower.GetValue(), self.teStop.GetValue()])
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
		steps[i1][0] = steps[i2][0]
		steps[i1][1] = steps[i2][1]
		steps[i2][0] = tower
		steps[i2][1] = stop
		
		self.lcSteps.RefreshItems(i2, i1)
		self.lcSteps.setSelection(i2)
		self.setModified()
		
	def setSelectedTrain(self, tid):
		if tid == wx.NOT_FOUND or tid is None:
			self.selectedTid = None
			self.selectedTrainInfo = None
			self.bMod.Enable(False)
			self.bDel.Enable(False)
			self.cbEast.SetValue(False)
			self.teDesc.SetValue("")
			self.teLoco.SetValue("")			
			self.lcSteps.setData([])
			return
		
		self.bMod.Enable(True)
		self.bDel.Enable(True)
		self.selectedTid = tid
		self.selectedTrainInfo = self.roster[tid]
		
		self.cbEast.SetValue(self.selectedTrainInfo['dir'].lower() == 'east')
		self.stDirection.SetLabel("%sbound" % self.selectedTrainInfo["dir"])
		
		self.teDesc.SetValue(self.selectedTrainInfo["desc"])
		self.stDescription.SetLabel(self.selectedTrainInfo["desc"])
		
		loco = self.selectedTrainInfo["loco"]
		if loco is None:
			loco = ""
		self.teLoco.SetValue(loco)
		self.stLocomotive.SetLabel("Loco: %s" % loco)
		
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
		self.InsertColumn(1, "Stop")
		self.SetColumnWidth(0, 150)
		self.SetColumnWidth(1, 400)

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
			return self.steps[item][1]

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return self.attr1
