
class ActiveTrain:
	def __init__(self, tid, tInfo, loco, ldesc, eng, block):
		self.tid = tid
		self.dir = tInfo["dir"]
		self.origin = tInfo["origin"]
		self.terminus = tInfo["terminus"]
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
