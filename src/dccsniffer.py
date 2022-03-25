import threading
import serial

class DCCSniffer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.tty = None
		self.baud = None
		self.port = None
		self.isRunning = False
		self.endOfLife = False
		self.cbMessage = None
		self.cbClosed = None
		
	def bind(self, cbMessage, cbClosed):
		self.cbMessage = cbMessage
		self.cbClosed = cbClosed

	def connect(self, tty, baud, timeout):
		self.tty = tty
		self.baud = baud
		try:
			self.port = serial.Serial(port=self.tty, baudrate=self.baud, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, timeout=timeout)
		except serial.SerialException:
			self.port = None
			raise
		self.start()

	def kill(self):
		self.isRunning = False

	def isKilled(self):
		return self.endOfLife
		
	def run(self):
		self.isRunning = True
		while self.isRunning:
			if self.port is None or not self.port.is_open:
				self.isRunning = False
			else:
				try:
					c = self.port.read_until()
				except serial.SerialException:
					self.port = None
					self.isRunning = True
				
				if len(c) != 0:
					if callable(self.cbMessage):
						s = str(c, 'UTF-8')
						self.cbMessage(s.split())

		try:
			self.port.close()
		except:
			pass
				
		self.endOfLife = True
		if callable(self.cbClosed):
			self.cbClosed()


