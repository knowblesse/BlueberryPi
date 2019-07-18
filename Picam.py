import picamera
import os


TIME = 60

mycam = picamera.PiCamera()
mycam.resolution = [500,500]

mycam.start_preview()


    
