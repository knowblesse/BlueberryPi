# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 19:27:51 2017

@author: Jeong Ji Hoon
@ Knowblesse

Description:
    Fetch HTML data from the JoN Web archive and Save to .txt
    JoN archive access permission is needed.
    Only use this script on university's network.
"""
# Import Modules
import urllib3
from html.parser import HTMLParser
from smtplib import SMTP
import time

id = "bluewaves9@gmail.com"
app_psw = "adgnqtjinwrtitr"

email_to = ["knowblesse@gmail.com"]
email_subject = "[New] Alert!"
email_body = "New Post!!!"
email_msg = """\
From: %s
To: %s
Subject: %s

%s
""" % ("Mimir", ",".join(email_to), email_subject, email_body)



############## C L A S S E S ##############

""" Abstract URL Parser """


class CustomParser(HTMLParser):
    # Get URL of Abstracts
    def __init__(self):
        HTMLParser.__init__(self)
        self.TableFlag = False  # Flag for table
        self.TDFlag = False
        self.NewFlag = False

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if ('class', 'm-table m-board') in attrs:
                self.TableFlag = True
        # Get Abstract Link
        if self.TableFlag:
            if tag == 'td':
                self.TDFlag = True

    def handle_data(self, data):
        if self.TableFlag and self.TDFlag:
            self.TableFlag = False
            if data == '7':
                self.NewFlag = True


parser = CustomParser()

while not parser.NewFlag:
    url = 'https://www.nrf.re.kr/biz/info/notice/list?menu_no=378&biz_no=440'
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    data = r.data.decode('utf-8')

    # Get Abstract URL Data

    parser.feed(data)
    if parser.NewFlag:
        with SMTP("smtp.gmail.com", port=587) as smtp:
            try:
                smtp.starttls()
                smtp.login(id, app_psw)
                smtp.sendmail(id, email_to, email_msg)
                smtp.close()

                print("DONE")
            except:
                print("error")


    time.sleep(1)