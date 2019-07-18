import board
import busio
import adafruit_am2320
import time
from tkinter import *
import tkinter.messagebox
import matplotlib.pyplot as plt
import numpy as np

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_am2320.AM2320(i2c)
counter = 4
tot_temp = 0
tot_humd = 0

arr_temp = np.zeros([10,1])

while True:
        tot_temp += sensor.temperature
        tot_humd += sensor.relative_humidity
        time.sleep(60*15)
        counter = counter + 1
        if counter ==5 :
                t = time.ctime()
                print('{0} Temp : {1}, Humd : {2}'.format(t,tot_temp/4, tot_humd/4))
                #arr_temp = np.append(arr_temp[1:],tot_temp/4)
                #plt.plot(arr_temp)
                #plt.ylim([15,35])
                tot_temp = 0
                tot_humd = 0
                counter = 1
	
