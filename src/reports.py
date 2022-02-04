import HTML
import wx
import os
import wx.html2 as webview

# WebView Backends
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
		
		color1 = "#ffffff"
		color2 = "#caffca"
		
		rows = []
		
		for tid in order:
			c = color1
			color1 = color2
			color2 = c
			tInfo = roster.getTrain(tid)
			lid = tInfo["loco"]
			if lid is None:
				lid = ""
				desc = ""
			else:
				desc = locos.getLoco(lid)
				if desc is None:
					desc = ""
			rows.append(HTML.tr({"bgcolor": c},
				HTML.td({}, tid),
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


	