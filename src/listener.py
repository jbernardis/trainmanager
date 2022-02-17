import socket
import threading

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

		self.thread = threading.Thread(target=self.run)
		
	def start(self):
		self.thread.start()
		
	def kill(self):
		if self.isRunning:
			self.isRunning = False
			self.thread.join()
		
	def bind(self, cbMessage, cbConnect, cbDisconnect, cbFailure):
		self.cbTrainID = cbMessage
		self.cbConnect = cbConnect
		self.cbDisconnect = cbDisconnect
		self.cbFailure = cbFailure
		
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
					
		self.isRunning = False
		try:
			self.skt.close()
		except:
			pass
		
		if callable(self.cbDisconnect):
			self.cbDisconnect()
					





