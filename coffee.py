from gpiozero import Button
import picamera as pc
import time

button = Button(3); # pin number 3

#save file location

# 누르면 찍기 시작.
# 특정 시간이 지나면 save 및 알람!

mycam = pc.PiCamera()
mycam.resolution = (800,800)
mycam.vflip = True
mycam.hflip = True

starttime = 0;
while ture:
	if button.value == True:
		# start capturing
		mycam.start_preview()
		mycam.capture(output_old,'rgb')






