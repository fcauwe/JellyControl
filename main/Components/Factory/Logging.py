from Components import Component
from threading import Timer
import logging, logging.config
import datetime, pytz, time
# module for forward event
import urllib2
# module for send email
import smtplib
from email.mime.text import MIMEText
# error tracing
import sys,traceback,os.path



class event2csv(Component.generic):
  Name = 'event2csv'
  sinkList = ['In']
  sourceList = []
  defaultState={}
  defaultConfig={'filename':'log.csv','timezone':'Europe/Brussels','minTimeBetween':'60'}
  time_of_last_value=0

  def __init__(self,compid):
    Component.generic.__init__(self,compid)

  def catchEvent(self,event,value):
    ## Avoid logging to much values
    if (self.time_of_last_value <= int(time.time())):
      self.time_of_last_value = int(time.time())+int(self.getConfigVariable("minTimeBetween"))

      tz=pytz.timezone(self.getConfigVariable("timezone"))
      current_time = datetime.datetime.now(tz).strftime("%Y/%m/%d %H:%M:%S") 
      f = open("logging/" + self.getConfigVariable("filename"), 'a')
      f.write( current_time + "," + str(value["value"]) + '\n')
      f.close()


class TimerEvent(Component.generic):
  Name = 'TimerEvent'
  sinkList = []
  sourceList = ['Out']
  defaultState={}
  defaultConfig={'delay':2}
  timer_running=False

  def __init__(self,compid):
    Component.generic.__init__(self,compid)

  def doEvent(self):
    if (not self.timer_running):
      #create a timer
      self.timer_running=True
    else:
      self.generateEvent('Out',{'value':True})
    
    self.t = Timer(float(self.getConfigVariable("delay")), self.doEvent)
    self.t.start()


  def init(self):
    self.doEvent()


# component	KeukenBarLicht
# event	Toggle
# jsoncallback	jQuery191007434058361624563_1419249219018
# value	True

class ForwardEvent(Component.generic):
  Name = 'ForwardEvent'
  sinkList = ['In']
  sourceList = []
  defaultState={}
  defaultConfig={'host':'http://localhost:8080/', 'interface':'panel.sendEvent.json','component':'proxy','event':'In','user':'tester','password':'','minTimeBetween':'2'}
  time_of_last_value=0

  def __init__(self,compid):
    Component.generic.__init__(self,compid)

  def catchEvent(self,event,value):
    if (self.time_of_last_value <= int(time.time())):
      self.time_of_last_value = int(time.time())+int(self.getConfigVariable("minTimeBetween"))

      try:
        # Create an OpenerDirector with support for Basic HTTP Authentication...
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='dotControl',
                                  uri=self.getConfigVariable("host"),
                                  user=self.getConfigVariable("user"),
                                  passwd=self.getConfigVariable("password"))
        opener = urllib2.build_opener(auth_handler)
        # ...and install it globally so it can be used with urlopen.
        urllib2.install_opener(opener)
        urllib2.urlopen(self.getConfigVariable("host") + self.getConfigVariable("interface") 
                        + '?jsoncallback=123&component=' + self.getConfigVariable("component")
                        + '&event=' + self.getConfigVariable("event")
                        + '&value=' + str(value["value"]))
       


      except Exception, e:
        logger=logging.getLogger("main")
        tb = traceback.extract_tb(sys.exc_info()[2])[-1]      
        logger.error("Could not execute " + event[0] + " (" + event[1] + "): "
                      + e.message + " (" +os.path.basename(tb[0]) + ":" + str(tb[1])+ ").")

        logger.error("Could not connect to remote host " + self.getConfigVariable("host") + ").")


class SendEmail(Component.generic):
  Name = 'ForwardEvent'
  sinkList = ['In']
  sourceList = []
  defaultState={}
  defaultConfig={'smtp':'smtp.dummy.com', 'from':'dummy@host.tld','to':'you@host.tld','subject':'email alert','content':'hi, <br>you have mail!<br> Jellycontrol','minTimeBetween':'10'}
  time_of_last_value=0

  def __init__(self,compid):
    Component.generic.__init__(self,compid)

  def catchEvent(self,event,value):
    if (value["value"] == True ) :
      if (self.time_of_last_value <= int(time.time())):
        self.time_of_last_value = int(time.time())+int(self.getConfigVariable("minTimeBetween"))

        try:
          msg = MIMEText(self.getConfigVariable("content").replace("<br>", "\n"))
          msg['Subject'] = self.getConfigVariable("subject")
          msg['From'] = self.getConfigVariable("from")
          msg['To'] = self.getConfigVariable("to")

          s = smtplib.SMTP(self.getConfigVariable("smtp"))
          s.sendmail(self.getConfigVariable("from"), self.getConfigVariable("to").split(","), msg.as_string())
          s.quit()

        except Exception, e:
          logger=logging.getLogger("main")
          tb = traceback.extract_tb(sys.exc_info()[2])[-1]      
          logger.error("Could not execute " + event[0] + " (" + event[1] + "): "
                      + e.message + " (" +os.path.basename(tb[0]) + ":" + str(tb[1])+ ").")

          logger.error("Could not send email with " + self.getConfigVariable("smtp") + " to " + self.getConfigVariable("to")  +  ".")





