import socket
import threading
from rrmap import rrmap

class Listener():
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		
		self.failedSetup = False
		self.isRunning = False
		
		self.cbTrainID = None
		self.cbConnect = None
		self.cbDisconnect = None
		self.cbFailure = None
		self.cbClock = None
		self.cbBreaker = None

		self.thread = threading.Thread(target=self.run)
		
	def start(self):
		self.thread.start()
		
	def kill(self, skipDisconnect=False):
		if skipDisconnect:
			self.cbDisconnect = None
			
		if self.isRunning:
			self.isRunning = False
			self.thread.join()
		
	def bind(self, cbConnect, cbDisconnect, cbFailure, cbTrainID, cbClock, cbBreakers):
		self.cbConnect = cbConnect
		self.cbDisconnect = cbDisconnect
		self.cbFailure = cbFailure
		self.cbTrainID = cbTrainID
		self.cbClock = cbClock
		self.cbBreakers = cbBreakers
		
	def run(self):
		try:
			self.skt = socket.create_connection((self.ip, self.port), timeout=10)
		except:  #TimeoutError:
			self.failedSetup = True
			if callable(self.cbFailure):
				self.cbFailure()
			return

		if callable(self.cbConnect):
			self.cbConnect()
					
		self.skt.settimeout(0.5)
		
		self.isRunning = True
		while self.isRunning:
			try:
				b = str(self.skt.recv(1024), 'utf-8')
				if len(b) == 0:
					self.isRunning = False
				bl = b.split("\r\n")

			except socket.timeout:
				pass
			except Exception as e:
				print("Exception %s - terminating thread" % str(e))
				self.isRunning = False
				
			else:
				if self.isRunning:
					for b in bl:
						if b == "":
							continue
						
						if b.startswith("TrnMgr"):
							train = b[9:19].strip()
							block = b[19:29].strip()
							loco = b[29:39].strip()
							if callable(self.cbTrainID):
								self.cbTrainID(train, loco, block)
										
						elif b.startswith("TrainID"):
							try:
								x = int(b[19:24].strip())
							except:
								print("Unable to parse X coordinate from (%s)" % b[19:24].strip())
								print("Message = (%s)" % b)
								x = None
							try:
								y = int(b[24:29].strip())
							except:
								print("Unable to parse Y coordinate from (%s)" % b[24:29].strip())
								print("Message = (%s)" % b)
								y = None
								
							if x is None or y is None:
								continue
							
							screen = b[9:19].strip()
							train = b[29:39].strip()
							if train.startswith("#"):
								loco = train[2:]
								train = ""
							else:
								loco = ""
							for row, col, block in rrmap[screen]:
								if row == x and col == y:
									if callable(self.cbTrainID):
										self.cbTrainID(train, loco, block)

						elif b.startswith("PSClock"):
							tm = b[9:19].strip()
							if callable(self.cbClock):
								self.cbClock(tm)
						elif b.startswith("CktBkr"):
							text = b[9:39].strip()
							if callable(self.cbBreakers):
								self.cbBreakers(text)
					
		try:
			self.skt.close()
		except:
			pass
		
		if callable(self.cbDisconnect):
			self.cbDisconnect()
					





