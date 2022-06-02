
class ActiveTrain:
	def __init__(self, tid, tInfo, loco, ldesc, eng, block):
		self.tid = tid
		self.dir = tInfo["dir"]

		if tInfo["origin"]["loc"] is None:
			self.origin = ""
		elif tInfo["origin"]["track"] is None:
			self.origin = tInfo["origin"]["loc"]
		else:
			self.origin = "%s / %s" % (tInfo["origin"]["loc"], tInfo["origin"]["track"])

		if tInfo["terminus"]["loc"] is None:
			self.terminus = ""
		elif tInfo["terminus"]["track"] is None:
			self.terminus = tInfo["terminus"]["loc"]
		else:
			self.terminus = "%s / %s" % (tInfo["terminus"]["loc"], tInfo["terminus"]["track"])

		self.block = block
		self.loco = loco
		self.ldesc = ldesc
		self.engineer = eng
		self.throttle = None
		self.speed = 0
		self.limit = None
		self.highlight = 0
		self.time = 0

		self.sortAscending = False
		self.sortGroupDir = False
		self.sortKey = "time"
