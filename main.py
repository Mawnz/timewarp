from timewarp import TimeWarp, cv2, os
FILE_OUTPUT = 'output.avi'
height = 480
width = 640
	
if __name__ == '__main__':
	try:
	    os.remove(FILE_OUTPUT)
	except OSError:
	    pass

	cap = cv2.VideoCapture(0)
	tw = TimeWarp(cap)
	#tw.root.mainloop()