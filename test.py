import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

s = smtplib.SMTP('mail.usg-election.com', 587)
s.ehlo()
s.starttls()
s.login('comelec@usg-election.com', 'BZL-LAcUaPa1Vs5b')

subject = '[COMELEC] Election is now starting'
text = '''\
DLSU Comelec is inviting to you to vote in the elections.
Voter ID: 11827211
Voter Key: hi
To vote, go to this link: https://usg-election.dlsu.edu.ph/login
    '''

#Setting Email Parameters
msg             = MIMEMultipart('alternative')
msg['From']     = 'DLSU COMELEC<comelec@usg-election.com>'
msg['To']       = '11827211@dlsu.edu.ph'
msg['Subject']  = subject

#Email Body Content
fp = open('email_template.html', 'r')
HTML_STR = fp.read()
fp.close()

html = HTML_STR
html = html.replace('11xxxxxx', '11827211', 2)
html = html.replace('xxxxxxxx', 'HEELLOO00', 1)

#Add Message To Email Body
fp = open('ComelecLogo.png', 'rb')
img = MIMEImage(fp.read())
fp.close()
img.add_header('Content-ID', '<logo>')

msg.attach(MIMEText(text, 'text'))
msg.attach(MIMEText(html, 'html'))
msg.attach(img)

try:
    s.send_message(msg)
except Exception as e:
    print(e)
    print('Did not send')

s.quit()