import os
import wx
import wx.lib.gizmos as gizmos

from wx.lib import newevent

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
from listener import Listener

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
MENU_MANAGE_ASSIGN_LOCOS = 203
MENU_MANAGE_LOCOS = 204
MENU_MANAGE_ORDER = 205
MENU_REPORT_OP_WORKSHEET = 301
MENU_REPORT_TRAIN_CARDS = 302
MENU_REPORT_DISPATCH = 303
MENU_DISPATCH_CONNECT = 401
MENU_DISPATCH_DISCONNECT = 402
MENU_DISPATCH_SETUPIP = 403
MENU_DISPATCH_SETUPPORT = 404


wildcard = "JSON file (*.json)|*.json|"	 \
		   "All files (*.*)|*.*"
wildcardTxt = "TXT file (*.txt)|*.txt|"	 \
		   "All files (*.*)|*.*"
wildcardLog = "Log file (*.log)|*.log|"	 \
		   "All files (*.*)|*.*"

(TrainLocationEvent, EVT_TRAINLOC) = newevent.NewEvent()  
(ClockEvent, EVT_CLOCK) = newevent.NewEvent()  
(BreakerEvent, EVT_BREAKER) = newevent.NewEvent()  
(SocketConnectEvent, EVT_SOCKET_CONNECT) = newevent.NewEvent()
(SocketDisconnectEvent, EVT_SOCKET_DISCONNECT) = newevent.NewEvent()
(SocketFailureEvent, EVT_SOCKET_FAILURE) = newevent.NewEvent()

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		font = wx.Font(wx.Font(14, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))

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
		
		self.menuReports = wx.Menu()
		i = wx.MenuItem(self.menuReports, MENU_REPORT_OP_WORKSHEET, "Operating Worksheet", helpString="Print an Operating Worksheet")
		i.SetFont(font)
		self.menuReports.Append(i)
		i = wx.MenuItem(self.menuReports, MENU_REPORT_TRAIN_CARDS, "Train Cards", helpString="Print Train Cards")
		i.SetFont(font)
		self.menuReports.Append(i)
		i = wx.MenuItem(self.menuReports, MENU_REPORT_DISPATCH, "Train/Loco/Block Report", helpString="Information to enter into dispatcher")
		i.SetFont(font)
		self.menuReports.Append(i)
		
		self.menuDispatch = wx.Menu()
		i = wx.MenuItem(self.menuDispatch, MENU_DISPATCH_CONNECT, "Connect", helpString="Connect to dispatcher")
		i.SetFont(font)
		self.menuDispatch.Append(i)
		i = wx.MenuItem(self.menuDispatch, MENU_DISPATCH_DISCONNECT, "Disconnect", helpString="Disconnect from Dispatcher")
		i.SetFont(font)
		self.menuDispatch.Append(i)
		self.menuDispatch.Enable(MENU_DISPATCH_DISCONNECT, False)
		self.menuDispatch.AppendSeparator()
		i = wx.MenuItem(self.menuDispatch, MENU_DISPATCH_SETUPIP, "Configure IP Address", helpString="Configure IP address")
		i.SetFont(font)
		self.menuDispatch.Append(i)
		i = wx.MenuItem(self.menuDispatch, MENU_DISPATCH_SETUPPORT, "Configure Port", helpString="Configure Port")
		i.SetFont(font)
		self.menuDispatch.Append(i)

		menuBar.Append(self.menuFile, "File")
		menuBar.Append(self.menuManage, "Manage")
		menuBar.Append(self.menuReports, "Reports")
		menuBar.Append(self.menuDispatch, "Dispatch")
				
		self.SetMenuBar(menuBar)
		self.menuBar = menuBar

		sizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.panel = TrainTrackerPanel(self)
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
		self.Bind(wx.EVT_MENU, self.panel.onManageOrder, id=MENU_MANAGE_ORDER)
		self.Bind(wx.EVT_MENU, self.panel.onAssignLocos, id=MENU_MANAGE_ASSIGN_LOCOS)
		self.Bind(wx.EVT_MENU, self.panel.onManageLocos, id=MENU_MANAGE_LOCOS)
		
		self.Bind(wx.EVT_MENU, self.panel.onReportOpWorksheet, id=MENU_REPORT_OP_WORKSHEET)
		self.Bind(wx.EVT_MENU, self.panel.onReportTrainCards, id=MENU_REPORT_TRAIN_CARDS)
		
		self.Bind(wx.EVT_MENU, self.panel.connectToDispatch, id=MENU_DISPATCH_CONNECT)
		self.Bind(wx.EVT_MENU, self.panel.disconnectFromDispatch, id=MENU_DISPATCH_DISCONNECT)
		self.Bind(wx.EVT_MENU, self.panel.setupIP, id=MENU_DISPATCH_SETUPIP)
		self.Bind(wx.EVT_MENU, self.panel.setupPort, id=MENU_DISPATCH_SETUPPORT)
		self.Bind(wx.EVT_MENU, self.panel.dispatchReport, id=MENU_REPORT_DISPATCH)
		
		self.SetSizer(sizer)
		self.Layout()
		self.Fit();
		
	def setTitle(self, train=None, order=None, engineer=None, loco=None, connection=None):
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
			title += "     %s" % self.connection
		self.SetTitle(title)
		
	def disableReports(self):
		self.menuReports.Enable(MENU_REPORT_OP_WORKSHEET, False)
		
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
		self.connected = False
			
		self.log = Log()
		
		self.listener = None

		self.pendingTrains = []
		self.activeEngineers = [] 
		self.allPresentEngineers = [x for x in self.activeEngineers]
		self.trainOrder = None
		
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		labelFont = wx.Font(wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL, faceName="Monospace"))
		labelFontBold = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		
		vsizerl = wx.BoxSizer(wx.VERTICAL)
		vsizerl.AddSpacer(20)

		boxTrain = wx.StaticBox(self, wx.ID_ANY, "Train")
		boxTrain.SetFont(labelFontBold)
		topBorder = boxTrain.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)
		bsizer.Add(wx.StaticText(boxTrain, wx.ID_ANY, "", size=(240, -1)))
		
		self.chTrain = wx.Choice(boxTrain, wx.ID_ANY, choices=self.pendingTrains, size=(90, -1))
		self.chTrain.SetSelection(0)
		self.chTrain.SetFont(textFont)
		self.Bind(wx.EVT_CHOICE, self.onChoiceTID, self.chTrain)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(boxTrain, wx.ID_ANY, "Scheduled: ", size=(120, -1))
		st.SetFont(textFontBold)
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chTrain)
		bsizer.Add(sz)
		
		bsizer.AddSpacer(10)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		self.cbExtra = wx.CheckBox(boxTrain, wx.ID_ANY, "Run Extra")
		self.cbExtra.SetFont(textFontBold)
		self.Bind(wx.EVT_CHECKBOX, self.onCbExtra, self.cbExtra)
		sz.AddSpacer(100)
		sz.Add(self.cbExtra)
		self.cbExtra.Enable(False)
		bsizer.Add(sz)
		
		bsizer.AddSpacer(10)

		self.chExtra = wx.Choice(boxTrain, wx.ID_ANY, choices=[], size=(90, -1))
		self.chExtra.SetFont(textFont)
		self.chExtra.Enable(False)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(boxTrain, wx.ID_ANY, "Extra: ", size=(120, -1))
		st.SetFont(textFontBold)
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
		boxEng.SetFont(labelFontBold)
		topBorder = boxEng.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)
		bsizer.Add(wx.StaticText(boxEng, wx.ID_ANY, "", size=(240, -1)))

		self.chEngineer = wx.Choice(boxEng, wx.ID_ANY, choices=self.activeEngineers)
		self.chEngineer.SetSelection(0)
		self.chEngineer.SetFont(textFont)
		self.selectedEngineer = self.chEngineer.GetString(0)
		self.Bind(wx.EVT_CHOICE, self.onChoiceEngineer, self.chEngineer)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(boxEng, wx.ID_ANY, "Engineer: ", size=(120, -1))
		st.SetFont(textFontBold)
		sz.Add(st, 1, wx.TOP, 4)
		sz.Add(self.chEngineer)
		bsizer.Add(sz)
		
		bsizer.AddSpacer(10)
		
		sz = wx.BoxSizer(wx.HORIZONTAL)
		self.cbATC = wx.CheckBox(boxEng, wx.ID_ANY, "ATC")
		self.cbATC.SetFont(textFontBold)
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
		self.bAssign.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bAssignPressed, self.bAssign)
		btnsizer.Add(self.bAssign)
		self.bAssign.Enable(len(self.activeEngineers) != 0 and len(self.pendingTrains) != 0)
		
		btnsizer.AddSpacer(30)
		
		self.bSkip = wx.Button(self, wx.ID_ANY, "Skip\nTrain", size=BTNSZ)
		self.bSkip.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bSkipPressed, self.bSkip)
		btnsizer.Add(self.bSkip)

		vsizerl.AddSpacer(20)
		vsizerl.Add(btnsizer, 1, wx.ALIGN_CENTER_HORIZONTAL)

		vsizerr = wx.BoxSizer(wx.VERTICAL)
		vsizerr.AddSpacer(20)
		
		self.teBreaker = wx.TextCtrl(self, wx.ID_ANY, "", size=(240, -1), style=wx.TE_CENTER)
		self.setBreakerValue("All OK")
		breakerFont = wx.Font(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		self.teBreaker.SetFont(breakerFont)
		self.teBreaker.SetForegroundColour(wx.Colour(255, 255, 255))

		self.clock = gizmos.LEDNumberCtrl(self, wx.ID_ANY, size=(160, 50), style=gizmos.LED_ALIGN_CENTER)  # @UndefinedVariable
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.teBreaker, 1, wx.TOP, 10)
		hsz.AddSpacer(100)
		hsz.Add(self.clock)
		
		vsizerr.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizerr.AddSpacer(20)

		boxDetails = wx.StaticBox(self, wx.ID_ANY, "Train Details")
		boxDetails.SetFont(labelFontBold)
		topBorder = boxDetails.GetBordersForSizer()[0]
		bsizer = wx.BoxSizer(wx.VERTICAL)
		bsizer.AddSpacer(topBorder)
		
		bsizer.Add(wx.StaticText(boxDetails, wx.ID_ANY, "", size=(300, -1)))
		bsizer.AddSpacer(20)

		self.stDescription = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(400, -1))
		self.stDescription.SetFont(labelFontBold)
		bsizer.Add(self.stDescription)
		bsizer.AddSpacer(10)
		self.stStepsTower = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(100, 150))
		self.stStepsLoc = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(60, 150))
		self.stStepsStop = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(300, 150))
		self.stStepsTower.SetFont(labelFont)
		self.stStepsLoc.SetFont(labelFont)
		self.stStepsStop.SetFont(labelFont)
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.Add(self.stStepsTower)
		sz.Add(self.stStepsLoc)
		sz.Add(self.stStepsStop)
		bsizer.Add(sz)
		
		self.stLocoInfo = wx.StaticText(boxDetails, wx.ID_ANY, "", size=(600, -1))
		self.stLocoInfo.SetFont(labelFontBold)
		bsizer.AddSpacer(10)
		bsizer.Add(self.stLocoInfo)
		bsizer.AddSpacer(20)
		
		bhsizer = wx.BoxSizer(wx.HORIZONTAL)
		bhsizer.AddSpacer(20)
		bhsizer.Add(bsizer)
		bhsizer.AddSpacer(20)
		boxDetails.SetSizer(bhsizer)
		
		vsizerr.Add(boxDetails)
		vsizerr.AddSpacer(20)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizerl)
		hsizer.AddSpacer(90)
		hsizer.Add(vsizerr)
		hsizer.AddSpacer(20)
		
		wsizer = wx.BoxSizer(wx.VERTICAL)
		wsizer.Add(hsizer)
		wsizer.AddSpacer(20)
		
		self.activeTrainList = ActiveTrainList(self)
		sz = wx.BoxSizer(wx.HORIZONTAL)
		sz.AddSpacer(20)
		sz.Add(self.activeTrainList)
		sz.AddSpacer(20)
		
		wsizer.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		wsizer.AddSpacer(20)

		self.SetSizer(wsizer)
		self.Layout()
		self.Fit()
		
		self.Bind(EVT_TRAINLOC, self.setTrainLocation)
		self.Bind(EVT_CLOCK, self.setClockEvent)
		self.Bind(EVT_BREAKER, self.setBreakersEvent)
		self.Bind(EVT_SOCKET_CONNECT, self.socketConnectEvent)
		self.Bind(EVT_SOCKET_DISCONNECT, self.socketDisconnectEvent)
		self.Bind(EVT_SOCKET_FAILURE, self.socketFailureEvent)
		
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

		self.setBreakerValue("All OK")
		self.setClockValue("")
		self.setExtraTrains()
		self.parent.setTitle(connection="Not Connected")
		
	def dispatchReport(self, _):
		self.report.dispatchReport(self.roster, self.trainOrder)
		
	def connectToDispatch(self, _):
		self.parent.setTitle(connection="Connecting...")
		self.log.append("Connecting to dispatch at %s:%s" % (self.settings.dispatchip, self.settings.dispatchport))
		self.listener = Listener(self.settings.dispatchip, self.settings.dispatchport)
		self.listener.bind(self.socketConnect, self.socketDisconnect, self.connectFailure, self.trainReport, self.setClock, self.setBreakers)
		self.listener.start()
		
	def socketConnect(self):  # thread context
		evt = SocketConnectEvent()
		wx.PostEvent(self, evt)

	def socketConnectEvent(self, _):
		self.parent.setTitle(connection="Connected")
		self.connected = True
		self.log.append("Socket Connection successful")
		self.parent.enableListenerDisconnect(True)
		
	def socketDisconnect(self):  # thread context
		evt = SocketDisconnectEvent()
		wx.PostEvent(self, evt)

	def socketDisconnectEvent(self, _):
		self.parent.setTitle(connection="Disconnected")
		self.log.append("Socket disconnection complete")
		self.parent.enableListenerDisconnect(False)
		self.connected = False
		self.setBreakerValue("")
		self.setClockValue("")
		self.listener = None
		
	def connectFailure(self):  # thread context
		evt = SocketFailureEvent()
		wx.PostEvent(self, evt)

	def socketFailureEvent(self, _):
		dlg = wx.MessageDialog(self, 'Connection to Dispatcher failed.\nNo locomotive or block information is available',
                               'Connection Failed',
                               wx.OK | wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()
		
		self.parent.setTitle(connection="Connection Failed")
		self.log.append("Error from socket connection request")
		self.listener = None
		
	def disconnectFromDispatch(self, _):
		self.log.append("Starting socket disconnection request")
		self.listener.kill()
		
	def setupIP(self, _):
		dlg = wx.TextEntryDialog(self, 'Enter/Modify IP Address', 'IP Address', self.settings.dispatchip)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			newIP = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		self.settings.dispatchip = newIP
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
		
	def trainReport(self, train, loco, block):
		# This method executes in thread context - don't touch the wxpython elements here
		evt = TrainLocationEvent(train=train, loco=loco, block=block)
		wx.PostEvent(self, evt)
		
	def setTrainLocation(self, evt):
		tid = evt.train
		loco = evt.loco
		block = evt.block
		self.log.append("Train report: Train(%s) Loco(%s) Blk(%s)" % (tid, loco, block))

		if tid is None or tid == "":
			if loco is not None:
				self.log.append("Trying to identify train by loco id")
				tid = self.roster.getTrainByLoco(loco)
						
		if tid is None or tid == "":
			self.log.append("Unable to determine train ID")
			return 
		
		tInfo = self.roster.getTrain(tid)
		if tInfo is None:
			self.log.append("Ignoring train report for train (%s) - unknown train" % tid)
			return
		
		tInfo["block"] = block
		self.log.append("Setting block for train %s to %s" % (tid, block))
		desc = None
		if tInfo["loco"] != loco and loco != "":
			tInfo["loco"] = loco
			desc = self.locos.getLoco(loco)
			self.log.append("Setting locomotive for train %s to %s" % (tid, loco))

		self.activeTrainList.updateTrain(tid, loco, desc, block)
		if tid == self.selectedTrain:
			self.showInfo(self.selectedTrain)
			
	def setClock(self, tm):
		evt = ClockEvent(tm=tm)
		wx.PostEvent(self, evt)
		
	def setClockEvent(self, evt):
		self.setClkockValue(evt.tm)
		
	def setClockValue(self, tm):
		if not self.connected:
			self.clock.SetValue("")
			self.clock.SetBackgroundColour(wx.Colour(255, 115, 47))
			return
		self.clock.SetBackgroundColour(wx.Colour(0, 0, 0))
		self.clock.SetValue(tm)
		
	def setBreakers(self, txt):
		evt = BreakerEvent(txt=txt)
		wx.PostEvent(self, evt)
		
	def setBreakersEvent(self, evt):
		print("breakers: %s" % evt.txt)
		self.setBreakerValue(evt.txt)
		
	def setBreakerValue(self, txt):
		if not self.connected:
			self.teBreaker.SetValue("not connected")
			self.teBreaker.SetBackgroundColour(wx.Colour(255, 115, 47))
			return
			
		self.teBreaker.SetValue(txt)
		if txt == "All OK":
			self.teBreaker.SetBackgroundColour(wx.Colour(10, 158, 32))
		else:
			self.teBreaker.SetBackgroundColour(wx.Colour(241, 41, 47))

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
		self.setExtraTrains()
		
	def loadTrainFile(self, fn):
		self.log.append("loading train file (%s)" % fn)
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
	
	def setExtraTrains(self):		
		self.extraTrains = self.roster.getExtraTrains(self.pendingTrains)
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
			self.bAssign.Enable(len(self.activeEngineers) > 0 or self.cbATC.IsChecked())
		else:
			self.chExtra.Enable(False)
			self.chTrain.Enable(True)
			tx = self.chTrain.GetSelection()
			tid = self.chTrain.GetString(tx)
			self.setSelectedTrain(tid)
			self.bSkip.Enable(len(self.pendingTrains) > 0)
			self.cbExtra.SetValue(False)
			if len(self.pendingTrains) > 0 and (len(self.activeEngineers) > 0 or self.cbATC.IsChecked()):
				self.bAssign.Enable(True)
			else:
				self.bAssign.Enable(False)
	
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
		self.log.append("Loading locomotive file (%s)" % fn)
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

				self.activeTrainList.updateTrain(tid, rloco, ndesc, tInfo["block"])
					
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
			
		self.activeEngineers = []
		self.allPresentEngineers = [x for x in self.activeEngineers]
		self.chEngineer.SetItems(self.activeEngineers)
		self.chEngineer.Enable(len(self.activeEngineers) > 0)

		self.activeTrainList.clear()
		self.cbATC.SetValue(False)
		self.bAssign.Enable(len(self.pendingTrains) > 0 and len(self.activeEngineers) > 0)
		
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
		self.setExtraTrains()
		
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

		if not preserveActive:
			self.activeTrainList.clear()
			
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

		with open(path, "w") as ofp:
			for ln in self.log:
				ofp.write("%s\n" % ln)
		
	def onCbATC(self, _):
		if self.cbATC.IsChecked():
			self.bAssign.Enable(len(self.pendingTrains) > 0 or self.cbExtra.IsChecked())
		else:
			self.bAssign.Enable(len(self.activeEngineers) > 0 and (len(self.pendingTrains) > 0 or self.cbExtra.IsChecked()))
		
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
			descr = ""
		else:
			loco = tInfo["loco"]
			descr = self.locos.getLoco(loco)
			if descr is None:
				descr = ""
		if "block" in tInfo:
			block = tInfo["block"]
		else:
			block = None	
		acttr = {
			"tid": tid,
			"dir": tInfo["dir"],
			"origin": tInfo["origin"],
			"terminus": tInfo["terminus"],
			"block": block,
			"loco": loco,
			"desc": descr,
			"engineer": eng}
		self.activeTrainList.addTrain(acttr)
		self.log.append("Assigned %s train %s to %s" % (tid, "extra" if runningExtra else "", eng))

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
			self.enableExtraMode(False)
		
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
		
	def reassignTrain(self, t):
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
		
	def returnActiveTrain(self, t):
		dlg = wx.MessageDialog(self, "This removes train %s (and its engineer) from the\nactive list, and places it back to the top of the schedule.\nThis cannot be undone.\n\nPress OK to continue, or Cancel" % t["tid"],
							'Return Train', wx.OK | wx.CANCEL | wx.OK_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_CANCEL:
			return

		self.log.append("Retruned train %s from active list" % t["tid"])
		self.activeTrainList.delSelected()
		self.pendingTrains = [t["tid"]] + self.pendingTrains
		self.chTrain.SetItems(self.pendingTrains)

		self.chTrain.SetSelection(0)
		tid = self.chTrain.GetString(0)
		self.setSelectedTrain(tid)
		
		if t["engineer"] in self.allPresentEngineers:
			self.log.append("Returned engineer %s to head of pool" % t["engineer"])
			if t["engineer"] not in self.activeEngineers:
				self.activeEngineers = [t["engineer"]] + self.activeEngineers
			self.chEngineer.Enable(True)
			self.chEngineer.SetItems(self.activeEngineers)
			self.chEngineer.SetSelection(0)
			self.selectedEngineer = self.chEngineer.GetString(0)
			
		self.chTrain.Enable(len(self.pendingTrains) > 0)
			
		if len(self.pendingTrains) > 0 and (len(self.activeEngineers) > 0 or self.cbATC.IsChecked()):
			self.bAssign.Enable(True)
		
	def removeActiveTrain(self, t):
		dlg = wx.MessageDialog(self, "This indicates that train %s has reached its destination.\nThis cannot be undone.\n\nPress OK to continue, or Cancel" % t["tid"],
							'Remove Train', wx.OK | wx.CANCEL | wx.OK_DEFAULT | wx.ICON_QUESTION)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_CANCEL:
			return

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
		
	def changeLoco(self, t):
		dlg = wx.SingleChoiceDialog(
				self, 'Choose a Locomotive', 'Change Locomotive',
				self.locos.getLocoList(),
				wx.CHOICEDLG_STYLE
				)

		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			loco = dlg.GetStringSelection()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		tid = t["tid"]
		
		desc = self.locos.getLoco(loco)
		self.activeTrainList.updateTrain(tid, loco, desc, None)
		
		tinfo = self.roster.getTrain(tid)
		if tinfo is not None:
			tinfo["loco"] = loco
		
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
			self.stStepsLoc.SetLabel("")
			self.stStepsStop.SetLabel("")
			return
		
		if self.roster is None:
			self.stDescription.SetLabel("Train Roster is empty")
			self.stStepsTower.SetLabel("")
			self.stStepsLoc.SetLabel("")
			self.stStepsStop.SetLabel("")
			return
		else:
			tInfo = self.roster.getTrain(tid)
			
		if tInfo is None:
			self.stDescription.SetLabel("Train %s is not in Train Roster" % tid)
			self.stStepsTower.SetLabel("")
			self.stStepsLoc.SetLabel("")
			self.stStepsStop.SetLabel("")
			return

		descr = "%s   %sbound %s" % (tid, tInfo["dir"], tInfo["desc"])		
		self.stDescription.SetLabel(descr)
		locs = []
		for step in tInfo["steps"]:
			if step[2] == 0:
				locs.append("")
			else:
				locs.append("(%2d)" % step[2])
		towers = "\n".join([step[0] for step in tInfo["steps"]])
		loc = "\n".join(locs)
		stops  = "\n".join([step[1] for step in tInfo["steps"]])

		self.stStepsTower.SetLabel(towers)
		self.stStepsLoc.SetLabel(loc)
		self.stStepsStop.SetLabel(stops)
		# TODO - May have to limit how many lines we see here - or come up with other approach
		
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
			blockString = ""
		else:
			blockString = "Block: %s" % tInfo["block"]	
						
		self.stLocoInfo.SetLabel("%-40.40s %s" % (locoString, blockString))
				
	def onManageOrder(self, _):
		dlg = ManageOrderDlg(self, self.trainOrder, self.roster, self.settings)
		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			norder = dlg.getValues()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		neworder = [t for t in norder if not self.activeTrainList.hasTrain(t)]
		
		if self.trainOrder is None:
			self.pendingTrains = [x for x in neworder]
		else:
			self.trainOrder.setNewOrder(neworder)
			self.pendingTrains = [x for x in self.trainOrder]
			
		self.setTrainOrder(preserveActive=True)

	def onManageTrains(self, _):
		dlg = ManageTrainsDlg(self, self.roster, self.locos, self.settings)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		
		# no need to retrieve dialog values because the data is saved automatically when OK is pressed
		# just re-read the file
		self.loadTrainFile(os.path.join(self.settings.traindir, self.settings.trainfile))
		self.setExtraTrains()
		
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
		
	def onReportOpWorksheet(self, _):
		self.report.OpWorksheetReport(self.roster, self.trainOrder, self.locos)
			
	def onReportTrainCards(self, _):
		self.report.TrainCards(self.roster, self.trainOrder)
			
	def onClose(self, _):
		if self.activeTrainList.count() > 0:
			dlg = wx.MessageDialog(self, 'Trains are still active.\nPress "Yes" to exit program, or "No" to cancel.',
	                               'Active Trains',
	                               wx.YES_NO | wx.ICON_QUESTION)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		if self.listener is not None:
			self.listener.kill()
			
		self.settings.save()
		self.Destroy()
		
class DetailsDlg(wx.Dialog):
	def __init__(self, parent, tid, tinfo, desc, engineer):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Train Details")
		self.Bind(wx.EVT_CLOSE, self.onClose)

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
		
		if desc is None:
			ldesc = ""
		else:
			ldesc = desc.replace('&', '&&')
		st = wx.StaticText(self, wx.ID_ANY, "Loco: %s - %s" % (tinfo["loco"], ldesc))
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
			st2 = wx.StaticText(self, wx.ID_ANY, "(%2d)" % stp[2] if stp[2] > 0 else "", size=(60, -1))
			st2.SetFont(labelFontBold)
			st3 = wx.StaticText(self, wx.ID_ANY, stp[1])
			st3.SetFont(labelFontBold)
			
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(120)
			hsz.Add(st1)
			hsz.Add(st2)
			hsz.Add(st3)
			
			vsizer.Add(hsz)
			vsizer.AddSpacer(2)
			
		vsizer.AddSpacer(10)
		
		if tinfo["block"] is None or tinfo["block"] == "":
			block = "<unknown>"
		else:
			block = tinfo["block"]
			
		st = wx.StaticText(self, wx.ID_ANY, "Block: %s" % block)
		st.SetFont(labelFontBold)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(100)
		hsz.Add(st)
		
		vsizer.Add(hsz)
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
