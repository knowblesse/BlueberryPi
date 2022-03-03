import tkinter as tk
from pi_sht1x import SHT1x
import RPi.GPIO as GPIO


class SHT_go():
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("SHT_go")
        self.win.minsize(500, 250)
        self.win.configure(bg='black')
        self.tk_var_temp = tk.StringVar()
        self.tk_var_humd = tk.StringVar()
        self.tk_var_temp.set("0")
        self.tk_var_humd.set("0")
        label_temp = tk.Label(self.win, textvariable=self.tk_var_temp, fg='white', bg='black', font=("helvetica", 50))
        label_humd = tk.Label(self.win, textvariable=self.tk_var_humd, fg='white', bg='black', font=("helvetica", 50))
        label_temp.place(x=60, y=30)
        label_humd.place(x=260, y=30)
        self.sensor = SHT1x(18,23,gpio_mode=GPIO.BCM)
        self.updater()
        self.win.mainloop()
    def updater(self):
        self.tk_var_temp = self.sensor.read_temperature()
        self.tk_var_humd = self.sensor.read_humidity()
        self.tk_var_temp.set('{:.3}'.format(self.tk_var_temp))
        self.tk_var_humd.set('{:.3}'.format(self.tk_var_humd))
        self.win.after(1000, self.updater)

app = SHT_go()
