import os
import wx
import wx.lib.gizmos as gizmos

from wx.lib import newevent

from trainroster import TrainRoster
from locomotives import Locomotives
from engineers import Engineers
from order import Order
from activetrain import ActiveTrain
from activetrainlist import ActiveTrainList, FWD_128, FWD_28, REV_128, REV_28, STOP 
from activetrainlistctrl import ActiveTrainListCtrl
from activetrainlistdlg import ActiveTrainListDlg
from completedtrainlist import CompletedTrainList
from managetrains import ManageTrainsDlg
from manageengineers import ManageEngineersDlg
from manageorder import ManageOrderDlg
from managelocos import ManageLocosDlg
from assignlocos import AssignLocosDlg
from viewlogdlg import ViewLogDlg
from detailsdlg import DetailsDlg
from aboutdlg import AboutDlg
from settings import Settings
from reports import Report
from completedtrains import CompletedTrains
from log import Log
from listener import Listener
from backup import saveData, restoreData
from dccsniffer import DCCSniffer
from serial import SerialException
from optionsdlg import OptionsDlg
from engqueuedlg import EngQueueDlg
from sessionscheduledlg import SessionScheduleDlg

# class dummyDCCEvt:
# 	def __init__(self, loco, spd):
# 		self.dcc = {"instr": "F", "param": spd, "loco": loco}
# self.onDCCMessage(dummyDCCEvt("2216", "10"))
# self.onDCCMessage(dummyDCCEvt("2216", "0"))

DEVELOPMODE = False
VERSIONDATE = "2-February-2023"

BTNSZ = (120, 46)

MENU_FILE_VIEW_LOG = 110
MENU_FILE_CLEAR_LOG = 111
MENU_FILE_SAVE_LOG = 112
MENU_FILE_ABOUT = 120
MENU_FILE_BACKUP = 113
MENU_FILE_RESTORE = 114
MENU_FILE_EXIT = 199
MENU_MANAGE_TRAINS = 200
MENU_MANAGE_ENGINEERS = 201
MENU_MANAGE_ASSIGN_LOCOS = 203
MENU_MANAGE_LOCOS = 204
MENU_MANAGE_ORDER = 205
MENU_MANAGE_SESSION_SCHEDULE = 207
MENU_MANAGE_OPTIONS = 206
MENU_MANAGE_RESET = 299
MENU_REPORT_OP_WORKSHEET = 301
MENU_REPORT_TRAIN_CARDS = 302
MENU_REPORT_LOCOS = 303
MENU_REPORT_STATUS = 304
MENU_DISPATCH_CONNECT = 401
MENU_DISPATCH_DISCONNECT = 402
MENU_DISPATCH_SETUPIP = 403
MENU_DISPATCH_SETUPPORT = 404
MENU_DISPATCH_RESET = 405
MENU_DCC_CONNECT = 501
MENU_DCC_DISCONNECT = 502
MENU_DCC_SETUPPORT = 503
MENU_DCC_SETUPBAUD = 504
MENU_VIEW_ENG_QUEUE = 601
MENU_VIEW_ACTIVE_TRAINS = 602
MENU_VIEW_LEGEND = 603
MENU_VIEW_SHOWATTENTION = 604
MENU_VIEW_SORT = 610
MENU_SORT_TID = 650
MENU_SORT_TIME = 651
MENU_SORT_GROUP = 652
MENU_SORT_ASCENDING = 653

DEADMANSET = 10

MAX_STEPS = 9


wildcard = "JSON file (*.json)|*.json|"	 \
				"All files (*.*)|*.*"
wildcardTxt = "TXT file (*.txt)|*.txt|"	 \
				"All files (*.*)|*.*"
wildcardLog = "Log file (*.log)|*.log|"	 \
				"All files (*.*)|*.*"

(TrainLocationEvent, EVT_TRAINLOC) = newevent.NewEvent()  
(TrainSignalEvent, EVT_TRAINSIG) = newevent.NewEvent()  
(ClockEvent, EVT_CLOCK) = newevent.NewEvent()  
(BreakerEvent, EVT_BREAKER) = newevent.NewEvent()  
(SocketConnectEvent, EVT_SOCKET_CONNECT) = newevent.NewEvent()
(SocketDisconnectEvent, EVT_SOCKET_DISCONNECT) = newevent.NewEvent()
(SocketFailureEvent, EVT_SOCKET_FAILURE) = newevent.NewEvent()
(MessageEvent, EVT_MESSAGE) = newevent.NewEvent()  

