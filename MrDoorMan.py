import numpy as np
import cv2 as cv
import time
import picamera
import picamera.array

with picamera.PiCamera() as camera:
    camera.start_preview()
    time.sleep(2)
    with picamera.array.PiRGBArray(camera) as stream:
        camera.capture(stream, format='bgr')
        # At this point the image is available as stream.array
        image = stream.array
        cv.imshow('test', image)
        k = cv.waitKey(0)
cv.destroyWindow('test')
