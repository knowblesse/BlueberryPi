import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
from pathlib import Path
try:
    import serial
    from pi_sht1x import SHT1x
    import RPi.GPIO as GPIO
except ImportError:
    warnings.warn('Import Error. Probably not Raspberry Pi?')

class AirMonitor():
    def __init__(self, savePath='~/Desktop', debug=False):
        # Initialize
        self.win = tk.Tk()
        self.__init_gui__()
        self.__init_data__()
        self.__init_sensorReading__()
        if not debug:
            self.__init_sensor__()
        
        # Setup
        self.savePath = Path(savePath) 
        self.debug = debug
        self.start_time = datetime.now()
        self.graphMode = 'Temp'
        self.graphUpdated = False

        self.readInterval = 30 # data aquisition interval : seconds
        self.numRetry = 3 # maximum retry attempts for sensors
        self.numDatapoints = 24 # number of data points to plot

        self.updater()
        self.win.mainloop()

    def updater(self):
        processStartTime = datetime.now()
        if not self.debug:
            self.readData()
        else:
            self.readData_debug()
        self.appendData()
        self.saveData()
        self.updateLabel()
        if ((processStartTime.minute == 0) or (processStartTime.minute == 30)) and (not self.graphUpdated):
            self.updateGraph()
            self.graphUpdated = True
        else:
            self.graphUpdated = False
        delayTime = self.readInterval - (datetime.now() - processStartTime).total_seconds()
        print(delayTime)
        self.win.after(int(delayTime * 1000), self.updater)

    def updateLabel(self):
        self.tk_var_temp.set(f"{self.sensorReading['Temp'][0]:04.1f}℃")
        self.tk_var_humd.set(f"{self.sensorReading['Humd'][0]:04.1f}%")
        self.tk_var_pres.set(f"{self.sensorReading['Pres'][0]:.0f}mBar")
        self.tk_var_oxyg.set(f"{self.sensorReading['Oxyg'][0]:05.2f}%")
        self.tk_var_carb.set(f"{self.sensorReading['Carb'][0]:05.1f}ppm")

    def updateGraph(self):
        self.ax.cla()

        currentTime = datetime.now()

        # Find the right value of the 30 minute range
        """
        Data is averaged every 30 minutes.
        For example, data from [11:45 AM, 12:15 PM) is plotted as 12:00 PM data
        and data from [12:15 PM, 12:45 PM) is plotted as 12:30 PM data
        Algorithm first find the right end of the range. If it is 12:04 PM, this value is 11:45 AM
        and if it is 11:35 AM, the value is 11:15 AM.
        From this value, I subtracted 30 minutes and find out the whole datetime range to be plotted
        """
        if (currentTime.minute >= 15) and (currentTime.minute < 45):
            rightEnd = currentTime.replace(minute=15, second=0, microsecond=0)
        else:
            rightEnd = currentTime.replace(minute=45, second=0, microsecond=0)
            if currentTime.minute < 15:
                rightEnd -= timedelta(hours=1)

        timeRange = [] # Range in backward
        for i in range(self.numDatapoints+1):
            timeRange.append(rightEnd - i * timedelta(minutes=30))

        # Find the index2plot
        dataIndex = [] # Index in backward
        label2plot = [] # Label in forward
        for i in range(self.numDatapoints):
            indexResult = np.where(np.logical_and((self.DATA['Time'] < timeRange[i]).to_numpy(), (self.DATA['Time'].iloc[:] >= timeRange[i+1]).to_numpy()))[0]
            if len(indexResult) == 0:
                break
            else:
                dataIndex.append(indexResult[[0,-1]])
                label2plot.insert(0,(timeRange[i] - timedelta(minutes=15)).strftime('%H:%M'))

        # Check the data size
        if len(dataIndex) == 0:
            return

        # data2plot
        data2plot = self.__generateMeanData__(self.graphMode, dataIndex)

        # setup datatype specific parameter
        if self.graphMode == 'Temp':
            ylim = [10,35]
        elif self.graphMode == 'Humd':
            ylim = [10, 80]
        elif self.graphMode == 'Pres':
            ylim = [980, 1020]
        elif self.graphMode == 'Oxyg':
            ylim = [17, 21]
        elif self.graphMode == 'Carb':
            ylim = [200, 1000]
        else:
            ylim = [0, 1]

        self.ax.plot(data2plot, color='white', linewidth=3)
        self.ax.set_xticks([x for x in range(len(label2plot))])
        self.ax.set_xticklabels(label2plot, rotation=45)
        self.ax.set_ylabel(self.graphMode)
        self.ax.tick_params(colors='white')
        self.ax.yaxis.label.set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.set_ylim(ylim)
        self.graph.draw()

    def readData(self):
        # Reset reading validity
        self.sensorReading['Temp_Valid'] = False
        self.sensorReading['Humd_Valid'] = False
        self.sensorReading['Pres_Valid'] = False
        self.sensorReading['Oxyg_Valid'] = False
        self.sensorReading['Carb_Valid'] = False

        # O2 Sensor
        retry = 0
        for _ in range(self.numRetry):
            retry += 1
            self.serial_oxyg.write(bytes('%\r\n', encoding='ascii'))
            oxyg_data = self.serial_oxyg.read_until(b'\x0A')
            if len(oxyg_data) > 1:  # data received
                if oxyg_data[0] == ord('%'):  # No error
                    O2 = float(oxyg_data[1:])
                    self.sensorReading['Oxyg'] = O2
                    self.sensorReading['Oxyg_Valid'] = True
                    break
        self.__update_label_color__(self.label_oxyg_value,retry)

        # Pressure Sensor
        retry = 0
        for _ in range(self.numRetry):
            retry += 1
            self.serial_oxyg.write(bytes('P\r\n', encoding='ascii'))
            oxyg_data = self.serial_oxyg.read_until(b'\x0A')
            if len(oxyg_data) > 1:  # data received
                if oxyg_data[0] == ord('P'):  # No error
                    P = float(oxyg_data[1:])
                    self.sensorReading['Pres'] = P
                    self.sensorReading['Pres_Valid'] = True
                    break
        self.__update_label_color__(self.label_pres_value, retry)

        # CO2 Sensor
        retry = 0
        for _ in range(self.numRetry):
            self.serial_carb.write(b'\x42\x4d\xe3\x00\x00\x01\x72')  # Read Commend
            carb_data = self.serial_carb.read_until(size=12)

            if len(carb_data) == 12:
                chksum_high = int(sum(carb_data[:10]) / 256)
                chksum_low = sum(carb_data[:10]) % 256
                if not (chksum_high == carb_data[10] and chksum_low == carb_data[11]):
                    warnings.warn('Wrong CO2 Data : Checksum Error')
                else:
                    CO2 = carb_data[4] * 256 + carb_data[5]
                    self.sensorReading['Carb'] = CO2
                    self.sensorReading['Carb_Valid'] = True
                    break
        self.__update_label_color__(self.label_carb_value, retry)

        # Temp/Humd Sensor
        for _ in range(self.numRetry):
            try:
                TEMP = self.temp_sensor.read_temperature()
                HUMD = self.temp_sensor.read_humidity()
                self.sensorReading['Temp'] = TEMP
                self.sensorReading['Temp_Valid'] = True
                self.sensorReading['Humd'] = HUMD
                self.sensorReading['Humd_Valid'] = True
                self.__update_label_color__(self.label_temp_value, 0)
                self.__update_label_color__(self.label_humd_value, 0)
                break
            except:
                self.__update_label_color__(self.label_temp_value, self.numRetry)
                self.__update_label_color__(self.label_humd_value, self.numRetry)

        self.sensorReading['Time'] = datetime.now()

    def readData_debug(self):
        self.sensorReading['Time'] = datetime.now()
        self.sensorReading['Temp'] = np.random.randint(10) + 25
        self.sensorReading['Humd'] = np.random.randint(20) + 30
        self.sensorReading['Pres'] = np.random.randint(10) + 995
        self.sensorReading['Oxyg'] = np.random.randint(10)*0.1 + 19.5
        self.sensorReading['Carb'] = np.random.randint(400) + 300
        self.sensorReading['Temp_Valid'] = True
        self.sensorReading['Humd_Valid'] = True
        self.sensorReading['Pres_Valid'] = True
        self.sensorReading['Oxyg_Valid'] = True
        self.sensorReading['Carb_Valid'] = True

    def appendData(self):
        #if self.start_time.date != self.sensorReading['Time'].date:
        #    # New Day
        #    self.saveData()
        #    self.start_time = self.sensorReading['Time']
        #    self.__init_data__()
        self.DATA = self.DATA.append(self.sensorReading, ignore_index=True)

    def saveData(self):
        try:
            # save to the temp file
            fileName = f"AirMonData_{self.start_time.strftime('%m-%d_%H-%M')}"
            savePath = self.savePath / (fileName+'.tmp')
            self.DATA.to_csv(savePath, sep=',')
            # if success, overwrite to the original file 
            savePath.replace(savePath.parent / (fileName+'.csv'))
        except:
            warnings.warn('Failed to save data')

    def __init_gui__(self):
        self.win.title("AirMonitor")
        self.win.minsize(800,480)
        self.win.configure(bg='black')

        self.tk_var_temp = tk.StringVar()
        self.tk_var_humd = tk.StringVar()
        self.tk_var_oxyg = tk.StringVar()
        self.tk_var_carb = tk.StringVar()
        self.tk_var_pres = tk.StringVar()

        self.tk_var_temp.set("12.3 ℃")
        self.tk_var_humd.set("12.3 %")
        self.tk_var_oxyg.set("12.3 %")
        self.tk_var_carb.set("0123 ppm")
        self.tk_var_pres.set("0123 mBar")

        self.label_temp_value = tk.Label(self.win, textvariable=self.tk_var_temp, justify="center", fg='white', bg='black',
                                    font=("helvetica", 25))
        self.label_humd_value = tk.Label(self.win, textvariable=self.tk_var_humd, justify="center", fg='white', bg='black',
                                    font=("helvetica", 25))
        self.label_oxyg_value = tk.Label(self.win, textvariable=self.tk_var_oxyg, justify="center", fg='white', bg='black',
                                    font=("helvetica", 25))
        self.label_carb_value = tk.Label(self.win, textvariable=self.tk_var_carb, justify="center", fg='white', bg='black',
                                    font=("helvetica", 25))
        self.label_pres_value = tk.Label(self.win, textvariable=self.tk_var_pres, justify="center", fg='white', bg='black',
                                    font=("helvetica", 25))

        self.label_temp_value.bind('<Button-1>', lambda e, mode="Temp": self.__change_graphMode__(mode))
        self.label_humd_value.bind('<Button-1>', lambda e, mode="Humd": self.__change_graphMode__(mode))
        self.label_pres_value.bind('<Button-1>', lambda e, mode="Pres": self.__change_graphMode__(mode))
        self.label_oxyg_value.bind('<Button-1>', lambda e, mode="Oxyg": self.__change_graphMode__(mode))
        self.label_carb_value.bind('<Button-1>', lambda e, mode="Carb": self.__change_graphMode__(mode))

        label_temp = tk.Label(self.win, text="Temp", justify="center", fg='white', bg='black',
                              font=("helvetica", 18))
        label_humd = tk.Label(self.win, text="Humidity", justify="center", fg='white', bg='black',
                              font=("helvetica", 18))
        label_oxyg = tk.Label(self.win, text="Oxygen", justify="center", fg='white', bg='black', font=("helvetica", 18))
        label_carb = tk.Label(self.win, text="CO2", justify="center", fg='white', bg='black', font=("helvetica", 18))
        label_pres = tk.Label(self.win, text="Pressure", justify="center", fg='white', bg='black',
                              font=("helvetica", 18))

        label_temp.place(x=50, y=10)
        self.label_temp_value.place(x=30, y=60)

        label_humd.place(x=180, y=10)
        self.label_humd_value.place(x=170, y=60)

        label_pres.place(x=340, y=10)
        self.label_pres_value.place(x=310, y=60)

        label_oxyg.place(x=510, y=10)
        self.label_oxyg_value.place(x=500, y=60)

        label_carb.place(x=670, y=10)
        self.label_carb_value.place(x=630, y=60)

        figure = plt.Figure(figsize=(7.7, 3.4), dpi=100, tight_layout=True, facecolor="black")
        self.ax = figure.subplots(1, 1)
        self.ax.plot([1, 2, 3, 4, 5], 'r')
        self.ax.set_facecolor('black')
        self.ax.patch.set_facecolor('black')

        self.graph = FigureCanvasTkAgg(figure, self.win)
        self.graph.get_tk_widget().place(x=15, y=120)
        
    def __init_data__(self):
        self.DATA = pd.DataFrame(columns=['Time', 'Temp', 'Humd', 'Pres', 'Oxyg', 'Carb', 'Temp_Valid', 'Humd_Valid', 'Pres_Valid', 'Oxyg_Valid', 'Carb_Valid'])

    def __init_sensorReading__(self):
        self.sensorReading = pd.DataFrame(np.array([[0,0,0,0,0,0,0,0,0,0,0]]), columns=['Time', 'Temp', 'Humd', 'Pres', 'Oxyg', 'Carb', 'Temp_Valid', 'Humd_Valid', 'Pres_Valid', 'Oxyg_Valid', 'Carb_Valid'])

    def __init_sensor__(self):
        self.serial_oxyg = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        self.serial_carb = serial.Serial('/dev/ttyAMA1', 9600, timeout=1)
        self.temp_sensor = SHT1x(18, 23, gpio_mode=GPIO.BCM, vdd='5V', resolution='Low')
        self.serial_oxyg.write(bytes('M 1\r\n', encoding='ascii'))
        
    def __change_graphMode__(self, mode):
        self.graphMode = mode
        self.updateGraph()
        
    def __update_label_color__(self, label, retry):
        """
        update the color of the value label. yellow for the first failure, red for the continuous failure
        :param label: tk.Label
        :param retry: number of retry
        :return: 
        """
        if retry >= self.numRetry-1:
            if label['fg'] == 'white':
                label.config(fg='yellow')
            else:
                label.config(fg='red')
        else:
            label.config(fg='white')

    def __generateMeanData__(self, datatype, dataIndex):
        data2plot = np.zeros(len(dataIndex))
        for i, idx in enumerate(dataIndex):
            data2plot[i] = np.mean(self.DATA[datatype].iloc[idx[0]:idx[1]+1])
        return data2plot

app = AirMonitor(savePath='~/Desktop')