(DCCMessageEvent, EVT_DCCMESSAGE) = newevent.NewEvent()  
(DCCClosedEvent,  EVT_DCCCLOSED)  = newevent.NewEvent()  
(DCCLogEvent,     EVT_DCCLOG)     = newevent.NewEvent()  

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.Bind(wx.EVT_CLOSE, self.onClose)

		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap("traintracker.ico", wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)

		self.CreateStatusBar()
		menuBar = wx.MenuBar()
		
		self.trainfile = None
		self.orderfile = None
		self.engineerfile = None
		self.locofile = None
		self.connection = None
		self.dcc = None
		self.sessionsched = None

		self.menuFile = wx.Menu()

		i = wx.MenuItem(self.menuFile, MENU_FILE_VIEW_LOG, "View Log", helpString="View Log")
		self.menuFile.Append(i)
		
		i = wx.MenuItem(self.menuFile, MENU_FILE_SAVE_LOG, "Save Log", helpString="Save Log")
		self.menuFile.Append(i)
		
		i = wx.MenuItem(self.menuFile, MENU_FILE_CLEAR_LOG, "Clear Log", helpString="Clear Log")
		self.menuFile.Append(i)
		
		self.menuFile.AppendSeparator()
		
		i = wx.MenuItem(self.menuFile, MENU_FILE_BACKUP, "Backup", helpString="Backup data files to a ZIP file")
		self.menuFile.Append(i)
		
		i = wx.MenuItem(self.menuFile, MENU_FILE_RESTORE, "Restore", helpString="Restore data files from a ZIP file")
		self.menuFile.Append(i)
		
		self.menuFile.AppendSeparator()
		
		i = wx.MenuItem(self.menuFile, MENU_FILE_ABOUT, "About", helpString="About")
		self.menuFile.Append(i)
		
		self.menuFile.AppendSeparator()
		
		i = wx.MenuItem(self.menuFile, MENU_FILE_EXIT, "Exit", helpString="Exit Program")
		self.menuFile.Append(i)
		
		self.menuSort = wx.Menu()
		
		i = wx.MenuItem(self.menuSort, MENU_SORT_TID, "Train ID", helpString="Sort Based on Train ID", kind=wx.ITEM_RADIO)
		self.menuSort.Append(i)
		
		i = wx.MenuItem(self.menuSort, MENU_SORT_TIME, "Time", helpString="Sort Based on Train running time", kind=wx.ITEM_RADIO)
		self.menuSort.Append(i)
		i.Check()
		
		self.menuSort.AppendSeparator()
				
		i = wx.MenuItem(self.menuSort, MENU_SORT_GROUP, "Group by Direction", helpString="Group East and West trains together", kind=wx.ITEM_CHECK)
		self.menuSort.Append(i)
		i.Check(False)
		
		self.menuSort.AppendSeparator()
				
		i = wx.MenuItem(self.menuSort, MENU_SORT_ASCENDING, "Ascending", helpString="Sort ascending", kind=wx.ITEM_CHECK)
		self.menuSort.Append(i)
		i.Check(False)

		self.menuView = wx.Menu()
		
		i = wx.MenuItem(self.menuView, MENU_VIEW_SORT, "Sort Active Trains", helpString="Change sorting parameters", subMenu=self.menuSort)
		self.menuView.Append(i)
		
		self.menuView.AppendSeparator()
		
		i = wx.MenuItem(self.menuView, MENU_VIEW_ENG_QUEUE, "Engineer Queue", helpString="Display Engineer Queue")
		self.menuView.Append(i)
		
		i = wx.MenuItem(self.menuView, MENU_VIEW_ACTIVE_TRAINS, "Active Train List", helpString="Display Active Train List")
		self.menuView.Append(i)

		i = wx.MenuItem(self.menuView, MENU_VIEW_SHOWATTENTION, "High-light Trains", helpString="Show High-lighting on trains that need attention", kind=wx.ITEM_CHECK)
		self.menuView.Append(i)
		i.Check(True)

		i = wx.MenuItem(self.menuView, MENU_VIEW_LEGEND, "Legend", helpString="Display a legend for icons")
		self.menuView.Append(i)
		
		self.menuManage = wx.Menu()
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_TRAINS, "Trains", helpString="Manage the train roster")
		self.menuManage.Append(i)
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_ORDER, "Train Order", helpString="Add/remove/reorder trains to/from the schedule and extra train list")
		self.menuManage.Append(i)
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_ENGINEERS, "Engineers", helpString="Manage the content and ordering of active engineers list")
		self.menuManage.Append(i)
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_LOCOS, "Locomotives", helpString="Define, modify, delete locomotives")
		self.menuManage.Append(i)
		
		self.menuManage.AppendSeparator()
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_SESSION_SCHEDULE, "Session Schedules", helpString="Create/manage session schedules based on the loaded train order")
		self.menuManage.Append(i)
		
		self.menuManage.AppendSeparator()
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_ASSIGN_LOCOS, "Assign Locomotives", helpString="Assign locomotives to trains")
		self.menuManage.Append(i)
		
		self.menuManage.AppendSeparator()
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_OPTIONS, "Preferences", helpString="Change preferences")
		self.menuManage.Append(i)
		
		self.menuManage.AppendSeparator()
		
		i = wx.MenuItem(self.menuManage, MENU_MANAGE_RESET, "Reset Session", helpString="Reset Operating Session")
		self.menuManage.Append(i)
		
		self.menuReports = wx.Menu()
		
		i = wx.MenuItem(self.menuReports, MENU_REPORT_OP_WORKSHEET, "Operating Worksheet", helpString="Print an Operating Worksheet")
		self.menuReports.Append(i)
		
		i = wx.MenuItem(self.menuReports, MENU_REPORT_TRAIN_CARDS, "Train Cards", helpString="Print Train Cards")
		self.menuReports.Append(i)
		
		i = wx.MenuItem(self.menuReports, MENU_REPORT_LOCOS, "Locomotives", helpString="Print Locomotive Roster")
		self.menuReports.Append(i)
		
		i = wx.MenuItem(self.menuReports, MENU_REPORT_STATUS, "Train Status", helpString="List of all active and completed trains")
		self.menuReports.Append(i)
		
		self.menuDispatch = wx.Menu()
		
		i = wx.MenuItem(self.menuDispatch, MENU_DISPATCH_CONNECT, "Connect", helpString="Connect to dispatcher")
		self.menuDispatch.Append(i)
		
		i = wx.MenuItem(self.menuDispatch, MENU_DISPATCH_DISCONNECT, "Disconnect", helpString="Disconnect from dispatcher")
		self.menuDispatch.Append(i)
		self.menuDispatch.Enable(MENU_DISPATCH_DISCONNECT, False)
		
		self.menuDispatch.AppendSeparator()
		
		i = wx.MenuItem(self.menuDispatch, MENU_DISPATCH_SETUPIP, "Configure IP Address", helpString="Configure IP address")
		self.menuDispatch.Append(i)
		
		i = wx.MenuItem(self.menuDispatch, MENU_DISPATCH_SETUPPORT, "Configure Port", helpString="Configure Port")
		self.menuDispatch.Append(i)
		
		self.menuDispatch.AppendSeparator()
		
		i = wx.MenuItem(self.menuDispatch, MENU_DISPATCH_RESET, "Reset Connection", helpString="Reset connection to dispatcher")
		self.menuDispatch.Append(i)
		
		self.menuDCC = wx.Menu()
		
		i = wx.MenuItem(self.menuDCC, MENU_DCC_CONNECT, "Connect", helpString="Connect to DCC Sniffer")
		self.menuDCC.Append(i)
		
		i = wx.MenuItem(self.menuDCC, MENU_DCC_DISCONNECT, "Disconnect", helpString="Disconnect from DCC Sniffer")
		self.menuDCC.Append(i)
		self.menuDCC.Enable(MENU_DCC_DISCONNECT, False)
		
		self.menuDCC.AppendSeparator()
		
		i = wx.MenuItem(self.menuDCC, MENU_DCC_SETUPPORT, "Configure DCC Port Name", helpString="Configure DCC Port Name")
		self.menuDCC.Append(i)
		
		i = wx.MenuItem(self.menuDCC, MENU_DCC_SETUPBAUD, "Configure DCC Baud Rate", helpString="Configure DCC Baud Rate")
		self.menuDCC.Append(i)

		menuBar.Append(self.menuFile, "File")
		menuBar.Append(self.menuView, "View")
		menuBar.Append(self.menuManage, "Manage")
		menuBar.Append(self.menuReports, "Reports")
		menuBar.Append(self.menuDispatch, "Dispatch")
		menuBar.Append(self.menuDCC, "DCC")
				
		self.SetMenuBar(menuBar)
		self.menuBar = menuBar

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = TrainTrackerPanel(self)
		sizer.Add(self.panel)
		
		self.Bind(wx.EVT_MENU, self.panel.onViewLog, id=MENU_FILE_VIEW_LOG)
		self.Bind(wx.EVT_MENU, self.panel.onClearLog, id=MENU_FILE_CLEAR_LOG)
		self.Bind(wx.EVT_MENU, self.panel.onSaveLog, id=MENU_FILE_SAVE_LOG)
		self.Bind(wx.EVT_MENU, self.panel.onAbout, id=MENU_FILE_ABOUT)
		self.Bind(wx.EVT_MENU, self.panel.onSaveData, id=MENU_FILE_BACKUP)
		self.Bind(wx.EVT_MENU, self.panel.onRestoreData, id=MENU_FILE_RESTORE)
		self.Bind(wx.EVT_MENU, self.onClose, id=MENU_FILE_EXIT)
		
		self.Bind(wx.EVT_MENU, self.panel.onViewEngQueue, id=MENU_VIEW_ENG_QUEUE)
		self.Bind(wx.EVT_MENU, self.panel.onViewActiveTrains, id=MENU_VIEW_ACTIVE_TRAINS)
		self.Bind(wx.EVT_MENU, self.panel.onViewHiLite, id=MENU_VIEW_SHOWATTENTION)
		self.Bind(wx.EVT_MENU, self.panel.onViewLegend, id=MENU_VIEW_LEGEND)
		self.Bind(wx.EVT_MENU, self.panel.onChangeSort, id=MENU_SORT_TID)	
		self.Bind(wx.EVT_MENU, self.panel.onChangeSort, id=MENU_SORT_TIME)		
		self.Bind(wx.EVT_MENU, self.panel.onChangeSort, id=MENU_SORT_GROUP)		
		self.Bind(wx.EVT_MENU, self.panel.onChangeSort, id=MENU_SORT_ASCENDING)
		
		self.Bind(wx.EVT_MENU, self.panel.onManageTrains, id=MENU_MANAGE_TRAINS)
		self.Bind(wx.EVT_MENU, self.panel.onManageEngineers, id=MENU_MANAGE_ENGINEERS)
		self.Bind(wx.EVT_MENU, self.panel.onManageOrder, id=MENU_MANAGE_ORDER)
		self.Bind(wx.EVT_MENU, self.panel.onAssignLocos, id=MENU_MANAGE_ASSIGN_LOCOS)
		self.Bind(wx.EVT_MENU, self.panel.onManageLocos, id=MENU_MANAGE_LOCOS)
		self.Bind(wx.EVT_MENU, self.panel.onManageOptions, id=MENU_MANAGE_OPTIONS)
		self.Bind(wx.EVT_MENU, self.panel.onResetSession, id=MENU_MANAGE_RESET)
		self.Bind(wx.EVT_MENU, self.panel.onManageSessionSchedule, id=MENU_MANAGE_SESSION_SCHEDULE)
		
		self.Bind(wx.EVT_MENU, self.panel.onReportOpWorksheet, id=MENU_REPORT_OP_WORKSHEET)
		self.Bind(wx.EVT_MENU, self.panel.onReportTrainCards, id=MENU_REPORT_TRAIN_CARDS)
		self.Bind(wx.EVT_MENU, self.panel.onReportLocos, id=MENU_REPORT_LOCOS)
		self.Bind(wx.EVT_MENU, self.panel.onReportStatus, id=MENU_REPORT_STATUS)
		
		self.Bind(wx.EVT_MENU, self.panel.connectToDispatch, id=MENU_DISPATCH_CONNECT)
		self.Bind(wx.EVT_MENU, self.panel.disconnectFromDispatch, id=MENU_DISPATCH_DISCONNECT)
		self.Bind(wx.EVT_MENU, self.panel.setupIP, id=MENU_DISPATCH_SETUPIP)
		self.Bind(wx.EVT_MENU, self.panel.setupPort, id=MENU_DISPATCH_SETUPPORT)
		self.Bind(wx.EVT_MENU, self.panel.resetConnection, id=MENU_DISPATCH_RESET)
		
		self.Bind(wx.EVT_MENU, self.panel.onConnectSnifferPressed, id=MENU_DCC_CONNECT)
		self.Bind(wx.EVT_MENU, self.panel.onDisconnectSnifferPressed, id=MENU_DCC_DISCONNECT)
		self.Bind(wx.EVT_MENU, self.panel.setupDCCtty, id=MENU_DCC_SETUPPORT)
		self.Bind(wx.EVT_MENU, self.panel.setupDCCBaud, id=MENU_DCC_SETUPBAUD)
		
		sizer.AddSpacer(100)
		self.SetSizer(sizer)
		self.Layout()
		self.Fit()
		
	def setTitle(self, train=None, order=None, engineer=None, loco=None, connection=None, dcc=None):
		if train is not None:
			self.trainfile = train
			
		if order is not None:
			self.orderfile = order
			
		if engineer is not None:
			self.engineerfile = engineer
			
		if loco is not None:
			self.locofile = loco
			
		if connection is not None:
			self.connection = connection
			
		if dcc is not None:
			self.dcc = dcc
			
		title = "Train Tracker"
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
		
		if self.connection is not None:
			title += "     %s / " % self.connection
		else:
			title += " / "
		
		if self.dcc is not None:
			title += "%s" % self.dcc
		self.SetTitle(title)
		
	def disableReports(self):
		for r in [ MENU_REPORT_OP_WORKSHEET, MENU_REPORT_TRAIN_CARDS, MENU_REPORT_LOCOS, MENU_REPORT_STATUS ]:
			self.menuReports.Enable(r, False)
		
	def enableListenerDisconnect(self, flag=True):
		self.menuDispatch.Enable(MENU_DISPATCH_DISCONNECT, flag)
		self.menuDispatch.Enable(MENU_DISPATCH_CONNECT, not flag)
	
	def onClose(self, _):
		self.panel.onClose(None)
		self.Destroy()


class TrainTrackerPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.SetBackgroundColour(wx.Colour(250, 250, 250))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.parent = parent
		
		self.parent.setTitle()
		self.setConnected(False)
		self.completedTrains = CompletedTrains()
			
		self.log = Log()
		
		self.listener = None
		self.sniffer = None
		self.dlgEngQueue = None
		self.dlgActiveTrains = None

		self.pendingTrains = []
		self.selectedEngineers = [] 
		self.idleEngineers = []
		self.trainOrder = None
		self.speeds = {}
		self.sessionSchedule = []
		self.sessionFile = None
		
		self.dlgSplash = None
		self.splashTimer = 0;

		self.dlgLegend = None

		self.atl = ActiveTrainList()
		self.atl.setSortKey("time")

		labelFontBold = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
		textFont = wx.Font(wx.Font(9, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(9, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		
		vsizerl = wx.BoxSizer(wx.VERTICAL)
		vsizerl.AddSpacer(20)

		boxTrain = wx.StaticBox(self, wx.ID_ANY, "Train")
		topBorder = boxTrain.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)
		bsizer.Add(wx.StaticText(boxTrain, wx.ID_ANY, "", size=(240, -1)))
		
		self.chTrain = wx.Choice(boxTrain, wx.ID_ANY, choices=self.pendingTrains, size=(120, -1))
		self.chTrain.SetSelection(0)
		self.Bind(wx.EVT_CHOICE, self.onChoiceTID, self.chTrain)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(boxTrain, wx.ID_ANY, "Scheduled: ", size=(120, -1))
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chTrain)
		
		self.bSkip = wx.Button(boxTrain, wx.ID_ANY, "-", size=(30, -1))
		self.Bind(wx.EVT_BUTTON, self.bSkipPressed, self.bSkip)
		self.bSkip.SetToolTip("Remove train from schedule")
		sz.AddSpacer(5)
		sz.Add(self.bSkip)
		bsizer.Add(sz)

		bsizer.AddSpacer(1)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(120)
		self.stSessionSchedule = wx.StaticText(boxTrain, wx.ID_ANY, "(Base)")
		sz.Add(self.stSessionSchedule)
		bsizer.Add(sz)

		bsizer.AddSpacer(20)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		self.cbExtra = wx.CheckBox(boxTrain, wx.ID_ANY, "Run Extra")
		self.Bind(wx.EVT_CHECKBOX, self.onCbExtra, self.cbExtra)
		sz.AddSpacer(100)
		sz.Add(self.cbExtra)
		self.cbExtra.Enable(False)
		bsizer.Add(sz)
		
		bsizer.AddSpacer(10)

		self.chExtra = wx.Choice(boxTrain, wx.ID_ANY, choices=[], size=(120, -1))
		self.chExtra.Enable(False)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(boxTrain, wx.ID_ANY, "Extra: ", size=(120, -1))
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chExtra)
		bsizer.Add(sz)
		bsizer.AddSpacer(20)
		self.Bind(wx.EVT_CHOICE, self.onChExtra, self.chExtra)
		
		bhsizer = wx.BoxSizer(wx.HORIZONTAL)
		bhsizer.AddSpacer(20)
		bhsizer.Add(bsizer)
		bhsizer.AddSpacer(20)
		boxTrain.SetSizer(bhsizer)
		
		vsizerl.Add(boxTrain)
		
		vsizerl.AddSpacer(20)

		boxEng = wx.StaticBox(self, wx.ID_ANY, "Engineer")
		topBorder = boxEng.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)
		bsizer.Add(wx.StaticText(boxEng, wx.ID_ANY, "", size=(240, -1)))

		self.chEngineer = wx.Choice(boxEng, wx.ID_ANY, choices=self.idleEngineers, size=(120, -1))
		self.chEngineer.SetSelection(0)
		self.selectedEngineer = self.chEngineer.GetString(0)
		self.Bind(wx.EVT_CHOICE, self.onChoiceEngineer, self.chEngineer)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(boxEng, wx.ID_ANY, "Engineer: ", size=(120, -1))
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chEngineer)
		
		self.bRmEng = wx.Button(boxEng, wx.ID_ANY, "-", size=(30, -1))
		self.Bind(wx.EVT_BUTTON, self.onRmEngineer, self.bRmEng)
		self.bRmEng.SetToolTip("Remove engineer from active list")
		sz.AddSpacer(5)
		sz.Add(self.bRmEng)
		bsizer.Add(sz)
		
		bsizer.AddSpacer(10)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		self.cbATC = wx.CheckBox(boxEng, wx.ID_ANY, "ATC")
		self.Bind(wx.EVT_CHECKBOX, self.onCbATC, self.cbATC)
		sz.AddSpacer(100)
		sz.Add(self.cbATC)
		bsizer.Add(sz)
		
		bsizer.AddSpacer(20)

		bhsizer = wx.BoxSizer(wx.HORIZONTAL)
		bhsizer.AddSpacer(20)
		bhsizer.Add(bsizer)
		bhsizer.AddSpacer(20)
		boxEng.SetSizer(bhsizer)
		
		vsizerl.Add(boxEng)

		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bAssign = wx.Button(self, wx.ID_ANY, "Assign\nTrain/Engineer", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bAssignPressed, self.bAssign)
		btnsizer.Add(self.bAssign)
		self.bAssign.Enable(len(self.idleEngineers) != 0 and len(self.pendingTrains) != 0)

		vsizerl.AddSpacer(20)
		vsizerl.Add(btnsizer, 1, wx.ALIGN_CENTER_HORIZONTAL)

		vsizerr = wx.BoxSizer(wx.VERTICAL)
		vsizerr.AddSpacer(10)
		
		self.teBreaker = wx.TextCtrl(self, wx.ID_ANY, "", size=(240, -1), style=wx.TE_CENTER)
		self.setBreakerValue("All OK")
		breakerFont = wx.Font(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		self.teBreaker.SetFont(breakerFont)
		self.teBreaker.SetForegroundColour(wx.Colour(255, 255, 255))

		self.clock = gizmos.LEDNumberCtrl(self, wx.ID_ANY, size=(160, 50), style=gizmos.LED_ALIGN_CENTER)  # @UndefinedVariable
		
		self.pngPSRY = wx.Image("PSLogo.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(self.pngPSRY, wx.BLUE)
		self.pngPSRY.SetMask(mask)
		b = wx.StaticBitmap(self, wx.ID_ANY, self.pngPSRY)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.teBreaker, 1, wx.TOP, 40)
		hsz.AddSpacer(40)
		hsz.Add(b)
		hsz.AddSpacer(40)
		hsz.Add(self.clock, 1, wx.TOP, 30)
		
		vsizerr.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizerr.AddSpacer(10)

		boxDetails = wx.StaticBox(self, wx.ID_ANY, "Train Details")
		topBorder = boxDetails.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)

		self.stDescription = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(400, -1))
		self.stDescription.SetFont(labelFontBold)
		bsizer.Add(self.stDescription)
		bsizer.AddSpacer(5)
		self.stStepTowers = []
		self.stStepLocs = []
		self.stStepStops = []
		for i in range(MAX_STEPS):
			tower = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(100, -1))
			loc = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(60, -1))
			stop = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(300, -1))
			if i % 2 == 0:
				tower.SetBackgroundColour(wx.Colour(225, 255, 240))
				loc.SetBackgroundColour(wx.Colour(225, 255, 240))
				stop.SetBackgroundColour(wx.Colour(225, 255, 240))
			else:
				tower.SetBackgroundColour(wx.Colour(138, 255, 197))
				loc.SetBackgroundColour(wx.Colour(138, 255, 197))
				stop.SetBackgroundColour(wx.Colour(138, 255, 197))
			tower.SetFont(textFontBold)
			loc.SetFont(textFont)
			stop.SetFont(textFont)
			sz = wx.BoxSizer(wx.HORIZONTAL)
			sz.Add(tower)
			sz.Add(loc)
			sz.Add(stop)
			self.stStepTowers.append(tower)
			self.stStepLocs.append(loc)
			self.stStepStops.append(stop)
			bsizer.Add(sz)
		
		self.stLocoInfo = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(600, -1))
		self.stLocoInfo.SetFont(labelFontBold)
		bsizer.AddSpacer(5)
		bsizer.Add(self.stLocoInfo)
		bsizer.AddSpacer(5)
		
		bhsizer = wx.BoxSizer(wx.HORIZONTAL)
		bhsizer.AddSpacer(20)
		bhsizer.Add(bsizer)
		bhsizer.AddSpacer(20)
		boxDetails.SetSizer(bhsizer)
		
		vsizerr.Add(boxDetails)
		vsizerr.AddSpacer(5)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizerl)
		hsizer.AddSpacer(40)
		hsizer.Add(vsizerr)
		hsizer.AddSpacer(20)
		
		wsizerl = wx.BoxSizer(wx.VERTICAL)
		wsizerl.Add(hsizer)
		wsizerl.AddSpacer(5)
		st = wx.StaticText(self, wx.ID_ANY, "Active Trains:")
		st.SetFont(labelFontBold)
		wsizerl.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		self.lcActiveTrains = ActiveTrainListCtrl(self)
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(self.lcActiveTrains)
		sz.AddSpacer(20)
		
		wsizerl.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		wsizerl.AddSpacer(20)
		
		wsizerr = wx.BoxSizer(wx.VERTICAL)
		
		wsizerr.AddSpacer(50)

		st = wx.StaticText(self, wx.ID_ANY, "Completed Trains:")
		st.SetFont(labelFontBold)
		wsizerr.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		self.completedTrainList = CompletedTrainList(self, self.completedTrains)
		wsizerr.Add(self.completedTrainList)
		
		wsizer = wx.BoxSizer(wx.HORIZONTAL)
		wsizer.Add(wsizerl)
		wsizer.Add(wsizerr)
		wsizer.AddSpacer(10)

		self.SetSizer(wsizer)
		self.Layout()
		self.Fit()

		# events from dispatcher		
		self.Bind(EVT_TRAINLOC, self.setTrainLocation)
		self.Bind(EVT_TRAINSIG, self.setTrainSignal)
		self.Bind(EVT_CLOCK, self.setClockEvent)
		self.Bind(EVT_BREAKER, self.setBreakersEvent)
		self.Bind(EVT_SOCKET_CONNECT, self.socketConnectEvent)
		self.Bind(EVT_SOCKET_DISCONNECT, self.socketDisconnectEvent)
		self.Bind(EVT_SOCKET_FAILURE, self.socketFailureEvent)
		self.Bind(EVT_MESSAGE, self.setMessageEvent)

		# events from DCC tracker
		self.Bind(EVT_DCCMESSAGE, self.onDCCMessage)
		self.Bind(EVT_DCCCLOSED,  self.onDCCClosed)
		self.Bind(EVT_DCCLOG,     self.onDCCLog)
		
		wx.CallAfter(self.initialize)
		
	def initialize(self):
		self.splash()
		
		self.settings = Settings(self, os.getcwd())
		self.atl.setTimingThresholds(unstarted=self.settings.unstartedthreshold, stopped=self.settings.stoppedthreshold)
		
		self.trainFile = self.settings.trainfile
		self.orderFile = self.settings.orderfile
		self.engineerFile = self.settings.engineerfile
		self.locoFile = self.settings.locofile
		
		self.completedTrains.clear()
		self.completedTrainList.update()

		self.loadLocoFile(os.path.join(self.settings.locodir, self.settings.locofile))		
		self.loadEngineerFile(os.path.join(self.settings.engineerdir, self.settings.engineerfile))
		self.loadTrainFile(os.path.join(self.settings.traindir, self.settings.trainfile))		
		self.loadOrderFile(os.path.join(self.settings.orderdir, self.settings.orderfile))
		self.parent.setTitle(train=self.trainFile, order=self.orderFile, engineer=self.engineerFile, loco=self.locoFile)
		
		self.report = Report(self, self.settings)
		if not self.report.Initialized():
			self.parent.disableReports()

		self.setBreakerValue("All OK")
		self.setClockValue("")
		self.setExtraTrains()
		self.parent.setTitle(connection="Not Connected", dcc="DCC Not Connected")
		
		self.atl.addDisplay("main", self.lcActiveTrains)

		self.setSessionSchedule(None)
		
		self.Bind(wx.EVT_TIMER, self.onTicker)
		self.ticker = wx.Timer(self)
		self.ticker.Start(1000)
		
	def onTicker(self, _):
		if self.splashTimer > 0:
			self.splashTimer -= 1
			if self.splashTimer == 0:
				try:
					self.dlgSplash.Destroy()
				except:
					pass
				
		if self.connected and self.deadmanTimer != 0:
			self.deadmanTimer -= 1
			if self.deadmanTimer == 0:
				dlg = wx.MessageDialog(self, 'The connection to the dispatcher appears to be closed.',
								'Dispatcher Session Error',
								wx.OK | wx.ICON_WARNING)
				dlg.ShowModal()
				dlg.Destroy()
				
		self.atl.ticker()
		
	def onResetSession(self, _):
		dlg = wx.MessageDialog(self, 'This will reload all data files and will delete all active trains\nAre you sure you want to proceed?\n\nPress "Yes" to proceed, or "No" to cancel.',
							'Reset Session', wx.YES_NO | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_YES:
			return

		self.idleEngineers = [t for t in self.selectedEngineers]
		self.updateEngQueue()
		self.completedTrains.clear()
		self.completedTrainList.update()
		self.log.append("Completed trains list cleared")
		self.loadLocoFile(os.path.join(self.settings.locodir, self.settings.locofile))		
		self.loadEngineerFile(os.path.join(self.settings.engineerdir, self.settings.engineerfile), preserveActive = True)
		self.loadTrainFile(os.path.join(self.settings.traindir, self.settings.trainfile))		
		self.loadOrderFile(os.path.join(self.settings.orderdir, self.settings.orderfile))
		self.sessionSchedule = []
		self.sessionFile = None
		self.setSessionSchedule(self.sessionFile)
		self.setExtraTrains()
		self.log.append("Session Reset")
		
	def connectToDispatch(self, _):
		self.parent.setTitle(connection="Connecting...")
		self.log.append("Connecting to dispatch at %s:%s" % (self.settings.dispatchip, self.settings.dispatchport))
		self.listener = Listener(self.settings.dispatchip, self.settings.dispatchport)
		self.listener.bind(self.socketConnect, self.socketDisconnect, self.connectFailure, self.trainReport, self.signalReport, self.setClock, self.setBreakers, self.setMessage)
		self.listener.start()
		
	def setConnected(self, flag=True):
		self.connected = flag
		self.deadmanTimer = DEADMANSET if flag else 0
		
	def socketConnect(self):  # thread context
		evt = SocketConnectEvent()
		wx.PostEvent(self, evt)

	def socketConnectEvent(self, _):
		self.parent.setTitle(connection="Connected")
		self.setConnected()
		self.setBreakerValue("")
		self.setClockValue("")
		self.log.append("Socket Connection successful")
		self.parent.enableListenerDisconnect(True)
		
	def socketDisconnect(self):  # thread context
		evt = SocketDisconnectEvent()
		wx.PostEvent(self, evt)

	def socketDisconnectEvent(self, _):
		self.parent.setTitle(connection="Disconnected")
		self.log.append("Socket disconnection complete")
		self.parent.enableListenerDisconnect(False)
		self.setConnected(False)
		self.setBreakerValue("")
		self.setClockValue("")
		self.listener = None
		
	def connectFailure(self):  # thread context
		evt = SocketFailureEvent()
		wx.PostEvent(self, evt)

	def socketFailureEvent(self, _):
		dlg = wx.MessageDialog(self, 'Connection to Dispatcher failed.\nNo locomotive or block information is available',
								'Connection Failed', wx.OK | wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()
		
		self.parent.setTitle(connection="Connection Failed")
		self.log.append("Error from socket connection request")
		self.listener = None
		self.setConnected(False)
		
	def disconnectFromDispatch(self, _):
		self.log.append("Starting socket disconnection request")
		self.listener.kill()
		
	def resetConnection(self, _):
		dlg = wx.MessageDialog(self, 'This will sever the connection to the dispatcher program\nand should only be used to recover from error situations.\n\nPress "Yes" to proceed, or "No" to cancel.',
								'Reset Dispatcher Connection', wx.YES_NO | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_YES:
			return

		if self.listener is not None:
			self.listener.kill(skipDisconnect=True)
			self.listener = None
		self.log.append("connection reset started")
		self.socketDisconnect()
		
	def setupIP(self, _):
		dlg = wx.TextEntryDialog(self, 'Enter/Modify IP Address', 'IP Address', self.settings.dispatchip)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			newIP = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		self.settings.dispatchip = newIP
		self.log.append("modified IP address to %s" % newIP)
		self.settings.setModified()
		
	def setupPort(self, _):
		dlg = wx.TextEntryDialog(self, 'Enter/Modify IP Port Number', 'Port Number', self.settings.dispatchport)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			newPort = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		self.settings.dispatchport = newPort
		self.settings.setModified()
		self.log.append("modified IP port to %s" % newPort)		
		
	def setupDCCtty(self, _):
		dlg = wx.TextEntryDialog(self, 'Enter/Modify COM port for DCC', 'COM Port', self.settings.dccsnifferport)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			newPort = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		self.settings.dccsnifferport = newPort
		self.log.append("modified DCC Port to %s" % newPort)
		self.settings.setModified()
		
	def setupDCCBaud(self, _):
		dlg = wx.TextEntryDialog(self, 'Enter/Modify DCC Sniffer Baud rate', 'Baud Rate', "%d" % self.settings.dccsnifferbaud)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			newBaud = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		self.settings.dccsnifferbaud = int(newBaud)
		self.settings.setModified()
		self.log.append("modified DCC Baud Rate to %d" % int(newBaud))
		
	def trainReport(self, train, loco, block):
		# This method executes in thread context - don't touch the wxpython elements here
		evt = TrainLocationEvent(train=train, loco=loco, block=block)
		wx.PostEvent(self, evt)
		
	def setTrainLocation(self, evt):
		tid = evt.train
		if tid == "":
			tid = None
		loco = evt.loco
		if loco == "":
			loco = None
		block = evt.block
		self.log.append("Train report: Train(%s) Loco(%s) Blk(%s)" % (tid, loco, block))

		if tid is None:
			if loco is not None:
				self.log.append("Trying to identify train by loco id")
				tid = self.roster.getTrainByLoco(loco)
						
		if tid is None:
			self.log.append("Unable to determine train ID")
			return 
		
		tInfo = self.roster.getTrain(tid)
		if tInfo is None:
			self.log.append("Ignoring train report for train (%s) - unknown train" % tid)
			return
		
		tInfo["block"] = block
		self.log.append("Setting block for train %s to %s" % (tid, block))
		desc = None
		if tInfo["loco"] is None:
			if loco is not None:
				tInfo["loco"] = loco
				desc = self.locos.getLoco(loco)
				self.log.append("Setting locomotive for train %s to %s" % (tid, loco))
			else:
				loco = ""
		else:
			loco = tInfo["loco"]

		self.atl.updateTrain(tid, loco, desc, block)
			
		if tid == self.selectedTrain:
			self.showInfo(self.selectedTrain)
			
	def signalReport(self, loco, limit):
		# This method executes in thread context - don't touch the wxpython elements here
		evt = TrainSignalEvent(loco=loco, limit=limit)
		wx.PostEvent(self, evt)

	def setTrainSignal(self, evt):
		loco = evt.loco
		if loco == "":
			return 
		
		limit = evt.limit
		
		self.log.append("Trying to identify train by loco id")
		tid = self.roster.getTrainByLoco(loco)
						
		if tid is None:
			self.log.append("Unable to determine train ID")
			return 

		self.atl.setLimit(loco, limit)

	def setClock(self, tm): # thread context
		evt = ClockEvent(tm=tm)
		wx.PostEvent(self, evt)
		
	def setClockEvent(self, evt):
		self.setClockValue(evt.tm)
		self.deadmanTimer = DEADMANSET
		
	def setClockValue(self, tm):
		if not self.connected:
			self.clock.SetValue("")
			self.clock.SetBackgroundColour(wx.Colour(255, 10, 10))
			return
		self.clock.SetBackgroundColour(wx.Colour(0, 0, 0))
		self.clock.SetValue(tm)
		
	def setMessage(self, txt): # thread context
		evt = MessageEvent(txt=txt)
		wx.PostEvent(self, evt)
		
	def setMessageEvent(self, evt):
		self.log.append("Message: %s" % evt.txt)
		
	def setBreakers(self, txt): # thread context
		evt = BreakerEvent(txt=txt)
		wx.PostEvent(self, evt)
		
	def setBreakersEvent(self, evt):
		self.log.append("Set breakers to :%s" % evt.txt)
		self.setBreakerValue(evt.txt)
		
	def setBreakerValue(self, txt):
		if not self.connected:
			self.teBreaker.SetValue("not connected")
			self.teBreaker.SetBackgroundColour(wx.Colour(255, 10, 10))
			return
			
		self.teBreaker.SetValue(txt)
		if txt == "All OK" or txt == "":
			self.teBreaker.SetBackgroundColour(wx.Colour(10, 158, 32))
		else:
			self.teBreaker.SetBackgroundColour(wx.Colour(241, 41, 47))

	def loadTrainRoster(self, fn):
		self.log.append("loading train file (%s)" % fn)

		try:
			roster = TrainRoster(fn)
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, 'Unable to open Train roster file %s' % fn,
				'File Not Found',
				wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

			roster = None
		return roster

	def loadTrainFile(self, fn):
		self.roster = self.loadTrainRoster(fn)
		self.parent.setTitle(train=os.path.basename(fn))
		engRunning = [x for x in self.atl.getEngineers() if x not in self.idleEngineers]
		self.idleEngineers += engRunning 
		self.chEngineer.SetItems(self.idleEngineers)
		if len(self.idleEngineers) > 0:
			self.chEngineer.SetSelection(0)
		self.chEngineer.Enable(len(self.idleEngineers) > 0)
		self.bRmEng.Enable(len(self.idleEngineers) > 0)
		
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.idleEngineers) > 0)
		self.bSkip.Enable(len(self.pendingTrains) > 0)

		self.atl.clear()

		self.cbATC.SetValue(False)

		self.chTrain.SetItems(self.pendingTrains)
		self.chTrain.Enable(len(self.pendingTrains) > 0)
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.idleEngineers) > 0)
		
		if len(self.pendingTrains) > 0:
			self.chTrain.SetSelection(0)
			tid = self.chTrain.GetString(0)
		else:
			self.chTrain.SetSelection(wx.NOT_FOUND)
			tid = None
			
		self.setSelectedTrain(tid)
		
	def onViewEngQueue(self, _):
		if self.dlgEngQueue is None:
			self.dlgEngQueue = EngQueueDlg(self, self.idleEngineers, self.onCloseEngQueue)
			self.dlgEngQueue.Show()
		else:
			self.dlgEngQueue.Raise()
			
	def onCloseEngQueue(self):
		if self.dlgEngQueue is None:
			return
		
		self.dlgEngQueue.Destroy()
		self.dlgEngQueue = None
		
	def updateEngQueue(self):
		if self.dlgEngQueue is None:
			return
		
		self.dlgEngQueue.updateEngQueue(self.idleEngineers)
		
	def onViewActiveTrains(self, _):
		if self.dlgActiveTrains is None:
			self.dlgActiveTrains = ActiveTrainListDlg(self, self.atl, self.onCloseActiveTrains)
			self.dlgActiveTrains.Show()
		else:
			self.dlgActiveTrains.Raise()
			
	def onCloseActiveTrains(self):
		if self.dlgActiveTrains is None:
			return
		
		self.dlgActiveTrains.Destroy()
		self.dlgActiveTrains = None

	def onViewHiLite(self, _):
		if self.parent.menuView.FindItemById(MENU_VIEW_SHOWATTENTION).IsChecked():
			self.lcActiveTrains.setShowAttention(True)
		else:
			self.lcActiveTrains.setShowAttention(False)

	def onViewLegend(self, _):
		if self.dlgLegend is None:
			self.dlgLegend = LegendDlg(self, self.onLegendDlgClose)
			self.dlgLegend.Show();
		else:
			self.dlgLegend.Raise()

	def onLegendDlgClose(self):
		self.dlgLegend = None
	
	def setExtraTrains(self):
		extraPool = [ t for t in self.trainOrder.getExtras() if t not in self.sessionSchedule ]
		if self.trainOrder is None:
			self.extraTrains = []
		elif self.settings.allowextrarerun:		
			self.extraTrains = [t for t in extraPool if not self.atl.hasTrain(t)]
		else:
			self.extraTrains = [t for t in extraPool if not self.atl.hasTrain(t) and t not in self.completedTrains]
			
		self.log.append("Setting extra train list to %s" % str(self.extraTrains))

		self.chExtra.SetItems(self.extraTrains)
		if len(self.extraTrains) > 0:
			self.chExtra.SetSelection(0)
			
		self.cbExtra.SetValue(False)			
		self.cbExtra.Enable(len(self.extraTrains) > 0)
		self.chExtra.Enable(False)
		
	def onCbExtra(self, _):
		self.enableExtraMode(self.cbExtra.IsChecked())
			
	def enableExtraMode(self, flag=True):
		if flag:
			self.chExtra.Enable(True)
			tx = self.chExtra.GetSelection()
			tid = self.chExtra.GetString(tx)
			self.setSelectedTrain(tid)
			self.chTrain.Enable(False)
			self.bSkip.Enable(False)
			self.bAssign.Enable(len(self.idleEngineers) > 0 or self.cbATC.IsChecked())
		else:
			self.chExtra.Enable(False)
			self.chTrain.Enable(True)
			tx = self.chTrain.GetSelection()
			tid = self.chTrain.GetString(tx)
			self.setSelectedTrain(tid)
			self.bSkip.Enable(len(self.pendingTrains) > 0)
			self.cbExtra.SetValue(False)
			if len(self.pendingTrains) > 0 and (len(self.idleEngineers) > 0 or self.cbATC.IsChecked()):
				self.bAssign.Enable(True)
			else:
				self.bAssign.Enable(False)
					
	def loadLocoFile(self, fn):
		self.log.append("Loading locomotive file (%s)" % fn)
		self.parent.setTitle(loco=os.path.basename(fn))
		try:
			self.locos = Locomotives(fn)
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, 'Unable to open Locomotives file %s' % fn,
					'File Not Found', wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

			self.locos = None
		self.updateActiveListLocos()
		
	def updateActiveListLocos(self):
		if self.locos is None:
			return
		
		actTrains = self.atl.getTrains()
		locos = self.locos.getLocoList()
		for tid in actTrains:
			at = self.atl.getTrainByTid(tid)
			tInfo = self.roster.getTrain(tid)
			if at is not None:
				rloco = tInfo["loco"]
				if rloco not in locos:
					ndesc = ""
				else:
					ndesc = self.locos.getLoco(rloco)

				self.atl.updateTrain(tid, rloco, ndesc, tInfo["block"])

	def loadEngineerFile(self, fn, preserveActive=False):
		self.log.append("loading engineer file (%s)" % fn)
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
			
		if not preserveActive:
			self.idleEngineers = []
			self.updateEngQueue()
			
		self.selectedEngineers = [x for x in self.idleEngineers]
		self.chEngineer.SetItems(self.idleEngineers)
		self.chEngineer.Enable(len(self.idleEngineers) > 0)
		self.bRmEng.Enable(len(self.idleEngineers) > 0)

		self.atl.clear()

		self.cbATC.SetValue(False)
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.idleEngineers) > 0)
		
		if len(self.idleEngineers) > 0:
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)
		else:
			self.chEngineer.SetSelection(wx.NOT_FOUND)
			self.selectedEngineer = None
			
	def loadOrderFile(self, fn):
		self.log.append("loading train order file (%s)" % fn)
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
				
	def setTrainOrder(self, preserveActive=False):
		self.log.append("Setting train order to %s" % str(self.pendingTrains))
		self.chTrain.SetItems(self.pendingTrains)
		if len(self.pendingTrains) > 0:
			self.setSelectedTrain(self.chTrain.GetString(0))

		if not preserveActive:
			engRunning = [x for x in self.atl.getEngineers() if x not in self.idleEngineers]
			self.idleEngineers += engRunning 
		self.chEngineer.SetItems(self.idleEngineers)
		if len(self.idleEngineers) > 0:
			self.chEngineer.SetSelection(0)
		self.chEngineer.Enable(len(self.idleEngineers) > 0)
		self.bRmEng.Enable(len(self.idleEngineers) > 0)
			
		self.chTrain.Enable(len(self.pendingTrains) > 0)
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.idleEngineers) > 0)
		self.bSkip.Enable(len(self.pendingTrains) > 0)

		if not preserveActive:
			self.atl.clear()
			
		self.cbATC.SetValue(False)
		
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
			return
		
		path = dlg.GetPath()
		dlg.Destroy()
	
		self.settings.logdir = os.path.split(path)[0]
		self.settings.setModified()

		try:
			self.log.saveAs(path)
		except:
			dlg = wx.MessageDialog(self, "Unable to write to log file: %s" % path,
								'Error saving log',
								wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
		
	def onCbATC(self, _):
		if self.cbATC.IsChecked():
			self.bAssign.Enable(len(self.pendingTrains) > 0 or self.cbExtra.IsChecked())
		else:
			self.bAssign.Enable(len(self.idleEngineers) > 0 and (len(self.pendingTrains) > 0 or self.cbExtra.IsChecked()))
		
	def onRmEngineer(self, _):
		dlg = wx.MessageDialog(self, "This will remove engineer '%s' from the active list.\nPress \"Yes\" to proceed, or \"No\" to cancel." % self.selectedEngineer,
							'Remove Engineer',
							wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
			
		if rc != wx.ID_YES:
			return
		
		self.log.append("Removed engineer %s from active list" % self.selectedEngineer)
		self.idleEngineers.remove(self.selectedEngineer)
		self.updateEngQueue()
		self.selectedEngineers.remove(self.selectedEngineer)
		self.chEngineer.SetItems(self.idleEngineers)
		if len(self.idleEngineers) == 0:
			self.chEngineer.Enable(False)
			self.bRmEng.Enable(False)
			self.bAssign.Enable(False)
		else:
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)
			self.bRmEng.Enable(True)
		
	def bAssignPressed(self, _):
		if self.cbExtra.IsChecked():
			tx = self.chExtra.GetSelection()
			tid = self.chExtra.GetString(tx)
			tInfo = self.roster.getTrain(tid)
			runningExtra = True
		else:
			tid = self.selectedTrain
			tInfo = self.roster.getTrain(self.selectedTrain)
			runningExtra = False
			
		if tInfo is None:
			return
		
		if self.cbATC.IsChecked():
			eng = "ATC"
		else:
			eng = self.selectedEngineer
			
		dlg = wx.MessageDialog(self, "This will assign engineer %s to train %s.\nPress \"Yes\" to proceed, or \"No\" to cancel." % (eng, tid),
							'Train/Engineer Assign',
							wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
			
		if rc != wx.ID_YES:
			return

		if tInfo["loco"] is None:
			loco = ""
			ldesc = ""
		else:
			loco = tInfo["loco"]
			ldesc = self.locos.getLoco(loco)
			if ldesc is None:
				ldesc = ""
				
		if "block" in tInfo:
			block = tInfo["block"]
		else:
			block = ""	

		self.atl.addTrain(ActiveTrain(tid, tInfo, loco, ldesc, eng, block))

		if loco in self.speeds:
			self.atl.setThrottle(loco, self.speeds[loco][0], self.speeds[loco][1])
			
		self.log.append("Assigned %strain %s to %s" % ("extra " if runningExtra else "", tid, eng))

		if not runningExtra:		
			self.pendingTrains.remove(tid)
			self.chTrain.SetItems(self.pendingTrains)
			if len(self.pendingTrains) == 0:
				self.chTrain.Enable(False)
				self.bAssign.Enable(False)
				self.bSkip.Enable(False)
				self.showInfo(None)
				self.setSelectedTrain(None)
			else:
				self.chTrain.SetSelection(0)
				self.setSelectedTrain(self.chTrain.GetString(0))
		else:
			self.setExtraTrains()
			self.enableExtraMode(False)
		
		if not self.cbATC.IsChecked():
			self.idleEngineers.remove(self.selectedEngineer)
			self.updateEngQueue()
			self.chEngineer.SetItems(self.idleEngineers)
			if len(self.idleEngineers) == 0:
				self.chEngineer.Enable(False)
				self.bRmEng.Enable(False)
				self.bAssign.Enable(False)
			else:
				self.chEngineer.SetSelection(0)
				self.selectedEngineer = self.chEngineer.GetString(0)
				self.bRmEng.Enable(True)
				
		else:
			self.cbATC.SetValue(False)
			self.bAssign.Enable(len(self.pendingTrains) != 0 and len(self.idleEngineers) != 0)
		
	def reassignTrain(self, tx):
		at = self.atl.getTrainByPosition(tx)
		if at is None:
			return

		engActive = self.atl.getEngineers()	
		if at.engineer != "ATC":
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
		
		if at.engineer in self.selectedEngineers:
			if at.engineer not in self.idleEngineers:
				self.idleEngineers.append(at.engineer)
				self.updateEngQueue()
			self.chEngineer.Enable(True)
			self.bRmEng.Enable(True)
			self.chEngineer.SetItems(self.idleEngineers)
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)

		if neng in self.idleEngineers:
			self.idleEngineers.remove(neng)
			self.updateEngQueue()
			self.chEngineer.SetItems(self.idleEngineers)
			if len(self.idleEngineers) == 0:
				self.chEngineer.Enable(False)
				self.bRmEng.Enable(False)
			else:
				self.chEngineer.SetSelection(0)
				self.selectedEngineer = self.chEngineer.GetString(0)
				self.chEngineer.Enable(True)
				self.bRmEng.Enable(True)

		if len(self.pendingTrains) > 0 and (len(self.idleEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)

		oeng = at.engineer	
		tid = at.tid	
		self.atl.setNewEngineer(tid, neng)
		self.log.append("Reassigned train %s from %s to %s" % (tid, oeng, neng))
		
	def onAbout(self, _):
		dlg = AboutDlg(self, self.pngPSRY, VERSIONDATE)
		dlg.ShowModal()
		dlg.Destroy()
		
	def splash(self):
		self.dlgSplash = AboutDlg(self, self.pngPSRY, VERSIONDATE)
		self.dlgSplash.CenterOnScreen()
		self.dlgSplash.Show()
		self.splashTimer = 5;
		
	def showDetails(self, tx):
		at = self.atl.getTrainByPosition(tx)
		if at is None:
			return
		
		tinfo = self.roster.getTrain(at.tid)
		
		lid = at.loco
		if lid is None or lid == "":
			desc = ""
		else:
			desc = self.locos.getLoco(lid)
			
		dlg = DetailsDlg(self, at.tid, tinfo, desc, at.engineer)
		dlg.Show()
		
	def bSkipPressed(self, _):	
		tInfo = self.roster.getTrain(self.selectedTrain)
		if tInfo is None:
			return

		dlg = wx.MessageDialog(self, "This removes train %s from the schedule\nPress OK to continue, or Cancel" % self.selectedTrain,
							'Skip Train', wx.OK | wx.CANCEL | wx.OK_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_CANCEL:
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

	def onChangeSort(self, evt):
		self.assertSortOrder()
		
	def assertSortOrder(self):
		if self.parent.menuSort.FindItemById(MENU_SORT_TID).IsChecked():
			sortKey = "tid"
		else:
			sortKey = "time"

		grp = self.parent.menuSort.FindItemById(MENU_SORT_GROUP).IsChecked()
		asc = self.parent.menuSort.FindItemById(MENU_SORT_ASCENDING).IsChecked()
		
		self.atl.setSortKey(sortKey, groupDir=grp, ascending=asc)

	def returnActiveTrain(self, tx):
		at = self.atl.getTrainByPosition(tx)
		if at is None:
			return
		isExtra = self.trainOrder.isExtraTrain(at.tid) and at.tid not in self.sessionSchedule
		if isExtra:		
			phrase  = "list of extra trains."	
		else:
			phrase = "top of the schedule."
			
		dlg = wx.MessageDialog(self, "This removes train %s (and its engineer) from the\nactive list, and places it back on the %s\nThis cannot be undone.\n\nPress OK to continue, or Cancel" % (at.tid, phrase),
							'Return Train', wx.OK | wx.CANCEL | wx.OK_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_CANCEL:
			return

		self.atl.delTrain(tx)

		if isExtra:
			self.log.append("Returned train %s from active list to extra train list" % at.tid)
			self.setExtraTrains()
		else:
			self.log.append("Returned train %s from active list to scheduled train list" % at.tid)
			self.pendingTrains = [at.tid] + self.pendingTrains
			self.chTrain.SetItems(self.pendingTrains)

			self.chTrain.SetSelection(0)
			self.setSelectedTrain(self.chTrain.GetString(0))

		if at.engineer in self.selectedEngineers:
			self.log.append("Returned engineer %s to head of pool" % at.engineer)
			if at.engineer not in self.idleEngineers:
				self.idleEngineers = [at.engineer] + self.idleEngineers
				self.updateEngQueue()
			self.chEngineer.Enable(True)
			self.bRmEng.Enable(True)
			self.chEngineer.SetItems(self.idleEngineers)
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)
			
		self.chTrain.Enable(len(self.pendingTrains) > 0)
			
		if len(self.pendingTrains) > 0 and (len(self.idleEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)
		
	def removeActiveTrain(self, tx):
		at = self.atl.getTrainByPosition(tx)
		if at is None:
			return
		
		dlg = wx.MessageDialog(self, "This indicates that train %s has reached its destination.\nThis cannot be undone.\n\nPress OK to continue, or Cancel" % at.tid,
							'Remove Train', wx.OK | wx.CANCEL | wx.OK_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_CANCEL:
			return

		mins = int(at.time / 60)
		secs = at.time % 60
		runtime = "%2d:%02d" % (mins, secs)
		self.log.append("Removed train %s from active list.  Run time %s" % (at.tid, runtime))
		self.completedTrains.append(at.tid, at.engineer, at.loco)
		self.completedTrainList.update()
		self.log.append("Train %s added to Completed trains list" % at.tid)
		self.atl.delTrain(tx)
		
		isExtra = self.trainOrder.isExtraTrain(at.tid) and at.tid not in self.sessionSchedule
		if self.settings.allowextrarerun and isExtra:
			self.setExtraTrains()
		
		if at.engineer in self.selectedEngineers:
			self.log.append("Returned engineer %s to pool" % at.engineer)
			if at.engineer not in self.idleEngineers:
				self.idleEngineers.append(at.engineer)
				self.updateEngQueue()
			self.chEngineer.Enable(True)
			self.bRmEng.Enable(True)
			self.chEngineer.SetItems(self.idleEngineers)
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)
			
		if len(self.pendingTrains) > 0 and (len(self.idleEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)
		
	def changeLoco(self, tx):
		at = self.atl.getTrainByPosition(tx)
		if at is None:
			return

		dlg = wx.SingleChoiceDialog(
				self, 'Choose a Locomotive', 'Change Locomotive',
				self.locos.getLocoListFull(),
				wx.CHOICEDLG_STYLE
				)

		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			loco = dlg.GetStringSelection()
			lid = loco.split(" ")[0]

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		desc = self.locos.getLoco(lid)
		self.atl.updateTrain(at.tid, lid, desc, None)
		
		if lid in self.speeds:
			self.atl.setThrottle(lid, self.speeds[lid][0], self.speeds[lid][1])
		
		tinfo = self.roster.getTrain(at.tid)
		if tinfo is not None:
			tinfo["loco"] = lid
		self.log.append("Train %s: changed loco to %s" % (at.tid, lid))
		
	def onChoiceTID(self, _):
		tx = self.chTrain.GetSelection()
		if tx == wx.NOT_FOUND:
			return
		
		tid = self.chTrain.GetString(tx)
		self.setSelectedTrain(tid)
		
	def onChExtra(self, _):
		tx = self.chExtra.GetSelection()
		if tx == wx.NOT_FOUND:
			return
		
		tid = self.chExtra.GetString(tx)
		self.setSelectedTrain(tid)
		
	def reportSelection(self, tx):
		pass
		
	def reportDoubleClick(self, tx):
		self.reportSelection(tx)
		self.showDetails(tx)
		
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
			for i in range(MAX_STEPS):
				self.stStepTowers[i].SetLabel("")
				self.stStepLocs[i].SetLabel("")
				self.stStepStops[i].SetLabel("")
			self.stDescription.SetLabel("")
			return
		
		if self.roster is None:
			for i in range(MAX_STEPS):
				self.stStepTowers[i].SetLabel("")
				self.stStepLocs[i].SetLabel("")
				self.stStepStops[i].SetLabel("")
			self.stDescription.SetLabel("Train Roster is empty")
			return
		else:
			tInfo = self.roster.getTrain(tid)
			
		if tInfo is None:
			self.stDescription.SetLabel("Train %s is not in Train Roster" % tid)
			for i in range(MAX_STEPS):
				self.stStepTowers[i].SetLabel("")
				self.stStepLocs[i].SetLabel("")
				self.stStepStops[i].SetLabel("")
			return

		descr = "%s   %sbound %s" % (tid, tInfo["dir"], tInfo["desc"])	
		if tInfo["cutoff"]:
			descr += " (via cutoff)"	
		self.stDescription.SetLabel(descr)
		i = 0
		for step in tInfo["steps"]:
			self.stStepTowers[i].SetLabel(step[0])
			self.stStepStops[i].SetLabel(step[1])
			if step[2] == 0:
				self.stStepLocs[i].SetLabel("")
			else:
				self.stStepLocs[i].SetLabel("(%2d)" % step[2])
			i += 1
			
		while i < MAX_STEPS:
			self.stStepTowers[i].SetLabel("")
			self.stStepLocs[i].SetLabel("")
			self.stStepStops[i].SetLabel("")
			i += 1
		
		if tInfo["loco"] is None:
			locoString = ""
		else:
			lId = tInfo["loco"]
			lInfo = self.locos.getLoco(lId)
			if lInfo is None:
				locoString = "Loco: %s" % lId
			else:
				locoString = "Loco: %s - %s" % (lId, lInfo.replace('&', '&&'))

		if tInfo["block"] is None or tInfo["block"] == "":
			self.stLocoInfo.SetLabel("%-50.50s" % locoString)
		else:
			blockString = "Block: %s" % tInfo["block"]	
			self.stLocoInfo.SetLabel("%-40.40s %s" % (locoString, blockString))
						
				
	def onManageOrder(self, _):
		dlg = ManageOrderDlg(self, self.trainOrder, self.roster.getTrainList(), self.settings)
		rc = dlg.ShowModal()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return

		self.parent.setTitle(order=self.settings.orderfile)
		fn = os.path.join(self.settings.orderdir, self.settings.orderfile)
		self.trainOrder = Order(fn)

		norder = self.trainOrder.getOrder()
		nextra = self.trainOrder.getExtras()
		
		self.log.append("Modified full train order to %s" % str(norder))
		self.log.append("Modified extra trains to %s" % str(nextra))
		
		self.pendingTrains = [t for t in norder if not self.atl.hasTrain(t) and t not in self.completedTrains]
		self.sessionSchedule = []
		self.sessionFile = None
		self.setSessionSchedule(self.sessionFile)
		self.log.append("Pending trains = %s" % str(self.pendingTrains))
		self.extraTrains = sorted([t for t in nextra])
		self.setTrainOrder(preserveActive=True)
		self.setExtraTrains()

	def onManageTrains(self, _):
		dlg = ManageTrainsDlg(self, self.roster, self.locos, self.settings)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		
		# no need to retrieve dialog values because the data is saved automatically when OK is pressed
		# just re-read the file
		self.parent.setTitle(train=self.settings.trainfile)
		self.loadTrainFile(os.path.join(self.settings.traindir, self.settings.trainfile))
		self.setExtraTrains()
		
	def onManageEngineers(self, _):
		busyEngineers = [x for x in self.atl.getEngineers() if x in self.selectedEngineers]
		availableEngineers = [x for x in list(self.engineers) if x not in busyEngineers]
		dlg = ManageEngineersDlg(self, availableEngineers, self.idleEngineers, busyEngineers, self.settings)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			newSelEngs, allEngs = dlg.getValues()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		fn = os.path.join(self.settings.engineerdir, self.settings.engineerfile)

		self.log.append("loading engineer file (%s)" % fn)
		try:
			self.engineers = Engineers(fn)
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, 'Unable to open Engineer file %s' % fn,
					'File Not Found',
					wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

			self.engineers = None
			return
		
		for eng in self.engineers:
			if not eng in allEngs:
				self.engineers.delete(eng)

		for eng in allEngs:
			if not self.engineers.contains(eng):
				self.engineers.add(eng)

		self.log.append("New Engineer list: %s" % str(newSelEngs))
		self.log.append("Currently assigned engineers = %s" % str(busyEngineers))
		self.parent.setTitle(engineer=self.settings.engineerfile)
		self.idleEngineers = newSelEngs	
		self.updateEngQueue()	
		self.chEngineer.SetItems(self.idleEngineers)
		self.chEngineer.Enable(len(self.idleEngineers) > 0)
		self.bRmEng.Enable(len(self.idleEngineers) > 0)
		if len(self.pendingTrains) > 0 and (len(self.idleEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)
		self.chEngineer.SetSelection(0)
		self.selectedEngineer = self.chEngineer.GetString(0)
		
		self.selectedEngineers = [x for x in self.idleEngineers] + [x for x in busyEngineers if x in allEngs]
		
	def onManageLocos(self, _):
		dlg = ManageLocosDlg(self, self.locos, self.settings)
		rc = dlg.ShowModal()
			
		dlg.Destroy()
				
		if rc != wx.ID_OK:
			return
		
		self.parent.setTitle(loco=self.settings.locofile)
		path = os.path.join(self.settings.locodir, self.settings.locofile)
		self.locos = Locomotives(path)
			
		self.showInfo(self.selectedTrain)
		self.updateActiveListLocos()
		
	def onManageOptions(self, _):
		dlg = OptionsDlg(self, self.settings)
		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			fSaveLog, fRerunExtra = dlg.getValues()
		
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return 
		
		if fSaveLog is not None:
			self.settings.savelogonexit = fSaveLog
			self.log.append("Changed option SaveLogOnExit to %s" % str(fSaveLog))
			self.settings.setModified()
			
		if fRerunExtra is not None:
			self.settings.allowextrarerun = fRerunExtra
			self.log.append("Changed option AllowExtraRerun to %s" % str(fRerunExtra))
			self.settings.setModified()
			self.setExtraTrains()
		
	def onAssignLocos(self, _):
		order = [x for x in self.trainOrder]
		dlg = AssignLocosDlg(self, self.roster, order, self.extraTrains, self.locos)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			result = dlg.getValues()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		for tid in list(self.trainOrder) + self.extraTrains:
			tinfo = self.roster.getTrain(tid)
			if tinfo["loco"] != result[tid]:
				self.log.append("Assigned loco %s to train %s (old value %s)" % (result[tid], tid, tinfo["loco"]))
				tinfo["loco"] = result[tid]
					
		self.showInfo(self.selectedTrain)
		self.updateActiveListLocos()
		self.roster.save()

	def setSessionSchedule(self, fn):
		if fn is None:
			txt = "(base)"
		else:
			txt = "(%s)" % fn
		self.stSessionSchedule.SetLabel(txt)

	def onManageSessionSchedule(self, _):
		dlg = SessionScheduleDlg(self, self.trainOrder, self.sessionFile, self.sessionSchedule)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			fn, sch = dlg.getResults()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		self.sessionSchedule = sch
		self.sessionFile = fn
		self.setSessionSchedule(self.sessionFile)
		self.pendingTrains = [t for t in self.sessionSchedule]
		self.chTrain.SetItems(self.pendingTrains)
		self.setExtraTrains()
		if len(self.pendingTrains) == 0:
			self.chTrain.Enable(False)
			self.bAssign.Enable(False)
			self.bSkip.Enable(False)
			self.showInfo(None)
		else:
			self.chTrain.SetSelection(0)
			self.setSelectedTrain(self.chTrain.GetString(0))
			self.chTrain.Enable(True)
			self.bAssign.Enable(True)
			self.bSkip.Enable(True)

	def onReportOpWorksheet(self, _):
		self.report.OpWorksheetReport(self.roster, self.trainOrder, self.sessionSchedule, self.locos)
		
	def onReportLocos(self, _):
		self.report.LocosReport(self.locos)
		
	def onReportStatus(self, _):
		self.report.StatusReport(self.atl, self.completedTrains)
			
	def onReportTrainCards(self, _):
		self.report.TrainCards(self.roster, self.extraTrains, self.trainOrder)
		
	def onSaveData(self, _):
		saveData(self, self.settings)
		
	def onRestoreData(self, _):
		restoreData(self, self.settings)
		
	def onConnectSnifferPressed(self, _):
		self.connectSniffer()

	def connectSniffer(self):		
		self.sniffer = DCCSniffer()
		self.sniffer.bind(self.DCCMessage, self.DCCClosed, self.DCCLog)

		try:
			self.sniffer.connect(self.settings.dccsnifferport, self.settings.dccsnifferbaud, 1)
		except SerialException:
			dlg = wx.MessageDialog(self, 'Connection to DCC Sniffer on port ' + self.settings.dccsnifferport + ' failed',
					'Connection Failed',
					wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			self.sniffer = None
			
		self.enableDCCDisconnect(self.sniffer is not None)
		if self.sniffer:
			self.parent.setTitle(dcc="DCC Connected(%s)" % self.settings.dccsnifferport)
			self.log.append("Connection to DCC sniffer successful on port %s" % self.settings.dccsnifferport)
		else:
			self.parent.setTitle(dcc="DCC Not Connected")
			self.log.append("Connection to DCC sniffer failed on port %s" % self.settings.dccsnifferport)

	def onDisconnectSnifferPressed(self, _):
		self.disconnectSniffer()
		
	def disconnectSniffer(self):
		if self.sniffer is None:
			return
		
		try:
			self.sniffer.kill()
			self.sniffer.join()	
		except:
			pass
		
		self.sniffer = None
		self.enableDCCDisconnect(False)
		self.log.append("DCC sniffer disconnected")
		self.parent.setTitle(dcc="DCC Not Connected")
		
	def enableDCCDisconnect(self, flag=True):
		self.parent.menuDCC.Enable(MENU_DCC_DISCONNECT, flag)
		self.parent.menuDCC.Enable(MENU_DCC_CONNECT, not flag)

			
	def DCCMessage(self, txt): # thread context
		try:
			dccMsg = {
				"instr": txt[0],
				"loco": "%d" % int(txt[1]), # strip off any leading zeroes
				"param": txt[2]
			}
		except:
			evt = DCCLogEvent(msg="Unable to parse DCC message (%s)" % str(txt))
			wx.PostEvent(self, evt)
		else:		
			evt = DCCMessageEvent(dcc=dccMsg)
			wx.PostEvent(self, evt)
		
	def onDCCMessage(self, evt):
		dccMsg = evt.dcc
		cmd = dccMsg["instr"]
		if cmd in ["F", "f", "R", "r", "s", "e"]:
			if cmd == "F":
				speedType = FWD_128
			elif cmd == "f":
				speedType = FWD_28
			elif cmd == "R":
				speedType = REV_128
			elif cmd == "r":
				speedType = REV_28
			else:
				speedType = STOP

			try:
				speed = int(dccMsg["param"])
			except:
				speed = None
				
			if speed is not None:
				self.speeds[dccMsg["loco"]] = [speed, speedType]
				self.atl.setThrottle(dccMsg["loco"], speed, speedType)
		
	def DCCClosed(self): # thread context
		evt = DCCClosedEvent()
		wx.PostEvent(self, evt)
		
	def onDCCClosed(self, evt):
		self.disconnectSniffer()
		
	def DCCLog(self, txt): # thread context
		evt = DCCLogEvent(msg=txt)
		wx.PostEvent(self, evt)
		
	def onDCCLog(self, evt):
		logMsg = evt.msg
		self.log.append(logMsg)
			
	def onClose(self, _):
		if self.atl.count() > 0:
			dlg = wx.MessageDialog(self, 'Trains are still active.\nPress "Yes" to exit program, or "No" to cancel.',
						'Active Trains',
						wx.YES_NO | wx.ICON_QUESTION)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		self.ticker.Stop()
			
		if self.dlgEngQueue is not None:
			self.dlgEngQueue.Destroy()
			
		if self.dlgActiveTrains is not None:
			self.dlgActiveTrains.Destroy()
			
		if self.listener is not None:
			self.listener.kill()
			
		self.disconnectSniffer()
			
		self.settings.save()
		if self.settings.savelogonexit:
			path = os.path.join(self.settings.logdir, "tracker.log")
			try:
				self.log.saveAs(path)
			except:
				print("Unable to save to log file: %s" % path)
				
		self.Destroy()

class LegendDlg(wx.Dialog):
	def __init__(self, parent, cbClose):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Legend", style=wx.DEFAULT_DIALOG_STYLE | wx.DIALOG_NO_PARENT |wx.STAY_ON_TOP)

		self.cbClose = cbClose
		self.Bind(wx.EVT_CLOSE, self.onClose)

		self.loadImages()		
		self.il = wx.ImageList(16, 16)
		empty = self.makeBlank()
		self.idxEmpty = self.il.Add(empty)
		self.idxRed = self.il.Add(self.imageRed)
		self.idxGreen = self.il.Add(self.imageGreen)
		self.idxYellow = self.il.Add(self.imageYellow)
		self.idxStopped = self.il.Add(self.imageStopped)
		self.idxNotStarted = self.il.Add(self.imageNotStarted)
		text = [
			[ self.idxGreen,      "Train is operating at correct speed or lower" ],
			[ self.idxYellow,     "Train is moving, Signal speed limit is unknown" ],
			[ self.idxRed,        "Train is traveling too fast for current signal" ],
			[ self.idxStopped,    "Train is stopped" ],
			[ self.idxNotStarted, "Train has not started since being assigned" ]
		]

		textFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		self.lcLegend = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.BORDER_NONE)
		self.lcLegend.SetFont(textFont)
		self.lcLegend.InsertColumn(0, "")

		self.lcLegend.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		for i in range(5):
			self.lcLegend.InsertItem(i*2, text[i][1], text[i][0])

		self.lcLegend.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		
		vsz = wx.BoxSizer(wx.VERTICAL)	
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(300)
		vsz.Add(hsz)	
		vsz.AddSpacer(20)

		vsz.Add(self.lcLegend, 0, wx.EXPAND)
		
		vsz.AddSpacer(20)		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)
		
		self.SetSizer(hsz)
		self.Layout()
		self.Fit();

	def onClose(self, _):
		if callable(self.cbClose):
			self.cbClose()	
		self.Destroy()	

	def loadImages(self):
		png = wx.Image("trainRed.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageRed = png
		png = wx.Image("trainGreen.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageGreen = png
		png = wx.Image("trainYellow.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageYellow = png
		png = wx.Image("trainStopped.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageStopped = png
		png = wx.Image("trainNotStarted.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageNotStarted = png

	def makeBlank(self):
		empty = wx.Bitmap(16,16,32)
		dc = wx.MemoryDC(empty)
		dc.SetBackground(wx.Brush((0,0,0,0)))
		dc.Clear()
		del dc
		empty.SetMaskColour((0,0,0))
		return empty


class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		if not DEVELOPMODE:
			self.frame.Maximize(True)
			
		self.SetTopWindow(self.frame)
		return True

import sys

ofp = open("tracker.out", "w")
efp = open("tracker.err", "w")

if not DEVELOPMODE:
	sys.stdout = ofp
	sys.stderr = efp

app = App(False)
app.MainLoop()

ofp.close()
efp.close()
