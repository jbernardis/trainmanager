import socket
import threading
import time
from rrmap import rrmap

class Listener():
	def __init__(self, ip, port):
		#self.skt = socket.create_connection((ip, port))
		#self.skt.settimeout(0.5)
		self.fp = open("disp.log", "r")
		
		self.cbTrainID = None

		self.thread = threading.Thread(target=self.run)
		
	def start(self):
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
				b = self.fp.readline()
				#b = str(self.skt.recv(1024), 'utf-8')
				if len(b) == 0:
					#self.skt.close()
					self.isRunning = False
					
			except Exception as e:
				print(e)
			#except socket.timeout:
				#pass
			else:
				if self.isRunning and b.startswith("TrainID"):
					screen = b[9:19].strip()
					x = int(b[19:24].strip())
					y = int(b[24:29].strip())
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
							break
					time.sleep(1)
					
		self.isRunning = False
					





