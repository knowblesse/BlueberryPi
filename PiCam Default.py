import picamera as pc
import numpy as np

output_old = np.empty((900,900,3),dtype=np.uint8)
output_new = np.empty((900,900,3),dtype=np.uint8)

tempsum = 0

mycam = pc.PiCamera()
mycam.resolution = (800,800)
mycam.vflip = True
mycam.hflip = True

mycam.start_preview()

while True:
    mycam.capture(output_old,'rgb')
    tempsum = np.sum((output_new - output_old)**2)
    mycam.capture(output_new,'rgb')
    print(tempsum)
    if tempsum > 20000000:
        print('££££££££££££££££££££££')
