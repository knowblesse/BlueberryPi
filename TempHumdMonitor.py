from datetime import datetime, timedelta
import time
#import board
#import busio
#import adafruit_am2320
from smtplib import SMTP

# Constants
refresh_rate = 10 # measure the temp and humid every this minutes
email_refractory_hours = 3 # hours
critical_temp_low = 20
critical_temp_high = 26
critical_humd_low = 35
critical_humd_high = 60

last_mail_sent_time = datetime.today() - timedelta(hours=email_refractory_hours)

# Mailing List
mlist = ['Ji Hoon <knowblesse@gmail.com>']

# Email structure
def sendAlertEmail(email_to, temp, humid):
    id = "bluewaves9@gmail.com"
    app_psw = "hweoecydrbrjxwzx"
    email_msg = \
"""from: Ratsius <knowblesse@gmail.com>\nto: %s\nsubject : [temp/humid] status alert\n

thermo-hygrostat alert!!!  
temperature : %s  
humidity : %s""" % (",".join(email_to), temp, humid)

    with SMTP("smtp.gmail.com", port = 587) as smtp:
        try:
            smtp.starttls()
            smtp.login(id, app_psw)
            smtp.sendmail(id, email_to, email_msg)
            smtp.close()
        except:
            print("error")

# Setup Sensor
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_am2320.AM2320(i2c)

# Send Test Mail
sendAlertEmail(mlist, sensor.temperature, sensor.relative_humidity)
# Run
while True:
        temp = sensor.temperature
        humd = sensor.relative_humidity
        print('{0} Temp : {1}, Humd : {2}'.format(time.ctime(),temp,humd))
        if temp > critical_temp_high or temp < critical_temp_low:
            print("critical temperature!")
            if (datetime.today() - last_mail_sent_time).total_seconds() / (60*60) >= email_refractory_hours:
                sendAlertEmail(mlist, str(temp) + "!!!", humd)
                last_mail_sent_time = datetime.today()
        elif humd > critical_humd_high or humd < critical_humd_low:
            print("critical humidity!")
            if (datetime.today() - last_mail_sent_time).total_seconds() / (60 * 60) >= email_refractory_hours:
                sendAlertEmail(mlist, temp, str(humd) + "!!!")
                last_mail_sent_time = datetime.today()
        time.sleep(60*refresh_rate)