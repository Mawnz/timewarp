import multiprocessing as mp
import Tkinter as tk
from PIL import Image
from PIL import ImageTk
import threading
import cv2
# https://www.pyimagesearch.com/2016/05/30/displaying-a-video-feed-with-opencv-and-tkinter/
#
class TimeWarp:
	def __init__(self, vs, output_path='output.avi'):
		self.vs = vs
		self.output_path = output_path
		self.frame = None
		self.process = None
		self.stopEvent = None

		self.root = tk.Tk()
		self.panel = None

		self.process = threading.Thread(target=self.capture, args=())
		self.process.start()

	def capture(self):
		try:
			while True:
				ret, self.frame = self.vs.read()
				# Change representation of image in order to display in PIL
				img = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
				img = Image.fromarray(img)
				img = ImageTk.PhotoImage(img)

				if self.panel is None:
					self.panel = tk.Label(image = img)
					self.panel.image = img
					self.panel.pack(side = "left", padx = 10, pady = 10)
				else:
					self.panel.configure(image = img)
					self.panel.image = img
		except RuntimeError, e:
			print('[INFO] Caught a RuntimeError')
	def onClose():
		self.vs.stop()
		self.root.quit()