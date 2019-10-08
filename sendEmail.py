from smtplib import SMTP

id = "bluewaves9@gmail.com"
app_psw = ""

email_to = ["knowblesse@gmail.com"]
email_subject = "[Mimir] Temp-Humid Sensor Report"
email_body = ""
email_msg = """\
From: %s
To: %s
Subject: %s

%s
""" % ("Mimir", ",".join(email_to), email_subject, email_body)

with SMTP("smtp.gmail.com", port = 587) as smtp:
    try:
        smtp.starttls()
        smtp.login(id, app_psw)
        smtp.sendmail(id, email_to, email_msg)
        smtp.close()

        print("DONE")
    except:
        print("error")
