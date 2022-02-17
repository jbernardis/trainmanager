import socket
import threading

class Listener():
	def __init__(self, ip, port):
		self.failedSetup = False
		self.isRunning = False
		try:
			self.skt = socket.create_connection((ip, port))
		except TimeoutError:
			self.failedSetup = True
			return
		
		self.skt.settimeout(0.5)
		
		self.cbTrainID = None

		self.thread = threading.Thread(target=self.run)
		
	def start(self):
		if self.failedSetup:
			return
		
		self.thread.start()
		
	def kill(self):
		if self.isRunning:
			self.isRunning = False
			self.thread.join()
		
	def bind(self, cb):
		self.cbTrainID = cb
		
	def run(self):
		self.isRunning = True
		while self.isRunning:
			try:
				b = str(self.skt.recv(1024), 'utf-8')
				if len(b) == 0:
					self.skt.close()
					print("closing socket")
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
					





