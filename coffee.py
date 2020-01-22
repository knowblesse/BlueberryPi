from gpiozero import Button, LED
import picamera as pc
import time
from datetime import datetime
import os

print("""
####################################################################
#          N  a  u  g  h  t  y     D  e  t  e  c  t  o  r          #
####################################################################
""")


button = Button(17) # pin number 3
led = LED(4)
led.off()

#save file location
loc = "../refrigerator/"
thr = 40 # sec

mycam = pc.PiCamera()
mycam.vflip = True
mycam.hflip = True

starttime = 0
isCapturing = False
isDumbdetected = False
filename = ""
while True:
	if not(isDumbdetected):
		if button.value == True: # lever pressed and waiting for the dumb
			if not(isCapturing): # currently not capturing -> start capture
				print("start capturing!")
				isCapturing = True
				# start capturing
				starttime = datetime.now().timestamp()
				mycam.start_preview()
				time.sleep(1)
				mycam.stop_preview()
				filename = datetime.now().strftime("%m-%d_%H:%M:%S.h264")
				mycam.start_recording(loc+filename)
			else: # currently capturing.
				if datetime.now().timestamp() - starttime > thr: # got the dumb!!!
					for i in range(10):
						print("No Coffee For YOU!!!!!")
					os.system('python3 sendEmail.py')
					print("noticifation email is sent!")
					mycam.stop_recording()
					print("stop capture")
					print("wating for reset")
					isCapturing = False
					isDumbdetected = True
		else:# button false
			if isCapturing: # in case where the lever is moved back to normal
				print("stop capturing")
				isCapturing = False
				mycam.stop_recording()
				os.system('rm ' + loc + filename)
	else: # wait for reset
		if button.value == False:
			isDumbdetected = False