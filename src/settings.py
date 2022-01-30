import configparser
import os

INIFILE = "trainmaster.ini"

def parseBoolean(val, defaultVal):
	lval = val.lower();
	
	if lval == 'true' or lval == 't' or lval == 'yes' or lval == 'y':
		return True
	
	if lval == 'false' or lval == 'f' or lval == 'no' or lval == 'n':
		return False
	
	return defaultVal

class Settings:
	def __init__(self, folder):
		self.inifile = os.path.join(folder, INIFILE)
		self.section = "trainmaster"	
		
		self.traindir = os.getcwd()
		self.trainfile = "trains.json"
		self.engineerdir = os.getcwd()
		self.engineerfile = "engineers.txt"
		self.orderdir = os.getcwd()
		self.orderfile = "order.txt"
		
		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			print("Settings file %s does not exist.  Using default values" % INIFILE)
			
			self.modified = True
			return

		self.modified = False	
		if self.cfg.has_section(self.section):
			for opt, value in self.cfg.items(self.section):
				if opt == 'traindir':
					self.traindir = value
				elif opt == 'trainfile':
					self.trainfile = value
				elif opt == 'engineerdir':
					self.engineerdir = value
				elif opt == "engineerfile":
					self.engineerfile = value;
				elif opt == "orderdir":
					self.orderdir = value
				elif opt == "orderfile":
					self.orderfile = value
				else:
					print("Unknown %s option: %s - ignoring" % (self.section, opt))
		else:
			print("Missing %s section - assuming defaults" % self.section)				

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
		self.cfg.set(self.section, "engineerdir", str(self.engineerdir))
		self.cfg.set(self.section, "engineerfile", str(self.engineerfile))
		self.cfg.set(self.section, "orderdir", str(self.orderdir))
		self.cfg.set(self.section, "orderfile", str(self.orderfile))

		try:		
			cfp = open(self.inifile, 'w')
		except:
			print("Unable to open settings file %s for writing" % self.inifile)
			return
		self.cfg.write(cfp)
		cfp.close()
		
		self.modified = False

