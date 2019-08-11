import smtplib
from email import encoders  # 파일전송을 할 때 이미지나 문서 동영상 등의 파일을 문자열로 변환할 때 사용할 패키지
from email.mime.text import MIMEText   # 본문내용을 전송할 때 사용되는 모듈
from email.mime.multipart import MIMEMultipart   # 메시지를 보낼 때 메시지에 대한 모듈
from email.mime.application import MIMEApplication

def send_mail():

    print('Sending mail...')
    server=smtplib.SMTP('mail.skbroadband.com',25)
    server.ehlo()
    #server.starttls()
    server.ehlo()

    server.login('snocjs.bot@skbroadband.com','!Sk@broad2761')
    sent_from= 'snocjs.bot@skbroadband.com'
    addrs =['snocjs@skbroadband.com','pacemaker00@sk.com']
    subject = "SMTP test"
    text ='Please check the attachment.'

    body = MIMEText(text)
    msg=MIMEMultipart()
    msg['From']= sent_from
    msg['Subject'] = subject
    msg.attach(body)

#    with open(self.saveFile, "rb") as file:
#        part = MIMEApplication(file.read(), Name=basename(self.saveFile))
#        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(self.saveFile)
#        msg.attach(part)

    for to in addrs:
        msg['To'] = to
        server.sendmail(sent_from,to,msg.as_string())

    print('mail has sent')
    server.quit()


send_mail()