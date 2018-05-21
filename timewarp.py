import multiprocessing as mp
import Tkinter as tk
from PIL import Image
from PIL import ImageTk
import threading
import cv2
import time
import os
import subprocess as sp
import numpy as np
import sys
# import struct # For decoding the FOURCC double
# https://www.pyimagesearch.com/2016/05/30/displaying-a-video-feed-with-opencv-and-tkinter/
# https://github.com/Zulko/moviepy/blob/master/moviepy/video/io/ffmpeg_writer.py
class TimeWarp:
	def __init__(self, video_capture, fps=30, width=640, height=480, video_format='DIVX', output_path='output', FFMPEG_BIN='ffmpeg/bin/ffmpeg.exe', extension='avi'):
		self.video_capture_from_camera = video_capture
		# -466162819.0
		#fourcc = self.video_capture_from_camera.get(cv2.CAP_PROP_FOURCC)
		#fourcc = struct.pack('<i', fourcc)
		#self.video_format = cv2.VideoWriter_fourcc(*video_format)
		#self.video_writer = cv2.VideoWriter(output_path, self.video_format, fps, (width, height))
		self.video_capture_from_file = cv2.VideoCapture(output_path)
		self.output_path = output_path
		self.extension = extension
		self.width = width
		self.height = height
		self.frame = None
		self.record = None
		self.play = None
		self.stopEvent = None

		self.root = tk.Tk()
		self.panel = None

		self.stopEvent = threading.Event()
		# http://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/
		self.command_capture = [ FFMPEG_BIN,
			'-y', # (optional) overwrite output file if it exists
			'-f', 'rawvideo',
			'-vcodec','rawvideo',
			'-s', '%dx%d' % (self.width, self.height), # size of one frame
			'-pix_fmt', 'rgb24',
			'-r', '%.02f' % fps, # frames per second
			'-i', '-', # The imput comes from a pipe
			'-an', # Tells FFMPEG not to expect any audio
			'-vcodec', 'libxvid',
			'b', '3000k',
			'%s.avi' % self.output_path]

		self.cmd = [FFMPEG_BIN,
			'-y',
			'i', '-',
			'-an',
			'-vcodec', 'libx264',
			'-b', '3000',
			'-s', '%dx%d' % (self.width, self.height),
			'-r', '%.02f' % fps,
			'%s.avi' % self.output_path]

		self.c_cap = [FFMPEG_BIN,
			'-y',
			'-f', 'rawvideo',
			'-vcodec', 'rawvideo',
			'-s', '%dx%d' % (self.width, self.height),
			'-pix_fmt', 'rgb24',
			'-r', '%.02f' % fps,
			'-i', '-', '-an',
			'-vcodec', 'libxvid',
			'-preset', 'fast',
			#'-crf', '17',
			'-b:v', '1M',
			'-minrate', '1M',
			'-maxrate', '1M',
			'-bufsize', '2M',
			#'-tune', 'zerolatency'
			#'-pix_fmt', 'yuv420p',
			'%s.%s' % (self.output_path, self.extension)]

		self.pipe_capture = sp.Popen(self.c_cap, stdin=sp.PIPE)
		#self.pipe_capture.stdin = Unbuffered(self.pipe_capture.stdin)
		# Thread that captures video
		self.record = threading.Thread(target=self.capture, args=())
		self.record.start()
		time.sleep(2)
		# We ask FFMPEG to now read file and direct it's ouput to Python
		self.c_play = [
			FFMPEG_BIN, 
			'-i', '%s.%s' % (self.output_path, self.extension), 
			'-f', 'image2pipe',
			#'-r', '%.02f' % fps,
			#'-f', 'rawvideo',
			#'-s', '%dx%d' % (self.width, self.height),
			#'-framerate', '1', 
			'-vcodec', 'rawvideo', 
			'-pix_fmt', 'rgb24', 
			#'-r', '%.02f' % fps,
			'-']
		self.pipe_play = sp.Popen(self.c_play, stdout = sp.PIPE, bufsize=10**8)

		# Thread that plays video
		self.play = threading.Thread(target=self.playback, args=())
		self.play.start()

		# Callback when we close window
		#self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	def playback(self):
			#while not self.stopEvent.is_set():
			while True:
				#ret, self.frame = self.video_capture_from_file.read()
				# Change representation of image in order to display in PIL
				#img = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
				#img = Image.fromarray(img)
				#img = ImageTk.PhotoImage(img)
				raw_img = self.pipe_play.stdout.read(self.width*self.height*3)
				img = np.fromstring(raw_img, dtype='uint8')
				img = img.reshape((self.height, self.width, 3))
				img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
				cv2.imshow('frame', img)
				self.pipe_play.stdout.flush()
				#if self.panel is None:
					#self.panel = tk.Label(image = img)
					#self.panel.image = img
					#self.panel.pack(side = "left", padx = 10, pady = 10)
				#else:
					#self.panel.configure(image = img)
					#self.panel.image = img
				
		#try:

		#except RuntimeError, e:
		#	print('[INFO] Caught a RuntimeError')

	def capture(self):
		c = 0
		while not self.stopEvent.is_set():
			# Grab next frame
			ret, frame = self.video_capture_from_camera.read()
			# To correct colorspace
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			# Convert it to string
			a = frame.tostring()
			#write
			self.pipe_capture.stdin.write(a)
			#self.pipe_capture.stdin.flush()
			#c = c + 1

		#self.pipe_capture.stdin.close()
		#self.pipe_capture.wait()

	def onClose(self):
		self.stopEvent.set()
		self.video_capture_from_camera.release()
		#self.video_writer.release()
		self.root.quit()

class Unbuffered(object):
	def __init__(self, stream):
		self.stream = stream
	def write(self, data):
		self.stream.write(data)
		self.stream.flush()
	def writelines(self, datas):
		self.stream.writelines(datas)
		self.stream.flush()
	def __getattr__(self, attr):
		return getattr(self.stream, attr)
