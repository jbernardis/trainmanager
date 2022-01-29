import os
import wx

from trainroster import TrainRoster
from engineers import Engineers
from activetrainlist import ActiveTrainList
from manageengineers import ManageEngineersDlg

BTNSZ = (90, 46)

MENU_FILE_OPEN = 100
MENU_FILE_RELOAD = 101
MENU_FILE_EXIT = 102
MENU_MANAGE_ENGINEERS = 200

wildcard = "JSON file (*.json)|*.json|"	 \
		   "All files (*.*)|*.*"

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(480, 800))
		self.Bind(wx.EVT_CLOSE, self.onClose)

		self.CreateStatusBar()
		menuBar = wx.MenuBar()

		self.menuFile = wx.Menu()		
		self.menuFile.Append(MENU_FILE_OPEN, "&Open", "Open Train List")
		self.menuFile.Append(MENU_FILE_RELOAD, "&Reload", "Reload Train List")
		self.menuFile.AppendSeparator()
		self.menuFile.Append(MENU_FILE_EXIT, "&Exit", "Exit Program")
		
		self.menuManage = wx.Menu()
		self.menuManage.Append(MENU_MANAGE_ENGINEERS, "&Manage Engineers", "Manage the active engineers list")
		
		menuBar.Append(self.menuFile, "&File")
		menuBar.Append(self.menuManage, "&Manage")
				
		self.SetMenuBar(menuBar)
		self.menuBar = menuBar

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = TrainMasterPanel(self)
		sizer.Add(self.panel)
		
		self.Bind(wx.EVT_MENU, self.panel.onOpen, id=MENU_FILE_OPEN)
		self.Bind(wx.EVT_MENU, self.panel.onReload, id=MENU_FILE_RELOAD)
		self.Bind(wx.EVT_MENU, self.onClose, id=MENU_FILE_EXIT)
		self.Bind(wx.EVT_MENU, self.panel.onManageEngineers, id=MENU_MANAGE_ENGINEERS)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def setTitle(self, fn):
		self.SetTitle("Train Master - %s" % fn)
	
	def onClose(self, _):
		self.panel.onClose(None)
		self.Destroy()
		
class TrainMasterPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.trainFileName = "trains.json"
		self.parent = parent
		
		self.parent.setTitle(self.trainFileName)
		
		self.roster = TrainRoster(self.trainFileName)
		self.activeTrains = [tid for tid in self.roster.getTrainOrder()]
		
		self.engineers = Engineers()
		self.activeEngineers = [] #e for e in self.engineers]
		self.allPresentEngineers = [x for x in self.activeEngineers]
		
		vsizerl = wx.BoxSizer(wx.VERTICAL)
		vsizerl.Add(wx.StaticText(self, wx.ID_ANY, "", size=(200, -1)))
		vsizerl.AddSpacer(20)
		
		self.trainId = wx.Choice(self, wx.ID_ANY, choices=self.activeTrains)
		self.trainId.SetSelection(0)
		self.Bind(wx.EVT_CHOICE, self.onChoiceTID, self.trainId)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.Add(wx.StaticText(self, wx.ID_ANY, "Next Train: ", size=(100, -1)))
		sz.Add(self.trainId)
		vsizerl.Add(sz)
		
		vsizerl.AddSpacer(10)
		
		self.engineer = wx.Choice(self, wx.ID_ANY, choices=self.activeEngineers)
		self.engineer.SetSelection(0)
		self.selectedEngineer = self.engineer.GetString(0)
		self.Bind(wx.EVT_CHOICE, self.onChoiceEngineer, self.engineer)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.Add(wx.StaticText(self, wx.ID_ANY, "Engineer: ", size=(100, -1)))
		sz.Add(self.engineer)
		vsizerl.Add(sz)
		
		vsizerl.AddSpacer(10)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		self.cbATC = wx.CheckBox(self, wx.ID_ANY, "ATC")
		self.Bind(wx.EVT_CHECKBOX, self.onCbATC, self.cbATC)
		sz.AddSpacer(100)
		sz.Add(self.cbATC)
		vsizerl.Add(sz)
		
		vsizerl.AddSpacer(20)
		
		vsizerr = wx.BoxSizer(wx.VERTICAL)
		vsizerr.Add(wx.StaticText(self, wx.ID_ANY, "", size=(300, -1)))
		vsizerr.AddSpacer(20)
		
		font = wx.Font(wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL, faceName="Monospace"))
		fontb = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
		self.stDescription = wx.StaticText(self, wx.ID_ANY, "", size=(400, -1))
		self.stDescription.SetFont(fontb)
		vsizerr.Add(self.stDescription)
		vsizerr.AddSpacer(10)
		self.stStepsTower = wx.StaticText(self, wx.ID_ANY, "", size=(100, 150))
		self.stStepsStop = wx.StaticText(self, wx.ID_ANY, "", size=(300, 150))
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.Add(self.stStepsTower)
		sz.Add(self.stStepsStop)
		vsizerr.Add(sz)
		self.stStepsTower.SetFont(font)
		self.stStepsStop.SetFont(font)
		
		vsizerr.AddSpacer(20)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizerl)
		hsizer.AddSpacer(10)
		hsizer.Add(vsizerr)
		hsizer.AddSpacer(20)
		
		wsizer = wx.BoxSizer(wx.VERTICAL)
		wsizer.Add(hsizer)
		
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bAssign = wx.Button(self, wx.ID_ANY, "Assign\nTrain/Engineer", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bAssignPressed, self.bAssign)
		btnsizer.Add(self.bAssign)
		self.bAssign.Enable(len(self.activeEngineers) != 0 and len(self.activeTrains) != 0)
		
		btnsizer.AddSpacer(30)
		
		self.bSkip = wx.Button(self, wx.ID_ANY, "Skip\nTrain", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bSkipPressed, self.bSkip)
		btnsizer.Add(self.bSkip)
		
		btnsizer.AddSpacer(30)
		
		self.bRemove = wx.Button(self, wx.ID_ANY, "Remove\nActive Train", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bRemovePressed, self.bRemove)
		btnsizer.Add(self.bRemove)
		self.bRemove.Enable(False)

		btnsizer.AddSpacer(30)
		
		self.bReassign = wx.Button(self, wx.ID_ANY, "Change\nEngineer", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bReassignPressed, self.bReassign)
		btnsizer.Add(self.bReassign)
		self.bReassign.Enable(False)
		
		wsizer.Add(btnsizer, 1, wx.ALIGN_CENTER_HORIZONTAL)
		wsizer.AddSpacer(20)
		
		self.activeTrainList = ActiveTrainList(self)
		wsizer.Add(self.activeTrainList, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		wsizer.AddSpacer(20)

		
		self.setSelectedTrain(self.trainId.GetString(0))
		self.selectedEngineer = self.engineer.GetString(0)
		
		self.SetSizer(wsizer)
		self.Layout()
		self.Fit()
		
	def onReload(self, _):
		if self.activeTrainList.count() > 0:
			dlg = wx.MessageDialog(self, 'This will clear out any active trains.\nPress "Yes" to proceed, or "No" to cancel.',
	                               'Data will be lost',
	                               wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		self.loadTrainFile()
		
	def onOpen(self, _):
		if self.activeTrainList.count() > 0:
			dlg = wx.MessageDialog(self, 'This will clear out any active trains.\nPress "Yes" to proceed, or "No" to cancel.',
	                               'Data will be lost',
	                               wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		dlg = wx.FileDialog(
			self, message="Choose a Train roster file",
			defaultDir=os.getcwd(),
			defaultFile="",
			wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return 

		self.trainFileName = dlg.GetPath()
		dlg.Destroy()
		
		self.parent.setTitle(os.path.basename(self.trainFileName))
		self.loadTrainFile()
		
	def loadTrainFile(self):
		self.roster = TrainRoster(self.trainFileName)
		self.activeTrains = [tid for tid in self.roster.getTrainOrder()]
		self.trainId.SetItems(self.activeTrains)
		if len(self.activeTrains) > 0:
			self.trainId.SetSelection(0)
		self.trainId.Enable(len(self.activeTrains) > 0)

		engRunning = self.activeTrainList.getEngineers()
		self.activeEngineers += engRunning
		self.allPresentEngineers = [x for x in self.activeEngineers]
		self.engineer.SetItems(self.activeEngineers)
		if len(self.activeEngineers) > 0:
			self.engineer.SetSelection(0)
		self.engineer.Enable(len(self.activeEngineers) > 0)
		
		self.bAssign.Enable(len(self.activeTrains) > 0 and len(self.activeEngineers) > 0)
		self.bSkip.Enable(len(self.activeTrains) > 0)
		self.bRemove.Enable(False)
		self.bReassign.Enable(False)

		self.activeTrainList.clear()
		self.cbATC.SetValue(False)
		
		
	def onCbATC(self, _):
		if len(self.activeTrains) == 0:
			return
		
		if len(self.activeEngineers) == 0:
			self.bAssign.Enable(self.cbATC.IsChecked())
		
	def bAssignPressed(self, _):
		tInfo = self.roster.getTrain(self.chosenTrain)
		if tInfo is None:
			return
		
		if self.cbATC.IsChecked():
			eng = "ATC"
		else:
			eng = self.selectedEngineer
		
		acttr = {
			"tid": self.chosenTrain,
			"dir": tInfo["dir"],
			"origin": tInfo["origin"],
			"terminus": tInfo["terminus"],
			"engineer": eng}
		self.activeTrainList.addTrain(acttr)
		
		self.activeTrains.remove(self.chosenTrain)
		self.trainId.SetItems(self.activeTrains)
		if len(self.activeTrains) == 0:
			self.trainId.Enable(False)
			self.bAssign.Enable(False)
			self.bSkip.Enable(False)
			self.showInfo(None)
		else:
			self.trainId.SetSelection(0)
			self.setSelectedTrain(self.trainId.GetString(0))
		
		if not self.cbATC.IsChecked():
			self.activeEngineers.remove(self.selectedEngineer)
			self.engineer.SetItems(self.activeEngineers)
			if len(self.activeEngineers) == 0:
				self.engineer.Enable(False)
				self.bAssign.Enable(False)
			else:
				self.engineer.SetSelection(0)
				self.selectedEngineer = self.engineer.GetString(0)
				
		else:
			self.cbATC.SetValue(False)
			self.bAssign.Enable(len(self.activeTrains) != 0 and len(self.activeEngineers) != 0)

	def bReassignPressed(self, _):
		t = self.activeTrainList.getSelection()
		if t is None:
			return

		if t["engineer"] in self.allPresentEngineers:
			if t["engineer"] not in self.activeEngineers:
				self.activeEngineers.append(t["engineer"])
			self.engineer.Enable(True)
			self.engineer.SetItems(self.activeEngineers)
			self.engineer.SetSelection(0)
			self.selectedEngineer = self.engineer.GetString(0)

		engActive = self.activeTrainList.getEngineers()		
		eng = ["ATC"] + sorted([x for x in self.engineers if x not in engActive])
		
		dlg = wx.SingleChoiceDialog(self, 'Choose New Engineer', 'Reassign Engineer',
				eng,
				wx.CHOICEDLG_STYLE
				)

		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			neng = dlg.GetStringSelection()

		dlg.Destroy()	
		
		if rc != wx.ID_OK:
			dlg.Destroy()
			return

		if neng in self.activeEngineers:
			self.activeEngineers.remove(neng)
			self.engineer.SetItems(self.activeEngineers)
			if len(self.activeEngineers) == 0:
				self.engineer.Enable(False)
				self.bAssign.Enable(self.cbATC.IsChecked())
			else:
				self.engineer.SetSelection(0)
				self.selectedEngineer = self.engineer.GetString(0)
				self.bAssign.Enable(True)
		
		self.activeTrainList.setNewEngineer(neng)
		
	def bSkipPressed(self, _):
		tInfo = self.roster.getTrain(self.chosenTrain)
		if tInfo is None:
			return
		
		self.activeTrains.remove(self.chosenTrain)
		self.trainId.SetItems(self.activeTrains)
		if len(self.activeTrains) == 0:
			self.trainId.Enable(False)
			self.bAssign.Enable(False)
			self.bSkip.Enable(False)
			self.showInfo(None)
		else:
			self.trainId.SetSelection(0)
			self.setSelectedTrain(self.trainId.GetString(0))
			
	def bRemovePressed(self, _):
		t = self.activeTrainList.getSelection()
		if t is not None:
			self.activeTrainList.delSelected()
			if t["engineer"] in self.allPresentEngineers:
				if t["engineer"] not in self.activeEngineers:
					self.activeEngineers.append(t["engineer"])
				self.engineer.Enable(True)
				self.engineer.SetItems(self.activeEngineers)
				self.engineer.SetSelection(0)
				self.selectedEngineer = self.engineer.GetString(0)
				
			if len(self.activeTrains) > 0 and (len(self.activeEngineers) > 0 or self.cbATC.IsChecked()):
				self.bAssign.Enable(True)
				
			self.bRemove.Enable(False)
			self.bReassign.Enable(False)
		
	def onChoiceTID(self, _):
		tx = self.trainId.GetSelection()
		if tx == wx.NOT_FOUND:
			return
		
		tid = self.trainId.GetString(tx)
		self.setSelectedTrain(tid)
		
	def reportSelection(self, tx):
		if tx is None:
			self.bRemove.Enable(False)
			self.bReassign.Enable(False)
		else:
			self.bRemove.Enable(True)
			self.bReassign.Enable(True)
		
	def onChoiceEngineer(self, _):
		ex = self.engineer.GetSelection()
		if ex == wx.NOT_FOUND:
			return
		
		self.selectedEngineer = self.engineer.GetString(ex)
		
	def setSelectedTrain(self, tid):
		self.chosenTrain = tid
		self.showInfo(tid)
		
	def showInfo(self, tid):
		if tid is None:
			self.stDescription.SetLabel("")
			self.stStepsTower.SetLabel("")
			self.stStepsStop.SetLabel("")
			return
		
		tInfo = self.roster.getTrain(tid)
		if tInfo is None:
			self.stDescription.SetLabel("")
			self.stStepsTower.SetLabel("")
			self.stStepsStop.SetLabel("")
			return

		descr = "%sbound %s" % (tInfo["dir"], tInfo["desc"])		
		self.stDescription.SetLabel(descr)
		towers = "\n".join([step[0] for step in tInfo["steps"]])
		stops  = "\n".join([step[1] for step in tInfo["steps"]])

		self.stStepsTower.SetLabel(towers)
		self.stStepsStop.SetLabel(stops)
		
	def onManageEngineers(self, _):
		currentEngineers = self.activeTrainList.getEngineers()
		availableEngineers = [x for x in list(self.engineers) if x not in currentEngineers]
		dlg = ManageEngineersDlg(self, availableEngineers, self.activeEngineers)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			newEngs = dlg.getValues()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 

		self.activeEngineers = newEngs		
		self.engineer.SetItems(self.activeEngineers)
		self.engineer.Enable(len(self.activeEngineers) > 0)
		if len(self.activeTrains) > 0 and (len(self.activeEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)
		self.engineer.SetSelection(0)
		self.selectedEngineer = self.engineer.GetString(0)
		
		self.allPresentEngineers = [x for x in self.activeEngineers] + currentEngineers
			
	def onClose(self, _):
		self.Destroy()

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		self.SetTopWindow(self.frame)
		return True

app = App(False)
app.MainLoop()
