import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class mail_class():
    def mail_method(self, email, results_json_path, body_name):
        email_user = 'skolix.ml@gmail.com'
        email_password = 'Ajaynit@1.'
        email_send = email
        subject = 'sending a mail with an attachment'
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_send
        msg['Subject'] = subject
        body = body_name
        msg.attach(MIMEText(body,'plain'))
        filename1 = results_json_path
        attachment  =open(filename1,'rb')
        part = MIMEBase('application','octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',"attachment; filename= "+os.path.basename(filename1))
        msg.attach(part)
        text = msg.as_string()
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(email_user,email_password)
        server.sendmail(email_user,email_send,text)
        server.quit()
    def mail2_method(self, email, message):
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("skolix.ml@gmail.com", "Ajaynit@1.")
        s.sendmail("sender_email_id", email, message)
        s.quit()