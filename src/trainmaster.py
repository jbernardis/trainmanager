import os
import wx

from trainroster import TrainRoster
from engineers import Engineers
from order import Order
from activetrainlist import ActiveTrainList
from manageengineers import ManageEngineersDlg
from settings import Settings

BTNSZ = (90, 46)

MENU_FILE_LOAD_TRAIN = 100
MENU_FILE_LOAD_ENG  = 101
MENU_FILE_LOAD_ORDER = 103
MENU_FILE_EXIT = 199
MENU_MANAGE_ENGINEERS = 200

wildcard = "JSON file (*.json)|*.json|"	 \
		   "All files (*.*)|*.*"
wildcardTxt = "TXT file (*.txt)|*.txt|"	 \
		   "All files (*.*)|*.*"

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(480, 800))
		self.Bind(wx.EVT_CLOSE, self.onClose)

		self.CreateStatusBar()
		menuBar = wx.MenuBar()
		
		self.trainfile = None
		self.orderfile = None

		self.menuFile = wx.Menu()		
		self.menuFile.Append(MENU_FILE_LOAD_TRAIN, "&Load Train Roster", "Load Train Roster")
		self.menuFile.Append(MENU_FILE_LOAD_ORDER, "&Load Train Order", "Load Train Order List")
		self.menuFile.Append(MENU_FILE_LOAD_ENG, "&Load Engineer list", "Load Engineer List")
		self.menuFile.AppendSeparator()
		self.menuFile.Append(MENU_FILE_EXIT, "&Exit", "Exit Program")
		
		self.menuManage = wx.Menu()
		self.menuManage.Append(MENU_MANAGE_ENGINEERS, "&Manage Engineers", "Manage the content and ordering of active engineers list")
		
		menuBar.Append(self.menuFile, "&File")
		menuBar.Append(self.menuManage, "&Manage")
				
		self.SetMenuBar(menuBar)
		self.menuBar = menuBar

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = TrainMasterPanel(self)
		sizer.Add(self.panel)
		
		self.Bind(wx.EVT_MENU, self.panel.onOpenTrain, id=MENU_FILE_LOAD_TRAIN)
		self.Bind(wx.EVT_MENU, self.panel.onOpenEngineer, id=MENU_FILE_LOAD_ENG)
		self.Bind(wx.EVT_MENU, self.panel.onOpenOrder, id=MENU_FILE_LOAD_ORDER)
		self.Bind(wx.EVT_MENU, self.onClose, id=MENU_FILE_EXIT)
		self.Bind(wx.EVT_MENU, self.panel.onManageEngineers, id=MENU_MANAGE_ENGINEERS)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def setTitle(self, train=None, order=None):
		if train is not None:
			self.trainfile = train
			
		if order is not None:
			self.orderfile = order
			
		title = "Train Master"
		if self.trainfile is not None:
			title += " - %s" % self.trainfile
			
		if self.orderfile is not None:
			title += " / %s" % self.orderfile
		
		self.SetTitle(title)
	
	def onClose(self, _):
		self.panel.onClose(None)
		self.Destroy()
		
class TrainMasterPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.parent = parent
		
		self.parent.setTitle()
			
		self.pendingTrains = []
		self.activeEngineers = [] 
		self.allPresentEngineers = [x for x in self.activeEngineers]
		
		vsizerl = wx.BoxSizer(wx.VERTICAL)
		vsizerl.Add(wx.StaticText(self, wx.ID_ANY, "", size=(200, -1)))
		vsizerl.AddSpacer(20)
		
		self.chTrain = wx.Choice(self, wx.ID_ANY, choices=self.pendingTrains)
		self.chTrain.SetSelection(0)
		self.Bind(wx.EVT_CHOICE, self.onChoiceTID, self.chTrain)

		font = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Next Train: ", size=(100, -1))
		st.SetFont(font)
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chTrain)
		vsizerl.Add(sz)
		
		vsizerl.AddSpacer(10)
		
		self.chEngineer = wx.Choice(self, wx.ID_ANY, choices=self.activeEngineers)
		self.chEngineer.SetSelection(0)
		self.selectedEngineer = self.chEngineer.GetString(0)
		self.Bind(wx.EVT_CHOICE, self.onChoiceEngineer, self.chEngineer)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Engineer: ", size=(100, -1))
		st.SetFont(font)
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chEngineer)
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
		self.bAssign.Enable(len(self.activeEngineers) != 0 and len(self.pendingTrains) != 0)
		
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

		self.SetSizer(wsizer)
		self.Layout()
		self.Fit()
		
		wx.CallAfter(self.initialize)
		
	def initialize(self):
		self.settings = Settings(os.getcwd())
		
		self.trainFile = self.settings.trainfile
		self.orderFile = self.settings.orderfile
		self.parent.setTitle(train=self.trainFile, order=self.orderFile)
		
		self.loadEngineerFile(os.path.join(self.settings.engineerdir, self.settings.engineerfile))

		self.loadTrainFile(os.path.join(self.settings.traindir, self.settings.trainfile))
		
		self.loadOrderFile(os.path.join(self.settings.orderdir, self.settings.orderfile))
		
	def onOpenTrain(self, _):
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
			defaultDir=self.settings.traindir,
			defaultFile="",
			wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return 

		path = dlg.GetPath()
		dlg.Destroy()
		
		self.settings.traindir, self.settings.trainfile = os.path.split(path)
		self.settings.setModified()
		
		self.loadTrainFile(path)
		
	def loadTrainFile(self, fn):
		self.parent.setTitle(train=os.path.basename(fn))

		try:
			self.roster = TrainRoster(fn)
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, 'Unable to open Train roster file %s' % fn,
                   'File Not Found',
                   wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

			self.roster = None

		engRunning = self.activeTrainList.getEngineers()
		self.activeEngineers += engRunning
		self.allPresentEngineers = [x for x in self.activeEngineers]
		self.chEngineer.SetItems(self.activeEngineers)
		if len(self.activeEngineers) > 0:
			self.chEngineer.SetSelection(0)
		self.chEngineer.Enable(len(self.activeEngineers) > 0)
		
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.activeEngineers) > 0)
		self.bSkip.Enable(len(self.pendingTrains) > 0)
		self.bRemove.Enable(False)
		self.bReassign.Enable(False)

		self.activeTrainList.clear()
		self.cbATC.SetValue(False)

		self.chTrain.SetItems(self.pendingTrains)
		self.chTrain.Enable(len(self.pendingTrains) > 0)
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.activeEngineers) > 0)
		
		if len(self.pendingTrains) > 0:
			self.chTrain.SetSelection(0)
			tid = self.chTrain.GetString(0)
		else:
			self.chTrain.SetSelection(wx.NOT_FOUND)
			tid = None
			
		self.setSelectedTrain(tid)

	def onOpenEngineer(self, _):
		if self.activeTrainList.count() > 0:
			dlg = wx.MessageDialog(self, 'This will clear out any active trains.\nPress "Yes" to proceed, or "No" to cancel.',
	                               'Data will be lost',
	                               wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		dlg = wx.FileDialog(
			self, message="Choose an engineer file",
			defaultDir=self.settings.engineerdir,
			defaultFile="",
			wildcard=wildcardTxt,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return 

		path = dlg.GetPath()
		dlg.Destroy()
		
		self.settings.engineerdir, self.settings.engineerfile = os.path.split(path)
		self.settings.setModified()
		
		self.loadEngineerFile(path)

	def loadEngineerFile(self, fn):
		try:
			self.engineers = Engineers(fn)
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, 'Unable to open Engineer file %s' % fn,
                   'File Not Found',
                   wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

			self.engineers = None
			
		self.activeEngineers = []
		self.allPresentEngineers = [x for x in self.activeEngineers]
		self.chEngineer.SetItems(self.activeEngineers)
		self.chEngineer.Enable(len(self.activeEngineers) > 0)

		self.activeTrainList.clear()
		self.cbATC.SetValue(False)
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.activeEngineers) > 0)
		self.bRemove.Enable(False)
		self.bReassign.Enable(False)
		
		if len(self.activeEngineers) > 0:
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)
		else:
			self.chEngineer.SetSelection(wx.NOT_FOUND)
			self.selectedEngineer = None
			
	def onOpenOrder(self, _):
		if self.activeTrainList.count() > 0:
			dlg = wx.MessageDialog(self, 'This will clear out any active trains.\nPress "Yes" to proceed, or "No" to cancel.',
	                               'Data will be lost',
	                               wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		dlg = wx.FileDialog(
			self, message="Choose an order file",
			defaultDir=self.settings.orderdir,
			defaultFile="",
			wildcard=wildcardTxt,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return 

		path = dlg.GetPath()
		dlg.Destroy()
		
		self.settings.orderdir, self.settings.orderfile = os.path.split(path)
		self.settings.setModified()
		
		self.loadOrderFile(path)
		
	def loadOrderFile(self, fn):
		self.parent.setTitle(order=os.path.basename(fn))
		try:
			self.pendingTrains = [x for x in Order(fn)]
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, 'Unable to open Order file %s' % fn,
                   'File Not Found',
                   wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			
			self.pendingTrains = []

		self.chTrain.SetItems(self.pendingTrains)
		if len(self.pendingTrains) > 0:
			self.setSelectedTrain(self.chTrain.GetString(0))
			
		self.chTrain.Enable(len(self.pendingTrains) > 0)
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.activeEngineers) > 0)

		self.activeTrainList.clear()
		self.cbATC.SetValue(False)
		self.bRemove.Enable(False)
		self.bReassign.Enable(False)
		
		if len(self.pendingTrains) > 0:
			self.chTrain.SetSelection(0)
			tid = self.chTrain.GetString(0)
		else:
			self.chTrain.SetSelection(wx.NOT_FOUND)
			tid = None
			
		self.setSelectedTrain(tid)

		
	def onCbATC(self, _):
		if len(self.pendingTrains) == 0:
			return
		
		if len(self.activeEngineers) == 0:
			self.bAssign.Enable(self.cbATC.IsChecked())
		
	def bAssignPressed(self, _):
		tInfo = self.roster.getTrain(self.selectedTrain)
		if tInfo is None:
			return
		
		if self.cbATC.IsChecked():
			eng = "ATC"
		else:
			eng = self.selectedEngineer
		
		acttr = {
			"tid": self.selectedTrain,
			"dir": tInfo["dir"],
			"origin": tInfo["origin"],
			"terminus": tInfo["terminus"],
			"engineer": eng}
		self.activeTrainList.addTrain(acttr)
		
		self.pendingTrains.remove(self.selectedTrain)
		self.chTrain.SetItems(self.pendingTrains)
		if len(self.pendingTrains) == 0:
			self.chTrain.Enable(False)
			self.bAssign.Enable(False)
			self.bSkip.Enable(False)
			self.showInfo(None)
		else:
			self.chTrain.SetSelection(0)
			self.setSelectedTrain(self.chTrain.GetString(0))
		
		if not self.cbATC.IsChecked():
			self.activeEngineers.remove(self.selectedEngineer)
			self.chEngineer.SetItems(self.activeEngineers)
			if len(self.activeEngineers) == 0:
				self.chEngineer.Enable(False)
				self.bAssign.Enable(False)
			else:
				self.chEngineer.SetSelection(0)
				self.selectedEngineer = self.chEngineer.GetString(0)
				
		else:
			self.cbATC.SetValue(False)
			self.bAssign.Enable(len(self.pendingTrains) != 0 and len(self.activeEngineers) != 0)

	def bReassignPressed(self, _):
		t = self.activeTrainList.getSelection()
		if t is None:
			return

		if t["engineer"] in self.allPresentEngineers:
			if t["engineer"] not in self.activeEngineers:
				self.activeEngineers.append(t["engineer"])
			self.chEngineer.Enable(True)
			self.chEngineer.SetItems(self.activeEngineers)
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)

		engActive = self.activeTrainList.getEngineers()	
		if t["engineer"] != "ATC":
			eng = ["ATC"]
		else:
			eng = []	
			
		eng += sorted([x for x in self.engineers if x not in engActive])
		
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
			self.chEngineer.SetItems(self.activeEngineers)
			if len(self.activeEngineers) == 0:
				self.chEngineer.Enable(False)
				self.bAssign.Enable(self.cbATC.IsChecked())
			else:
				self.chEngineer.SetSelection(0)
				self.selectedEngineer = self.chEngineer.GetString(0)
				self.bAssign.Enable(True)
		
		self.activeTrainList.setNewEngineer(neng)
		
	def bSkipPressed(self, _):
		tInfo = self.roster.getTrain(self.selectedTrain)
		if tInfo is None:
			return
		
		self.pendingTrains.remove(self.selectedTrain)
		self.chTrain.SetItems(self.pendingTrains)
		if len(self.pendingTrains) == 0:
			self.chTrain.Enable(False)
			self.bAssign.Enable(False)
			self.bSkip.Enable(False)
			self.showInfo(None)
		else:
			self.chTrain.SetSelection(0)
			self.setSelectedTrain(self.chTrain.GetString(0))
			
	def bRemovePressed(self, _):
		t = self.activeTrainList.getSelection()
		if t is not None:
			self.activeTrainList.delSelected()
			if t["engineer"] in self.allPresentEngineers:
				if t["engineer"] not in self.activeEngineers:
					self.activeEngineers.append(t["engineer"])
				self.chEngineer.Enable(True)
				self.chEngineer.SetItems(self.activeEngineers)
				self.chEngineer.SetSelection(0)
				self.selectedEngineer = self.chEngineer.GetString(0)
				
			if len(self.pendingTrains) > 0 and (len(self.activeEngineers) > 0 or self.cbATC.IsChecked()):
				self.bAssign.Enable(True)
				
			self.bRemove.Enable(False)
			self.bReassign.Enable(False)
		
	def onChoiceTID(self, _):
		tx = self.chTrain.GetSelection()
		if tx == wx.NOT_FOUND:
			return
		
		tid = self.chTrain.GetString(tx)
		self.setSelectedTrain(tid)
		
	def reportSelection(self, tx):
		if tx is None:
			self.bRemove.Enable(False)
			self.bReassign.Enable(False)
		else:
			self.bRemove.Enable(True)
			self.bReassign.Enable(True)
		
	def onChoiceEngineer(self, _):
		ex = self.chEngineer.GetSelection()
		if ex == wx.NOT_FOUND:
			return
		
		self.selectedEngineer = self.chEngineer.GetString(ex)
		
	def setSelectedTrain(self, tid):
		self.selectedTrain = tid
		self.showInfo(tid)
		
	def showInfo(self, tid):
		if tid is None or tid == "":
			self.stDescription.SetLabel("")
			self.stStepsTower.SetLabel("")
			self.stStepsStop.SetLabel("")
			return
		
		if self.roster is None:
			self.stDescription.SetLabel("Train Roster is empty")
			self.stStepsTower.SetLabel("")
			self.stStepsStop.SetLabel("")
			return
		else:
			tInfo = self.roster.getTrain(tid)
			
		if tInfo is None:
			self.stDescription.SetLabel("Train %s is not in Train Roster" % tid)
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
		self.chEngineer.SetItems(self.activeEngineers)
		self.chEngineer.Enable(len(self.activeEngineers) > 0)
		if len(self.pendingTrains) > 0 and (len(self.activeEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)
		self.chEngineer.SetSelection(0)
		self.selectedEngineer = self.chEngineer.GetString(0)
		
		self.allPresentEngineers = [x for x in self.activeEngineers] + currentEngineers
			
	def onClose(self, _):
		self.settings.save()
		self.Destroy()

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		self.SetTopWindow(self.frame)
		return True

app = App(False)
app.MainLoop()
