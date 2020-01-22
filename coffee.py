from gpiozero import Button, LED
import picamera as pc
import time
from datetime import datetime
import os

print("""
                           _                       _                                          
                          | |     _               | |        _                 _              
   ____  _____ _   _  ____| |__ _| |_ _   _     __| |_____ _| |_ _____  ____ _| |_ ___   ____ 
  |  _ \(____ | | | |/ _  |  _ (_   _) | | |   / _  | ___ (_   _) ___ |/ ___|_   _) _ \ / ___)
  | | | / ___ | |_| ( (_| | | | || |_| |_| |  ( (_| | ____| | |_| ____( (___  | || |_| | |    
  |_| |_\_____|____/ \___ |_| |_| \__)\__  |   \____|_____)  \__)_____)\____)  \__)___/|_|    
                    (_____|          (____/                                                   """)


button = Button(17) # pin number 3
led = LED(4)
led.off()

#save file location
loc = "../refrigerator/"
thr = 10 # sec

mycam = pc.PiCamera()
mycam.vflip = True
mycam.hflip = True

starttime = 0
isCapturing = False
filename = ""
while True:
    if button.value == True:
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
        else:
            if datetime.now().timestamp() - starttime > thr: # got the dumb!!!
                print("dumb!")
                led.on()
                time.sleep(0.5)
                led.off()
                time.sleep(0.5)
                led.on()
                time.sleep(0.5)
                led.off()
                mycam.stop_recording()
                print("stop capture")
                time.sleep(3)
                isCapturing = False

    else:
        if isCapturing:
            print("stop capturing")
            isCapturing = False
            mycam.stop_recording()
            os.system('rm ' + loc + filename)