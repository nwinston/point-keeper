from threading import Thread
import time

class Timer:
	def __init__(self, fn, interval):
		self.fn = fn
		self.interval = interval
		self.running = False
		self.thread = None

	def start(self):
		self.running = True
		self.thread = Thread(target=self._loop)
		self.thread.start()

	def stop(self):
		self.running = False
		self.thread.join()

	def _loop(self):
		while self.running:
			self.fn()
			time.sleep(self.interval)