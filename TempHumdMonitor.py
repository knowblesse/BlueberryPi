from datetime import datetime, timedelta
import time
from pi_sht1x import SHT1x
import RPi.GPIO as GPIO
from smtplib import SMTP


class Ratsius:
    # Constants
    refresh_rate = 10 # measure the temp and humid every this minutes
    email_refractory_hours = 12 # hours
    critical_temp_low = 18
    critical_temp_high = 26
    critical_humd_low = 35
    critical_humd_high = 65

    last_mail_sent_time = datetime.today() - timedelta(hours=email_refractory_hours)

    # Mailing List
    #email_to = ['JiHoon <knowblesse@gmail.com>', 'ChangKo <toto10kr@gmail.com>', 'Sharon <spyeon@korea.ac.kr>','JY <dlwodyd488@naver.com>', 'Kyeongim <jgi040@gmail.com>']
    email_to = ['JiHoon <knowblesse@gmail.com>']
    # Email structure
    def sendEmail(self, message_number, temp, humid):
        id = "blueberry@korea.ac.kr"
        app_psw = "wqulegiadgpzvvsa"
        email_msg = [
            # Message 0 : Alert
            """from: Ratsius <blueberry@korea.ac.kr>\nto: %s\nsubject : [Ratsius] Alert
            
Alert!!!  
            
temperature : %s  
humidity : %s""" % (",".join(self.email_to), temp, humid),
# Message 1 : System Online
            """from: Ratsius <blueberry@korea.ac.kr>\nto: %s\nsubject : [Ratsius] System online
            
Ratsius(Rat + Celsius) System is now online!  
            
This system will notify you when the thermo-hygrostat is reached to the critical state.
To reduce the spam-mail hazard, the system will notify only once in "notification email refractory period", even though the machine is still in the critical state.
            
Current State : 
temperature : %s  
humidity : %s
            
----------------------Current Setting---------------------- 
refresh rate : %s minutes
normal temperature range : %s ~ %s
normal humidity range : %s ~ %s
notification email refractory period : %s hours
-----------------------------------------------------------
            
Please do NOT reply to this email, 
and if you have any questions about the system, please come to my admin's desk. 
Since there is no Manual, Reset button, and Reboot function, don't worry :D
            
Sincerely, 
            
Ratsius.""" % (",".join(self.email_to), temp, humid, self.refresh_rate,
               self.critical_temp_low, self.critical_temp_high, self.critical_humd_low, self.critical_humd_high, self.email_refractory_hours )]

        with SMTP("smtp.gmail.com", port = 587) as smtp:
            try:
                smtp.starttls()
                smtp.login(id, app_psw)
                smtp.sendmail(id, self.email_to, email_msg[message_number])
                smtp.close()
            except:
                print("error")

# Setup Email module
em = Ratsius()
# Setup Sensor
sensor = SHT1x(18,23, gpio_mode=GPIO.BCM)

# Send System online email
#em.sendEmail(1, sensor.read_temperature(), sensor.read_humidity())
# Run
while True:
        temp = sensor.read_temperature()
        humd = sensor.read_humidity()
        print('{0} Temp : {1}, Humd : {2}'.format(time.ctime(),temp,humd))
        if temp > em.critical_temp_high or temp < em.critical_temp_low:
            print("critical temperature!")
            if (datetime.today() - em.last_mail_sent_time).total_seconds() / (60*60) >= em.email_refractory_hours:
                em.sendEmail(0, str(temp) + "!!!", humd)
                em.last_mail_sent_time = datetime.today()
        elif humd > em.critical_humd_high or humd < em.critical_humd_low:
            print("critical humidity!")
            if (datetime.today() - em.last_mail_sent_time).total_seconds() / (60 * 60) >= em.email_refractory_hours:
                em.sendEmail(0, temp, str(humd) + "!!!")
                em.last_mail_sent_time = datetime.today()
        time.sleep(60*em.refresh_rate)
