from timewarp import TimeWarp

video_format = cv2.VideoWriter_fourcc(*'FMP4')
FILE_OUTPUT = 'output.avi'
height = 480
width = 640
	
if __name__ == '__main__':
	cap = cv2.VideoCapture(0)
	tw = TimeWarp(cap)
	tw.root.mainloop()