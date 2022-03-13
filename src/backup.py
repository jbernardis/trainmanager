
import wx
import os
from zipfile import ZipFile, is_zipfile

TYPE_TRAIN = "train"
TYPE_ORDER = "order"
TYPE_ENGINEER = "engineer"
TYPE_LOCO = "loco"

def saveData(parent, settings):
		wildcard = "ZIP File (*.zip)|*.zip"
		dlg = wx.FileDialog(
			parent, message="Save data files to zip file ...", defaultDir=os.getcwd(),
			defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
			)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			zipfile = dlg.GetPath()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		dirs = { TYPE_TRAIN: settings.traindir,
				TYPE_ORDER: settings.orderdir,
				TYPE_ENGINEER: settings.engineerdir,
				TYPE_LOCO: settings.locodir }

		fc = 0
		msg2 = ""
		with ZipFile(zipfile, 'w') as zfp:
			for d in dirs.keys():
				fl = [ f for f in os.listdir(dirs[d]) if os.path.isfile(os.path.join(dirs[d], f)) ]
				for fn in fl:
					fc += 1
					msg2 += "%d: %s\n" % (fc, os.path.join(d, fn))
					zfp.write(os.path.join(dirs[d], fn), arcname=os.path.join(d, fn))
				
		msg1 = "%d files successfully written to\n%s\n\n" % (fc, zipfile)
				
		dlg = wx.MessageDialog(parent, msg1 + msg2, 'Data backup successfully written', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
		
def restoreData(parent, settings):
		wildcard = "ZIP File (*.zip)|*.zip"
		dlg = wx.FileDialog(
			parent, message="Restore data files from ...", defaultDir=os.getcwd(),
			defaultFile="", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
			)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			zf = dlg.GetPath()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		if not is_zipfile(zf):
			dlg = wx.MessageDialog(parent,
				"File %s is not a valid zip file" % zf,
				"Not a zip file",
				wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return 
		
		fc = 0
		msg2 = ""
		with ZipFile(zf, 'r') as zfp:
			nl  = zfp.namelist()
			for fn in nl:
				d, f = os.path.split(fn)
				if d == TYPE_TRAIN:
					ddir = settings.traindir
				elif d == TYPE_ORDER:
					ddir = settings.orderdir
				elif d == TYPE_ENGINEER:
					ddir = settings.engineerdir
				elif d == TYPE_LOCO:
					ddir = settings.locodir
				else:
					ddir = None
					
				if ddir:
					data = zfp.read(fn)
					dfn = os.path.join(ddir, f)
					fc += 1
					msg2 += "%d: %s -> %s\n" % (fc, f, dfn)
					with open(dfn, "wb") as ofp:
						ofp.write(data)
						
		msg1 = "%d files restored from %s\n\n" % (fc, zf)
				
		dlg = wx.MessageDialog(parent, msg1 + msg2, 'Data restore successful', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()
		
