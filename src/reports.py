import HTML
import wx
import os
import wx.html2 as webview

backends = [
	webview.WebViewBackendEdge,
	webview.WebViewBackendIE,
	webview.WebViewBackendWebKit,
	webview.WebViewBackendDefault
]
BTNSZ = (120, 46)

class Report:
	def __init__(self, parent):
		self.initialized = False
		self.parent = parent
		
		self.backend = None
		for bid in backends:
			available = webview.WebView.IsBackendAvailable(bid)
			if available and self.backend is None:
				self.backend = bid
				break

		if self.backend is None:
			dlg = wx.MessageDialog(self.parent, "Unable to find an available backend", 
		                               "Report Initialization failed",
		                               wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		self.initialized = True
		
	def Initialized(self):
		return self.initialized

	def OpWorksheetReport(self, roster, order, locos):	
		if not self.Initialized:
			dlg = wx.MessageDialog(self.parent, "Unable to generate reports - initialization failed", 
		                               "Report Initialization failed",
		                               wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return
			
		css = HTML.StyleSheet()
		css.addElement("table", {'width': '650px', 'border-spacing': '15px',  'margin-left': 'auto', 'margin-right': 'auto'})
		css.addElement("table, th, td", { 'border': "1px solid black", 'border-collapse': 'collapse'})
		css.addElement("td, th", {'text-align': 'center', 'width': '80px', 'overflow': 'hidden'})
		css.addElement("td.description", {'text-align': 'left', 'width': '300px', 'overflow': 'hidden'})
		css.addElement("td.engineer", {'width': '180px'})
		
		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))
		
		html += HTML.startbody()
	
	
		html += HTML.h1({'align': 'center'}, "Operating Worksheet")	
		html += "<br><br>"
		
		colorEast = "#c1e2b4"
		colorWest = "#fdc4a8"
		
		rows = []
		
		for tid in order:
			tInfo = roster.getTrain(tid)
			c = colorEast if tInfo["dir"].lower() == "east" else colorWest
			lid = tInfo["loco"]
			if lid is None:
				lid = ""
				desc = ""
			else:
				desc = locos.getLoco(lid)
				if desc is None:
					desc = ""
			rows.append(HTML.tr({},
				HTML.td({"bgcolor": c}, tid),
				HTML.td({}, lid),
				HTML.td({'class': 'description'}, HTML.nbsp(2), desc),
				HTML.td({'class': 'engineer'}, ""))
			)
		
		header = HTML.tr({},
			HTML.th({}, "Train"),
			HTML.th({}, "Loco"),
			HTML.th({}, "Description"),
			HTML.th({}, "Engineer"))
		
		html += HTML.table({}, header, "".join(rows))
		html += HTML.endbody()
		html += HTML.endhtml()
		
		dlg = RptDlg(self.parent, self.backend, "Operating Worksheet", html)
		dlg.ShowModal()
		dlg.Destroy()

	def TrainCards(self, roster, order):	
		if not self.Initialized:
			dlg = wx.MessageDialog(self.parent, "Unable to generate reports - initialization failed", 
		                               "Report Initialization failed",
		                               wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		dlg = ChooseCardsDlg(self.parent, list(order))
		rc = dlg.ShowModal()
		
		if rc == wx.ID_OK:
			cardsToPrint = dlg.getValues()
			
		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return
		
		ct = 0
		for flag in cardsToPrint:
			if flag:
				ct += 1
				
		if ct == 0:
			dlg = wx.MessageDialog(self.parent, "No Train Cards chosen - skipping report", 
		                               "Nothing to print",
		                               wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return

		css = HTML.StyleSheet()
		css.addElement("div.page", {"page-break-inside": "avoid"})
		css.addElement("*", {"box-sizing": "border-box"})
		css.addElement(".row", {"margin-left": "-5px", "margin-right": "-5px", "height": "107mm"})
		css.addElement(".column", {"float": "left", "width": "138mm", "padding": "1px"})
		css.addElement(".row::after", {"content": '""', "clear": "both", "display": "table"})
		css.addElement("table", {"border-collapse": "collapse", "border-spacing": "0", "width": "100%", "height": "99mm", "font-family": '"Times New Roman", Times, serif', "font-size": "16px"})
		css.addElement("td.trainid", {"width": "36.4%", "padding-left": "50px", "padding-top": "10px", "font-size": "28px", "font-weight": "bold"})
		css.addElement("td.firstcol", {"width": "36.4%", "padding-left": "50px"})
		css.addElement("td.secondcol", {"width": "10%"})
		css.addElement("td", {"text-align": "left", "padding": "6px"})
		css.addElement("td.cardnumber", {"text-align": "right", "padding-right": "50px"})
		
		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))
		
		html += HTML.startbody()
		
		cards = []

		for tx in range(len(order)):
			tid = order.getTid(tx)
			if cardsToPrint[tx]:
				cards.append(self.formatTrainCard(tid, roster.getTrain(tid), tx+1))
			
		nCards = len(cards)
		
		divs = []
		for i in range(0, nCards-1, 2):
			divs.append(HTML.div({"class": "row"}, cards[i], cards[i+1]))
			
		if nCards%2 != 0:
			divs.append(HTML.div({"class": "row"}, cards[-1]))

		dx = 0		
		while dx < len(divs):
			if dx == len(divs)-1:
				html += HTML.div({"class": "page"}, divs[dx])
			else:
				html += HTML.div({"class": "page"}, divs[dx], divs[dx+1])
				#HTML.p({}, HTML.nbsp()), 
				
			dx += 2

		html += HTML.endbody()
		html += HTML.endhtml()

		dlg = RptDlg(self.parent, self.backend, "Train Cards", html)
		dlg.ShowModal()
		dlg.Destroy()

	def formatTrainCard(self, tid, tinfo, tx):
		trainIdRow = HTML.tr({}, HTML.td({"class": "trainid"}, tid), HTML.td())
		emptyRow = HTML.tr({}, HTML.td({}, HTML.nbsp()))
		descRow = HTML.tr({}, HTML.td({"class": "firstcol", "colspan": "3"}, "%sbound %s" % (tinfo["dir"], tinfo["desc"])))
		cardNumberRow = HTML.tr({}, HTML.td({}, ""), HTML.td({}, ""), HTML.td({"class": "cardnumber"}, "%d" % tx))

		stepRows = []
		for stp in tinfo["steps"]:
			row = HTML.tr({},
						HTML.td({"class": "firstcol"}, stp[0]),
						HTML.td({"class": "secondcol"}, "" if stp[2] == 0 else ("(%2d)" % stp[2])),
						HTML.td({}, stp[1])
			)
			stepRows.append(row)
			
		nRows = len(stepRows)
		nEmpty = 8 - nRows
		
		table = HTML.table({},
			trainIdRow,
			descRow,
			emptyRow,
			" ".join(stepRows),
			nEmpty * emptyRow,
			cardNumberRow
		)
		
		return HTML.div({"class": "column"}, table)
	
	def dispatchReport(self, trains, order):
		if not self.Initialized:
			dlg = wx.MessageDialog(self.parent, "Unable to generate reports - initialization failed", 
		                               "Report Initialization failed",
		                               wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return
			
		css = HTML.StyleSheet()
		css.addElement("table", {'width': '650px', 'border-spacing': '15px',  'margin-left': 'auto', 'margin-right': 'auto'})
		css.addElement("table, th, td", { 'border': "1px solid black", 'border-collapse': 'collapse'})
		css.addElement("td, th", {'text-align': 'center', 'width': '80px', 'overflow': 'hidden'})
		
		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))
		
		html += HTML.startbody()
	
	
		html += HTML.h1({'align': 'center'}, "Train Locomotive and Block Report")	
		html += "<br><br>"

		header = HTML.tr({},
			HTML.th({}, "Train"),
			HTML.th({}, "Loco"),
			HTML.th({}, "Block"))

		rows = []		
		for tid in trains:
			tinfo = trains.getTrain(tid)
			row = HTML.tr({},
						HTML.td({}, tid),
						HTML.td({}, tinfo["loco"]),
						HTML.td({}, tinfo["block"])
			)
			rows.append(row)

		html += HTML.table({}, header, "".join(rows))
		html += HTML.endbody()
		html += HTML.endhtml()
		
		dlg = RptDlg(self.parent, self.backend, "Dispatch Report", html)
		dlg.ShowModal()
		dlg.Destroy()
	
