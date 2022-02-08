import os
import wx

from trainroster import TrainRoster
from locomotives import Locomotives
from engineers import Engineers
from order import Order
from activetrainlist import ActiveTrainList
from managetrains import ManageTrainsDlg
from manageengineers import ManageEngineersDlg
from manageorder import ManageOrderDlg
from managelocos import ManageLocosDlg
from assignlocos import AssignLocosDlg
from viewlogdlg import ViewLogDlg
from settings import Settings
from reports import Report
from log import Log

BTNSZ = (120, 46)

MENU_FILE_LOAD_TRAIN = 100
MENU_FILE_LOAD_ENG  = 101
MENU_FILE_LOAD_ORDER = 102
MENU_FILE_LOAD_LOCOS = 103
MENU_FILE_VIEW_LOG = 110
MENU_FILE_CLEAR_LOG = 111
MENU_FILE_SAVE_LOG = 112
MENU_FILE_EXIT = 199
MENU_MANAGE_TRAINS = 200
MENU_MANAGE_ENGINEERS = 201
MENU_MANAGE_RESET_ORDER = 202
MENU_MANAGE_ASSIGN_LOCOS = 203
MENU_MANAGE_LOCOS = 204
MENU_MANAGE_ORDER = 205
MENU_REPORT_OP_WORKSHEET = 301
MENU_REPORT_TRAIN_CARDS = 302


wildcard = "JSON file (*.json)|*.json|"	 \
		   "All files (*.*)|*.*"
wildcardTxt = "TXT file (*.txt)|*.txt|"	 \
		   "All files (*.*)|*.*"
