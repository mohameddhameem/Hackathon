#  Copyright (c) 2019.
#  This file is to compose and send email to the required participants
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import config

SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT_NO = config.SMTP_PORT_NO
EMAIL_ID = config.EMAIL_ID
EMAIL_PASSWORD = config.EMAIL_PASSWORD

class MailHelper:


    def sendEmail(self,to_email,subject,msg,meetingtitle,meetinginvited,meetingattendees,
                  meetingagenda,meetingsummary,meetingactions,transcript_path):
        #Lets initialize the connection to Google
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = EMAIL_ID
            message["To"] = to_email
            sender_email = EMAIL_ID
            receiver_email = to_email
            password = EMAIL_PASSWORD

            # Create the plain-text and HTML version of your message
            html = """\
            <html>
              <body>
                <p>Hi All,<br>
                <br>
                   Please find below attached meeting invite<br>
                   <table border=1>
                   <tr> <th>Meeting Title </th> <th>{meetingtitle}</th> </tr>
                   <tr> <td>Invited</td> <td> {meetinginvited} </td> </tr>
                   <tr> <td>Attendees</td> <td> {meetingattendees} </td> </tr>
                   <tr> <td>Agenda</td> <td> {meetingagenda} </td> </tr>
                   <tr> <td>Meeting Summary</td> <td> {meetingsummary} </td> </tr>
                   <tr> <td>Action Items</td> <td> {meetingactions} </td> </tr>
                   
                   </table>
                   <br>
                   <br>
                   The original transcript of this meeting is attached with this email for your reference.
                   Please reachout to meeting organizer if you have any question <br><br><br>
                   <a href="https://www.ubs.com">UBS</a> 
                   Generated for internal UBS Communications
                </p>
              </body>
            </html>
            """
            #Lets generate the template files
            html = html.format(meetingtitle=meetingtitle,meetinginvited = meetinginvited,
                               meetingattendees = meetingattendees,meetingagenda=meetingagenda,
                               meetingsummary=meetingsummary, meetingactions=meetingactions)

            part2 = MIMEText(html, "html")
            part3 = MIMEBase('application', "octet-stream")
            part3.add_header('Content-Disposition', 'attachment', filename="meeting_transcript.txt")
            part3.set_payload(open(transcript_path,"rb").read())
            # Add HTML/plain-text parts to MIMEMultipart message
            # The email client will try to render the last part first
            #message.attach(part1)
            message.attach(part2)
            message.attach(part3)

            # Create secure connection with server and send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )

        except Exception as e:
            raise e