class ChooseCardsDlg(wx.Dialog):
	def __init__(self, parent, order):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose Train Cards")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.order = order

		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		st = wx.StaticText(self, wx.ID_ANY, "Select Train Cards to Print:")
		st.SetFont(textFontBold)
		vsizer.Add(st)
		vsizer.AddSpacer(5)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		
		clb = wx.CheckListBox(self, wx.ID_ANY, choices=order)
		clb.SetFont(textFont)
		self.Bind(wx.EVT_CHECKLISTBOX, self.onClbOrder, clb)
		self.clbOrder = clb
		hsz.Add(clb)
		
		hsz.AddSpacer(10)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		
		self.bCheckAll = wx.Button(self, wx.ID_ANY, "Select\nAll", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bCheckAllPressed, self.bCheckAll)
		self.bCheckAll.SetFont(btnFont)
		
		self.bUncheckAll = wx.Button(self, wx.ID_ANY, "Unselect\nAll", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.bUncheckAllPressed, self.bUncheckAll)
		self.bUncheckAll.SetFont(btnFont)
		
		vsz.Add(self.bCheckAll)
		vsz.AddSpacer(20)
		vsz.Add(self.bUncheckAll)
		
		hsz.Add(vsz, 0, wx.ALIGN_CENTER_VERTICAL)
		
		vsizer.Add(hsz)
		
		vsizer.AddSpacer(10)
		
		self.stCheckCount = wx.StaticText(self, wx.ID_ANY, " 0 Trains Selected")
		self.stCheckCount.SetFont(textFontBold)
		vsizer.Add(self.stCheckCount, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsizer.AddSpacer(20)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.Add(self.bOK)
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
		self.Fit();
		
	def bCheckAllPressed(self, _):
		for i in range(len(self.order)):
			self.clbOrder.Check(i, True)
			
		self.reportCheckCount()
		
	def bUncheckAllPressed(self, _):
		for i in range(len(self.order)):
			self.clbOrder.Check(i, False)
			
		self.reportCheckCount()
		
	def onClbOrder(self, _):
		self.reportCheckCount()
		
	def reportCheckCount(self):
		ct = 0
		for i in range(len(self.order)):
			if self.clbOrder.IsChecked(i):
				ct += 1
				
		if ct == 1:
			text = " 1 Train  Selected"
		else:
			text = "%2d Trains Selected" % ct
			
		self.stCheckCount.SetLabel(text)
		
	def bOKPressed(self, _):
		self.EndModal(wx.ID_OK)
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		self.EndModal(wx.ID_CANCEL)
		
	def getValues(self):
		return [self.clbOrder.IsChecked(i) for i in range(len(self.order))]

class RptDlg(wx.Dialog):
	def __init__(self, parent, backend, title, html):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size=(760, 800), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		self.wv = webview.WebView.New(self, backend=backend)
		
		vsizer=wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		vsizer.Add(self.wv, 1, wx.EXPAND)
		vsizer.AddSpacer(20)
		
		btnsizer = wx.BoxSizer(wx.HORIZONTAL)
		btnsizer.AddSpacer(20)
		
		btn = wx.Button(self, wx.ID_ANY, "Print", size=BTNSZ)
		btn.SetFont(btnFont)
		self.Bind(wx.EVT_BUTTON, self.onBtn, btn)
		btnsizer.Add(btn)
		
		btnsizer.AddSpacer(20)
		
		vsizer.Add(btnsizer)
		vsizer.AddSpacer(20)
				
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer, 1, wx.EXPAND)
		hsizer.AddSpacer(20)
		self.SetSizer(hsizer)

		htmlFileName = "report.html"
		with open(htmlFileName, "w") as fp:
			fp.write(html)
		
		path = os.path.join(os.getcwd(), htmlFileName)
		
		fileURL = 'file:///'+path

		self.wv.LoadURL(fileURL)
		
		self.Layout()
		
	def onBtn(self, _):
		self.wv.Print()
		
	def onClose(self, _):
		self.EndModal(wx.ID_OK)
	