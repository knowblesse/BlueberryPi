import numpy as np
import cv2 as cv
import time
import picamera
import picamera.array

from gpiozero import Button, LED

status_led = LED(23)

reset_button = Button(17, pull_up=False)
capture_button = Button(27, pull_up=False)
live_button = Button(22, pull_up=False)
signal = LED(14)
signal.off()

state = False
bgimage = []
status_led_state = False

num_retry = 0
max_retry = 3

while num_retry < max_retry:
    try:
        camera = picamera.PiCamera()
        camera.resolution = [640,480]
        camera.iso = 640
        camera.framerate = 30

        rawCapture = picamera.array.PiRGBArray(camera)

        camera.start_preview()
        time.sleep(5)
        camera.stop_preview()

        status_led.on()
        for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
            fr = frame.array
            if (reset_button.is_pressed):
                time.sleep(1)
                bgimage = cv.cvtColor(fr, cv.COLOR_BGR2GRAY)
            else:
                image = cv.cvtColor(fr, cv.COLOR_BGR2GRAY)
                if (len(bgimage) != 0 ):
                    
                    # Status LED blinking
                    if status_led_state:
                        status_led.off()
                    else:
                        status_led.on()
                    
                    status_led_state = not status_led_state
                    
                    diff_value = np.sum(cv.subtract(image, bgimage) > 50)
                    print(diff_value)
                    if(diff_value > 2000):
                        signal.on()
                        print("on")
                    else:
                        signal.off()
                        print("off")
                    time.sleep(0.5)            
                    if (live_button.is_pressed):
                        cv.imshow('live',image)
                        time.sleep(1)
            rawCapture.truncate(0)
    except:
        num_retry += 1
        # Signal Error
        for i in range(20):
            if status_led_state:
                status_led.off()
            else:
                status_led.on()
            
            status_led_state = not status_led_state
            time.sleep(0.1)
                    
