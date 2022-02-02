import configparser
import os
import wx

INIFILE = "trainmaster.ini"

def parseBoolean(val, defaultVal):
	lval = val.lower();
	
	if lval == 'true' or lval == 't' or lval == 'yes' or lval == 'y':
		return True
	
	if lval == 'false' or lval == 'f' or lval == 'no' or lval == 'n':
		return False
	
	return defaultVal

class Settings:
	def __init__(self, parent, folder):
		self.parent = parent
		
		self.inifile = os.path.join(folder, INIFILE)
		self.section = "trainmaster"	
		
		self.traindir = os.getcwd()
		self.trainfile = "trains.json"
		self.locosdir = os.getcwd()
		self.locosfile = "locos.json"
		self.engineerdir = os.path.join(os.getcwd(), "engineers")
		self.engineerfile = "engineers.txt"
		self.orderdir = os.path.join(os.getcwd(), "orders")
		self.orderfile = "order.txt"
		self.logdir = os.path.join(os.getcwd(), "logs")
		
		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			dlg = wx.MessageDialog(self.parent, "Settings file %s does not exist.  Using default values" % INIFILE,
	                               'File Not Found',
	                               wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			self.modified = True
			return

		msgs = []
		self.modified = False	
		if self.cfg.has_section(self.section):
			for opt, value in self.cfg.items(self.section):
				if opt == 'traindir':
					self.traindir = value
				elif opt == 'trainfile':
					self.trainfile = value
				elif opt == 'locosdir':
					self.locosdir = value
				elif opt == 'locosfile':
					self.locosfile = value
				elif opt == 'engineerdir':
					self.engineerdir = value
				elif opt == "engineerfile":
					self.engineerfile = value;
				elif opt == "orderdir":
					self.orderdir = value
				elif opt == "orderfile":
					self.orderfile = value
				elif opt == "logdir":
					self.logdir = value
				else:
					msgs.append("INI file: Unknown %s option: %s - ignoring" % (self.section, opt))
		else:
			msgs.append("INI file: missing %s section - assuming defaults" % self.section)
			self.modified = True
			
		if len(msgs) > 0:				
			dlg = wx.MessageDialog(self.parent, "\n".join(msgs),
	                               'Errors reading settings',
	                               wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return

	def setModified(self):
		self.modified = True
		
	def checkModified(self):
		return self.modified
		
	def save(self):
		try:
			self.cfg.add_section(self.section)
		except configparser.DuplicateSectionError:
			pass
		
		self.cfg.set(self.section, "traindir", str(self.traindir))
		self.cfg.set(self.section, "trainfile", str(self.trainfile))
		self.cfg.set(self.section, "locosdir", str(self.locosdir))
		self.cfg.set(self.section, "locosfile", str(self.locosfile))
		self.cfg.set(self.section, "engineerdir", str(self.engineerdir))
		self.cfg.set(self.section, "engineerfile", str(self.engineerfile))
		self.cfg.set(self.section, "orderdir", str(self.orderdir))
		self.cfg.set(self.section, "orderfile", str(self.orderfile))
		self.cfg.set(self.section, "logdir", str(self.logdir))

		try:		
			cfp = open(self.inifile, 'w')
		except:
			print("Unable to open settings file %s for writing" % self.inifile)
			return
		self.cfg.write(cfp)
		cfp.close()
		
		self.modified = False