wildcardLog = "Log file (*.log)|*.log|"	 \
		   "All files (*.*)|*.*"

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		font = wx.Font(wx.Font(14, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))

		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap("trainmanager.ico", wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)

		self.CreateStatusBar()
		menuBar = wx.MenuBar()
		
		self.trainfile = None
		self.orderfile = None
		self.engineerfile = None
		self.locofile = None

		self.menuFile = wx.Menu()	
		i = wx.MenuItem(self.menuFile, MENU_FILE_LOAD_TRAIN, "Load Train Roster", helpString ="Load a Train Roster file")
		i.SetFont(font)
		self.menuFile.Append(i)
		i = wx.MenuItem(self.menuFile, MENU_FILE_LOAD_ORDER, "Load Train Order", helpString="Load Train Order/Sequence file")
		i.SetFont(font)
		self.menuFile.Append(i)
		i = wx.MenuItem(self.menuFile, MENU_FILE_LOAD_LOCOS, "Load Loco List", helpString="Load locomotive descriptions")
		i.SetFont(font)
		self.menuFile.Append(i)
		i = wx.MenuItem(self.menuFile, MENU_FILE_LOAD_ENG, "Load Engineer list", helpString="Load Engineer List")
		i.SetFont(font)
		self.menuFile.Append(i)
		self.menuFile.AppendSeparator()
		i = wx.MenuItem(self.menuFile, MENU_FILE_VIEW_LOG, "View Log", helpString="View Log")
		i.SetFont(font)
		self.menuFile.Append(i)
		i = wx.MenuItem(self.menuFile, MENU_FILE_SAVE_LOG, "Save Log", helpString="Save Log")
		i.SetFont(font)
		self.menuFile.Append(i)
		i = wx.MenuItem(self.menuFile, MENU_FILE_CLEAR_LOG, "Clear Log", helpString="Clear Log")
		i.SetFont(font)
		self.menuFile.Append(i)
		self.menuFile.AppendSeparator()
		i = wx.MenuItem(self.menuFile, MENU_FILE_EXIT, "Exit", helpString="Exit Program")
		i.SetFont(font)
		self.menuFile.Append(i)
		
		self.menuManage = wx.Menu()
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_TRAINS, "Manage Trains", helpString="Manage the train rodter")
		i.SetFont(font)
		self.menuManage.Append(i)
		self.menuManage.AppendSeparator()
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_ENGINEERS, "Manage Engineers", helpString="Manage the content and ordering of active engineers list")
		i.SetFont(font)
		self.menuManage.Append(i)
		self.menuManage.AppendSeparator()
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_LOCOS, "Manage Locomotives", helpString="Define, modify, delete locomotives")
		i.SetFont(font)
		self.menuManage.Append(i)
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_ASSIGN_LOCOS, "Assign Locomotives", helpString="Assign locomotives to trains")
		i.SetFont(font)
		self.menuManage.Append(i)
		self.menuManage.AppendSeparator()
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_ORDER, "Manage Train Order", helpString="Add/remove trains and modify sequence")
		i.SetFont(font)
		self.menuManage.Append(i)
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_RESET_ORDER, "Reset Train Order", helpString="Reset Train Order back to the beginning")
		i.SetFont(font)
		self.menuManage.Append(i)
		
		self.menuReports = wx.Menu()
		i = wx.MenuItem(self.menuManage, MENU_REPORT_OP_WORKSHEET, "Operating Worksheet", helpString="Print an Operating Worksheet")
		i.SetFont(font)
		self.menuReports.Append(i)
		i = wx.MenuItem(self.menuManage, MENU_REPORT_TRAIN_CARDS, "Train Cards", helpString="Print Train Cards")
		i.SetFont(font)
		self.menuReports.Append(i)

		menuBar.Append(self.menuFile, "File")
		menuBar.Append(self.menuManage, "Manage")
		menuBar.Append(self.menuReports, "Reports")
				
		self.SetMenuBar(menuBar)
		self.menuBar = menuBar

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = TrainManagerPanel(self)
		sizer.Add(self.panel)
		
		self.Bind(wx.EVT_MENU, self.panel.onOpenTrain, id=MENU_FILE_LOAD_TRAIN)
		self.Bind(wx.EVT_MENU, self.panel.onOpenEngineer, id=MENU_FILE_LOAD_ENG)
		self.Bind(wx.EVT_MENU, self.panel.onOpenOrder, id=MENU_FILE_LOAD_ORDER)
		self.Bind(wx.EVT_MENU, self.panel.onOpenLocos, id=MENU_FILE_LOAD_LOCOS)
		self.Bind(wx.EVT_MENU, self.panel.onViewLog, id=MENU_FILE_VIEW_LOG)
		self.Bind(wx.EVT_MENU, self.panel.onClearLog, id=MENU_FILE_CLEAR_LOG)
		self.Bind(wx.EVT_MENU, self.panel.onSaveLog, id=MENU_FILE_SAVE_LOG)
		self.Bind(wx.EVT_MENU, self.onClose, id=MENU_FILE_EXIT)
		
		self.Bind(wx.EVT_MENU, self.panel.onManageTrains, id=MENU_MANAGE_TRAINS)
		self.Bind(wx.EVT_MENU, self.panel.onManageEngineers, id=MENU_MANAGE_ENGINEERS)
		self.Bind(wx.EVT_MENU, self.panel.onResetOrder, id=MENU_MANAGE_RESET_ORDER)
		self.Bind(wx.EVT_MENU, self.panel.onManageOrder, id=MENU_MANAGE_ORDER)
		self.Bind(wx.EVT_MENU, self.panel.onAssignLocos, id=MENU_MANAGE_ASSIGN_LOCOS)
		self.Bind(wx.EVT_MENU, self.panel.onManageLocos, id=MENU_MANAGE_LOCOS)
		
		self.Bind(wx.EVT_MENU, self.panel.onReportOpWorksheet, id=MENU_REPORT_OP_WORKSHEET)
		self.Bind(wx.EVT_MENU, self.panel.onReportTrainCards, id=MENU_REPORT_TRAIN_CARDS)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def setTitle(self, train=None, order=None, engineer=None, loco=None):
		if train is not None:
			self.trainfile = train
			
		if order is not None:
			self.orderfile = order
			
		if engineer is not None:
			self.engineerfile = engineer
			
		if loco is not None:
			self.locofile = loco
			
		title = "Train Manager"
		if self.trainfile is not None:
			title += " - %s" % self.trainfile
		else:
			title += " - "
			
		if self.orderfile is not None:
			title += " / %s" % self.orderfile
		else:
			title += " / "
			
		if self.engineerfile is not None:
			title += " / %s" % self.engineerfile
		else:
			title += " / "
			
		if self.locofile is not None:
			title += " / %s" % self.locofile
		else:
			title += " / "
		
		self.SetTitle(title)
		
	def disableReports(self):
		self.menuReports.Enable(MENU_REPORT_OP_WORKSHEET, False)
	
	def onClose(self, _):
		self.panel.onClose(None)
		self.Destroy()
		
class TrainManagerPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.parent = parent
		
		self.parent.setTitle()
			
		self.log = Log()

		self.pendingTrains = []
		self.activeEngineers = [] 
		self.allPresentEngineers = [x for x in self.activeEngineers]
		self.trainOrder = None
		
		vsizerl = wx.BoxSizer(wx.VERTICAL)
		vsizerl.Add(wx.StaticText(self, wx.ID_ANY, "", size=(200, -1)))
		vsizerl.AddSpacer(20)

		
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		labelFont = wx.Font(wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL, faceName="Monospace"))
		labelFontBold = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		
		self.chTrain = wx.Choice(self, wx.ID_ANY, choices=self.pendingTrains)
		self.chTrain.SetSelection(0)
		self.chTrain.SetFont(textFont)
		self.Bind(wx.EVT_CHOICE, self.onChoiceTID, self.chTrain)


		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Next Train: ", size=(100, -1))
		st.SetFont(textFontBold)
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chTrain)
		vsizerl.Add(sz)
		
		vsizerl.AddSpacer(10)
		
		self.chEngineer = wx.Choice(self, wx.ID_ANY, choices=self.activeEngineers)
		self.chEngineer.SetSelection(0)
		self.chEngineer.SetFont(textFont)
		self.selectedEngineer = self.chEngineer.GetString(0)
		self.Bind(wx.EVT_CHOICE, self.onChoiceEngineer, self.chEngineer)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Engineer: ", size=(100, -1))
		st.SetFont(textFontBold)
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chEngineer)
		vsizerl.Add(sz)
		
		vsizerl.AddSpacer(10)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		self.cbATC = wx.CheckBox(self, wx.ID_ANY, "ATC")
		self.cbATC.SetFont(textFontBold)
		self.Bind(wx.EVT_CHECKBOX, self.onCbATC, self.cbATC)
		sz.AddSpacer(100)
		sz.Add(self.cbATC)
		vsizerl.Add(sz)
		
		vsizerl.AddSpacer(20)
		
		vsizerr = wx.BoxSizer(wx.VERTICAL)
		vsizerr.Add(wx.StaticText(self, wx.ID_ANY, "", size=(300, -1)))
		vsizerr.AddSpacer(20)

		self.stDescription = wx.StaticText(self, wx.ID_ANY, "", size=(400, -1))
		self.stDescription.SetFont(labelFontBold)
		vsizerr.Add(self.stDescription)
		vsizerr.AddSpacer(10)
		self.stStepsTower = wx.StaticText(self, wx.ID_ANY, "", size=(100, 150))
		self.stStepsStop = wx.StaticText(self, wx.ID_ANY, "", size=(300, 150))
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.Add(self.stStepsTower)
		sz.Add(self.stStepsStop)
		vsizerr.Add(sz)
		self.stStepsTower.SetFont(labelFont)
		self.stStepsStop.SetFont(labelFont)
		
		self.stLocoInfo = wx.StaticText(self, wx.ID_ANY, "", size=(700, -1))
		self.stLocoInfo.SetFont(labelFontBold)
		vsizerr.AddSpacer(10)
		vsizerr.Add(self.stLocoInfo)
		
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
		self.bAssign.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bAssignPressed, self.bAssign)
		btnsizer.Add(self.bAssign)
		self.bAssign.Enable(len(self.activeEngineers) != 0 and len(self.pendingTrains) != 0)
		
		btnsizer.AddSpacer(30)
		
		self.bSkip = wx.Button(self, wx.ID_ANY, "Skip\nTrain", size=BTNSZ)
		self.bSkip.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bSkipPressed, self.bSkip)
		btnsizer.Add(self.bSkip)
		
		btnsizer.AddSpacer(30)
		
		self.bRemove = wx.Button(self, wx.ID_ANY, "Remove\nActive Train", size=BTNSZ)
		self.bRemove.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bRemovePressed, self.bRemove)
		btnsizer.Add(self.bRemove)
		self.bRemove.Enable(False)

		btnsizer.AddSpacer(30)
		
		self.bReassign = wx.Button(self, wx.ID_ANY, "Change\nEngineer", size=BTNSZ)
		self.bReassign.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bReassignPressed, self.bReassign)
		btnsizer.Add(self.bReassign)
		self.bReassign.Enable(False)

		btnsizer.AddSpacer(30)
		
		self.bShowDetails = wx.Button(self, wx.ID_ANY, "Show Train\nDetails", size=BTNSZ)
		self.bShowDetails.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bShowDetailsPressed, self.bShowDetails)
		btnsizer.Add(self.bShowDetails)
		self.bShowDetails.Enable(False)
		
		wsizer.Add(btnsizer, 1, wx.ALIGN_CENTER_HORIZONTAL)
		wsizer.AddSpacer(20)
		
		self.activeTrainList = ActiveTrainList(self)
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(10)
		sz.Add(self.activeTrainList)
		sz.AddSpacer(20)
		
		wsizer.Add(sz)
		
		wsizer.AddSpacer(20)

		self.SetSizer(wsizer)
		self.Layout()
		self.Fit()
		
		wx.CallAfter(self.initialize)
		
	def initialize(self):
		self.settings = Settings(self, os.getcwd())
		
		self.trainFile = self.settings.trainfile
		self.orderFile = self.settings.orderfile
		self.engineerFile = self.settings.engineerfile
		self.locoFile = self.settings.locofile
		
		self.loadLocoFile(os.path.join(self.settings.locodir, self.settings.locofile))
		
		self.parent.setTitle(train=self.trainFile, order=self.orderFile, engineer=self.engineerFile, loco=self.locoFile)
		
		self.loadEngineerFile(os.path.join(self.settings.engineerdir, self.settings.engineerfile))

		self.loadTrainFile(os.path.join(self.settings.traindir, self.settings.trainfile))
		
		self.loadOrderFile(os.path.join(self.settings.orderdir, self.settings.orderfile))
		
		self.report = Report(self)
		if not self.report.Initialized():
			self.parent.disableReports()

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
		
	def onOpenLocos(self, _):
		dlg = wx.FileDialog(
			self, message="Choose a locomotive file",
			defaultDir=self.settings.locodir,
			defaultFile="",
			wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return 

		path = dlg.GetPath()
		dlg.Destroy()
		
		self.settings.locodir, self.settings.locofile = os.path.split(path)
		self.settings.setModified()
		
		self.loadLocoFile(path)
		self.showInfo(self.selectedTrain)
					
	def loadLocoFile(self, fn):
		self.parent.setTitle(loco=os.path.basename(fn))
		try:
			self.locos = Locomotives(fn)
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, 'Unable to open Locomotives file %s' % fn,
                   'File Not Found',
                   wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

			self.locos = None
		self.updateActiveListLocos()
		
	def updateActiveListLocos(self):
		actTrains = self.activeTrainList.getTrains()
		locos = self.locos.getLocoList()
		for tid in actTrains:
			atInfo = self.activeTrainList.getTrainByTid(tid)
			tInfo = self.roster.getTrain(tid)
			if atInfo is not None:
				rloco = tInfo["loco"]
				if rloco not in locos:
					ndesc = ""
				else:
					ndesc = self.locos.getLoco(rloco)

				self.activeTrainList.updateTrain(tid, rloco, ndesc)
					
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
		self.parent.setTitle(engineer=os.path.basename(fn))
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
			
	def onResetOrder(self, _):
		if self.activeTrainList.count() > 0:
			dlg = wx.MessageDialog(self, 'This will clear out any active trains.\nPress "Yes" to proceed, or "No" to cancel.',
	                               'Data will be lost',
	                               wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		if self.trainOrder is None:
			self.pendingTrains = []
		else:
			self.pendingTrains = [x for x in self.trainOrder]
			
		self.setTrainOrder()
		
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
			self.trainOrder = Order(fn)
			self.pendingTrains = [x for x in self.trainOrder]
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, 'Unable to open Order file %s' % fn,
	               'File Not Found',
	               wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			
			self.pendingTrains = []
			
		self.setTrainOrder()
				
	def setTrainOrder(self):
		self.chTrain.SetItems(self.pendingTrains)
		if len(self.pendingTrains) > 0:
			self.setSelectedTrain(self.chTrain.GetString(0))
			
		engRunning = self.activeTrainList.getEngineers()
		self.activeEngineers += engRunning
		self.allPresentEngineers = [x for x in self.activeEngineers]
		self.chEngineer.SetItems(self.activeEngineers)
		if len(self.activeEngineers) > 0:
			self.chEngineer.SetSelection(0)
		self.chEngineer.Enable(len(self.activeEngineers) > 0)
			
		self.chTrain.Enable(len(self.pendingTrains) > 0)
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.activeEngineers) > 0)
		self.bSkip.Enable(len(self.pendingTrains) > 0)

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

	def onViewLog(self, _):
		dlg = ViewLogDlg(self, self.log)
		dlg.ShowModal()
		dlg.Destroy()
		
			
	def onClearLog(self, _):
		self.log.clear()
		
	def onSaveLog(self, _):
		dlg = wx.FileDialog(self, message="Save log to file", defaultDir=self.settings.logdir,
			defaultFile="", wildcard=wildcardLog, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			return False
		
		path = dlg.GetPath()
		dlg.Destroy()
	
		self.settings.logdir = os.path.split(path)[0]
		self.settings.setModified()

		with open(path, "w") as ofp:
			for ln in self.log:
				ofp.write("%s\n" % ln)

		
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

		if tInfo["loco"] is None:
			loco = ""
			descr = ""
		else:
			loco = tInfo["loco"]
			descr = self.locos.getLoco(loco)		
		acttr = {
			"tid": self.selectedTrain,
			"dir": tInfo["dir"],
			"origin": tInfo["origin"],
			"terminus": tInfo["terminus"],
			"loco": loco,
			"descr": descr,
			"engineer": eng}
		self.activeTrainList.addTrain(acttr)
		self.log.append("Assigned train %s to %s" % (self.selectedTrain, eng))
		
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
		
		if t["engineer"] in self.allPresentEngineers:
			if t["engineer"] not in self.activeEngineers:
				self.activeEngineers.append(t["engineer"])
			self.chEngineer.Enable(True)
			self.chEngineer.SetItems(self.activeEngineers)
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)

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

		oeng = t["engineer"]		
		self.activeTrainList.setNewEngineer(neng)
		self.log.append("Reassigned train %s from %s to %s" % (t["tid"], oeng, neng))
		
	def bShowDetailsPressed(self, _):
		t = self.activeTrainList.getSelection()
		if t is None:
			return
		
		self.showDetails(t)
		
	def showDetails(self, t):
		if t is None:
			return
		
		tid = t["tid"]
		tinfo = self.roster.getTrain(tid)
		
		lid = t["loco"]
		if lid is None or lid == "":
			desc = ""
		else:
			desc = self.locos.getLoco(lid)
			
		dlg = DetailsDlg(self, tid, tinfo, desc, t["engineer"])
		dlg.Show()
		
	def bSkipPressed(self, _):
		tInfo = self.roster.getTrain(self.selectedTrain)
		if tInfo is None:
			return
		
		self.log.append("Skipped train %s" % self.selectedTrain)
		
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
			self.log.append("Removed train %s from active list" % t["tid"])
			self.activeTrainList.delSelected()
			if t["engineer"] in self.allPresentEngineers:
				self.log.append("Returned engineer %s to pool" % t["engineer"])
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
		self.bRemove.Enable(tx is not None)
		self.bReassign.Enable(tx is not None)
		self.bShowDetails.Enable(tx is not None)
		
	def reportDoubleClick(self, tx):
		self.reportSelection(tx)
		tinfo = self.activeTrainList.getTrain(tx)
		self.showDetails(tinfo)
		
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
		# TODO - May have to limit how many lines we see here - or come up with other approach
		
		if tInfo["loco"] is None:
			self.stLocoInfo.SetLabel("")
		else:
			lId = tInfo["loco"]
			lInfo = self.locos.getLoco(lId)
			if lInfo is None:
				self.stLocoInfo.SetLabel("Loco: %s" % lId)
			else:
				self.stLocoInfo.SetLabel("Loco: %s - %s" % (lId, lInfo))
				
	def onManageOrder(self, _):
		if self.activeTrainList.count() > 0:
			dlg = wx.MessageDialog(self, 'This will clear out any active trains.\nPress "Yes" to proceed, or "No" to cancel.',
	                               'Data will be lost',
	                               wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		dlg = ManageOrderDlg(self, self.trainOrder, self.roster, self.settings)
		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			norder = dlg.getValues()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		if self.trainOrder is None:
			self.pendingTrains = [x for x in norder]
		else:
			self.trainOrder.setNewOrder(norder)
			self.pendingTrains = [x for x in self.trainOrder]
			
		self.setTrainOrder()

	def onManageTrains(self, _):
		dlg = ManageTrainsDlg(self, self.roster, self.locos, self.settings)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		
		# no need to retrieve dialog values because the data is saved automatically when OK is pressed
		# just re-read the file
		self.loadTrainFile(os.path.join(self.settings.traindir, self.settings.trainfile))

		
	def onManageEngineers(self, _):
		currentEngineers = self.activeTrainList.getEngineers()
		availableEngineers = [x for x in list(self.engineers) if x not in currentEngineers]
		dlg = ManageEngineersDlg(self, availableEngineers, self.activeEngineers, currentEngineers, self.settings)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			newEngs, allEngs = dlg.getValues()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		
		for eng in self.engineers:
			if not eng in allEngs:
				self.engineers.delete(eng)

		for eng in allEngs:
			if not self.engineers.contains(eng):
				self.engineers.add(eng)

		self.log.append("New Engineer list: %s" % str(newEngs))
		self.activeEngineers = newEngs		
		self.chEngineer.SetItems(self.activeEngineers)
		self.chEngineer.Enable(len(self.activeEngineers) > 0)
		if len(self.pendingTrains) > 0 and (len(self.activeEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)
		self.chEngineer.SetSelection(0)
		self.selectedEngineer = self.chEngineer.GetString(0)
		
		self.allPresentEngineers = [x for x in self.activeEngineers] + currentEngineers
		
	def onManageLocos(self, _):
		dlg = ManageLocosDlg(self, self.locos, self.settings)
		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			modlocos, delLocos = dlg.getValues()
			
		dlg.Destroy()
				
		if rc != wx.ID_OK:
			return
		
		for lId in modlocos.keys():
			self.locos.setDescription(lId, modlocos[lId])
			
		for lId in delLocos:
			self.locos.delete(lId)
			
		self.showInfo(self.selectedTrain)
		self.updateActiveListLocos()
		
	def onAssignLocos(self, _):
		order = [x for x in self.trainOrder]
		dlg = AssignLocosDlg(self, self.roster, order, self.locos)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			result = dlg.getValues()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		for tid in self.trainOrder:
			tinfo = self.roster.getTrain(tid)
			if tinfo["loco"] != result[tid]:
				self.log.append("Assigned loco %s to train %s (old value %s)" % (result[tid], tid, tinfo["loco"]))
				tinfo["loco"] = result[tid]
					
		self.showInfo(self.selectedTrain)
		self.updateActiveListLocos()
		self.roster.save()
		
	def onReportOpWorksheet(self, _):
		self.report.OpWorksheetReport(self.roster, self.trainOrder, self.locos)
			
	def onReportTrainCards(self, _):
		self.report.TrainCards(self.roster, self.trainOrder)
			
	def onClose(self, _):
		self.settings.save()
		self.Destroy()
		
class DetailsDlg(wx.Dialog):
	def __init__(self, parent, tid, tinfo, desc, engineer):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Train Details")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		labelFont = wx.Font(wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL, faceName="Monospace"))
		labelFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
		labelFontLargeBold = wx.Font(wx.Font(16, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
		
		vsizer=wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		st1 = wx.StaticText(self, wx.ID_ANY, tid, size=(80, -1))
		st1.SetFont(labelFontLargeBold)
		
		st2 = wx.StaticText(self, wx.ID_ANY, "%sbound %s" % (tinfo["dir"], tinfo["desc"]))
		st2.SetFont(labelFontBold)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st1)
		hsz.Add(st2)
		
		vsizer.Add(hsz)
		vsizer.AddSpacer(10)
		
		st = wx.StaticText(self, wx.ID_ANY, "Loco: %s - %s" % (tinfo["loco"], desc))
		st.SetFont(labelFontBold)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(100)
		hsz.Add(st)
		
		vsizer.Add(hsz)
		vsizer.AddSpacer(10)
		
		st = wx.StaticText(self, wx.ID_ANY, "Engineer: %s" % engineer)
		st.SetFont(labelFontBold)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(100)
		hsz.Add(st)
		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		for stp in tinfo["steps"]:
			st1 = wx.StaticText(self, wx.ID_ANY, stp[0], size=(80, -1))
			st1.SetFont(labelFontBold)
			st2 = wx.StaticText(self, wx.ID_ANY, stp[1])
			st2.SetFont(labelFontBold)
			
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(120)
			hsz.Add(st1)
			hsz.Add(st2)
			
			vsizer.Add(hsz)
			vsizer.AddSpacer(2)


		
		
		
		
		vsizer.AddSpacer(20)
				
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)
		self.SetSizer(hsizer)

		self.Layout()
		self.Fit()
		
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
