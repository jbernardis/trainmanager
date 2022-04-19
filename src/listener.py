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
		self.cbTrainSignal = None
		self.cbConnect = None
		self.cbDisconnect = None
		self.cbFailure = None
		self.cbClock = None
		self.cbBreaker = None
		self.cbMessage = None

		self.thread = threading.Thread(target=self.run)
		
	def start(self):
		self.thread.start()
		
	def kill(self, skipDisconnect=False):
		if skipDisconnect:
			self.cbDisconnect = None
			
		if self.isRunning:
			self.isRunning = False
			self.thread.join()
		
	def bind(self, cbConnect, cbDisconnect, cbFailure, cbTrainID, cbTrainSignal, cbClock, cbBreakers, cbMessage):
		self.cbConnect = cbConnect
		self.cbDisconnect = cbDisconnect
		self.cbFailure = cbFailure
		self.cbTrainID = cbTrainID
		self.cbClock = cbClock
		self.cbBreakers = cbBreakers
		self.cbMessage = cbMessage
		self.cbTrainSignal = cbTrainSignal
		
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
				if callable(self.cbMessage):
					self.cbMessage("Exception %s - terminating thread" % str(e))
				self.isRunning = False
				
			else:
				if self.isRunning:
					for b in bl:
						if b == "":
							continue
						
						if b.startswith("TrnTkr"):
							print("TrnTkr: (%s)" % b)
							loco = b[9:17].strip()
							train = b[17:25].strip()
							block = b[25:33].strip()
							if callable(self.cbTrainID):
								self.cbTrainID(train, loco, block)
										
						elif b.startswith("TrnSig"):
							print("TrnSig: (%s)" % b)
							loco = b[9:17].strip()
							slimit = b[25:29].strip()
							try:
								limit = int(slimit)
							except:
								limit = None
							if limit is not None:
								if callable(self.cbTrainSignal):
									self.cbTrainSignal(loco, limit)
							else:
								if callable(self.cbMessage):
									self.cbMessage("Unable to parse X speed from (%s)" % slimit)
									self.cbMessage("Message = (%s)" % b)

										
						elif b.startswith("TrainID"):
							print("TrainID: (%s)" % b)
							try:
								x = int(b[19:24].strip())
							except:
								if callable(self.cbMessage):
									self.cbMessage("Unable to parse X coordinate from (%s)" % b[19:24].strip())
									self.cbMessage("Message = (%s)" % b)
								x = None
							try:
								y = int(b[24:29].strip())
							except:
								if callable(self.cbMessage):
									self.cbMessage("Unable to parse Y coordinate from (%s)" % b[24:29].strip())
									self.cbMessage("Message = (%s)" % b)
								y = None
								
							if x is None or y is None:
								continue
							
							screen = b[9:19].strip()
							train = b[29:39].strip()
							if train.startswith("#"):
								loco = train[2:].strip()
								train = ""
							else:
								loco = ""
							for row, col, block in rrmap[screen]:
								if row == x and col == y:
									if callable(self.cbTrainID):
										self.cbTrainID(train, loco, block)
									break

						elif b.startswith("PSClock"):
							tm = b[9:19].strip()
							if callable(self.cbClock):
								self.cbClock(tm)
						elif b.startswith("CktBkr"):
							text = b[9:39].strip()
							if callable(self.cbBreakers):
								self.cbBreakers(text)
					
		if callable(self.cbMessage):
			self.cbMessage("Attempting socket close")
			
		try:
			self.skt.close()
		except Exception as e:
			if callable(self.cbMessage):
				self.cbMessage("Socket Close Failed: %s" % str(e))
			print("Socket Close Failed: %s" % str(e))
			
		if callable(self.cbMessage):
			self.cbMessage("socket close completed")
		
		if callable(self.cbDisconnect):
			if callable(self.cbMessage):
				self.cbMessage("sending disconnect")
			print("sending disconnect")
			self.cbDisconnect()
			
		if callable(self.cbMessage):
			self.cbMessage("Thread execution ended")
		print("Thread execution ended")
