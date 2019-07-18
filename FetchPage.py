# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 19:00:00 2019

@author: Jeong Ji Hoon
@ Knowblesse

Description:
    Fetch HTML data from the Printer Site and get tot Num of Pages printed
"""
# Import Modules
import urllib3
from html.parser import HTMLParser
import tkinter as tk
import time

############## C L A S S E S ##############

""" Abstract URL Parser """
class PageParser(HTMLParser):
    # Parse Used Pages
    def __init__(self):
        HTMLParser.__init__(self)
        self.FoundClassNum = 0
        self.IsData = False
    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if ('class', 'hpPageText') in attrs:
                self.FoundClassNum = self.FoundClassNum + 1
                self.IsData = True

    def handle_data(self,data):
        if self.IsData:
            self.IsData = False
            if self.FoundClassNum == 20:
                self.pageNum = data


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.label = tk.Label(self)
        self.label["text"] = ""
        self.label.pack(side="top")
        self.label.config(font=("Courier",30))
        self.label.after(1000, self.refreshLabel)


    def refreshLabel(self):
        # Setup URL Connection
        url = 'https://163.152.86.220/hp/device/this.LCDispatcher?nav=hp.Usage'
        urllib3.disable_warnings()
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        data = r.data.decode('utf-8')

        # Get Abstract URL Data
        parser = PageParser()
        parser.feed(data)
        numpage = int(parser.pageNum.replace(',','')) - 217550

        # Update
        self.label["text"] = "사용 페이지\n" + str(numpage)
        self.label.after(3000, self.refreshLabel)

root = tk.Tk()
app = Application(master=root)
app.mainloop()