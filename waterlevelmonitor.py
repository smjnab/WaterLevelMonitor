import RPi.GPIO as GPIO
import time
import datetime
import smtplib  
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
 
###################################################################################################
#SETUP
###################################################################################################
GPIO.setmode(GPIO.BCM)

#Get two conntections to monitor when water elevates and gets critical.
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Count how many loops water has been at a level.
cNormal = 0
cWarning = 0
cCritical = 0

#Track time when water reaches different levels.
timeNormal = datetime.datetime.now()    #only for init
timeWarning = datetime.datetime.now()   #only for init
timeCritical = datetime.datetime.now()  #only for init
ẗimeDiff = datetime.datetime.now()      #only for init
timeDiffCritical = datetime.datetime.now()      #only for init

#Track if sent an email for this water level.
msgSent = False 

#Time to sleep when monitoring and after message. Switch out time.sleep to a proper sleep process for WiPy TODO.
monitorTick = 0.5       #Every .5 sec monitor count goes up 1, when reaching 10 water level confirmed.
afterMessageTick = 10   #Should be something like 15 minutes for real application.


###################################################################################################
#SEND MAIL
###################################################################################################
def SendMail(subject, body):

    global msgSent
    
    #In case I messed something up to avoid spam.
    if msgSent: return
    
    #Whole email section is a copy from AWS docs.
    SENDER = 'EDITME'  
    SENDERNAME = 'EDITME'
    RECIPIENT  = 'EDITME'
    RETURNPATH  = 'EDITME'
    USERNAME_SMTP = "EDITME"
    PASSWORD_SMTP = "EDITME"
    HOST = "email-smtp.eu-west-1.amazonaws.com"
    PORT = 587
    
    SUBJECT = subject
    
    BODY_TEXT = body
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>"""+subject+"""</h1>
      <p>"""+body+"""</p>
    </body>
    </html>"""

    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
    msg['To'] = RECIPIENT
    msg['Return-Path'] = RETURNPATH
    part1 = MIMEText(BODY_TEXT, 'plain')
    part2 = MIMEText(BODY_HTML, 'html')
    msg.attach(part1)
    msg.attach(part2)

    try:  
        server = smtplib.SMTP(HOST, PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(USERNAME_SMTP, PASSWORD_SMTP)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())
        server.close()
        
        msgSent = True
    except Exception as e:
        print ("Error: ", e)
    else:
        print ("Email sent!")

    #Print message to log. Leftover from testing.
    print(subject+body)


###################################################################################################
#REMOVE MICROSEC FROM TIME
###################################################################################################
def TimeStr(timeDiff):
    return str(timeDiff).split(".")[0]


###################################################################################################
#MONITOR CONNECTIONS LOOP.
###################################################################################################
while True:
    critical = GPIO.input(24)
    warning = GPIO.input(23)


    ###################################################################################################
    #WATER LEVEL CRITICAL
    ###################################################################################################
    if critical == False:
        cCritical += 1

        #Set time when reached critical and calculate how long it has been since normal.
        if cCritical == 10:
            timeCritical = datetime.datetime.now()
            timeDiff = timeCritical-timeWarning
            timeDiffCritical = timeCritical-timeNormal
            msgSent = False
            
            SendMail('Critical water level!', 'It took '+TimeStr(timeDiff)+' for water to rise from normal to critical. '
                 +'It has been '+TimeStr(timeDiffCritical)+' since water level was normal.')
            
            time.sleep(afterMessageTick)
            continue

        #Reset other counters to make sure they are always 0.
        cWarning = 0
        cNormal = 0
        
        time.sleep(monitorTick)


    ###################################################################################################
    #WATER LEVEL ELEVATED
    ###################################################################################################
    elif warning == False:
        cWarning += 1

        #Set time when reached elevated.
        if cWarning == 10:
            timeWarning = datetime.datetime.now()
            msgSent = False
            
        #Send dropped from critical to elevated message while level remains critical.
        if cCritical >= 10 and cWarning >= 10: 
            timeDiff = timeWarning-timeCritical
            SendMail('Warning, elevated water level.', 'It took '+TimeStr(timeDiff)+' for water to drop from critical to elevated.')
            cCritical = 0
            time.sleep(afterMessageTick)
            continue

        #Send reached critical message while level remains critical. 
        if cNormal >= 10 and cWarning >= 10:
            timeDiff = timeWarning-timeNormal
            SendMail('Warning, elevated water level.', 'It took '+TimeStr(timeDiff)+' for water to rise from normal to elevated.')
            cNormal = 0
            time.sleep(afterMessageTick)
            continue

        time.sleep(monitorTick)


    ###################################################################################################
    #WATER LEVEL NOMRAL
    ###################################################################################################
    else:
        cNormal += 1

        #Set time level reached normal and calculate how long it took to go from elevated to normal.
        if cNormal == 10:
            timeNormal = datetime.datetime.now()
            timeDiff = timeNormal-timeWarning
            msgSent = False
            
             #Send message level been normal since start of app.
            if timeDiff.total_seconds() <= 5: 
                SendMail('Normal water level.', 'Level has not been elevated since starting to monitor.')

            #Send message level back to normal from elevated.
            else:
                SendMail('Normal water level.', 'It took '+TimeStr(timeDiff)+' for water to drop from elevated to normal.')

            #Reset counters.
            cCritical = 0
            cWarning = 0
            
            time.sleep(afterMessageTick)
            continue
        
        time.sleep(monitorTick)
