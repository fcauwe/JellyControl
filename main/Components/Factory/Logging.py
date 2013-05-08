from Components import Component
from threading import Timer
import datetime, pytz

class event2csv(Component.generic):
  Name = 'event2csv'
  sinkList = ['In']
  sourceList = []
  defaultState={}
  defaultConfig={'filename':'log.csv','timezone':'Europe/Brussels'}

  def __init__(self,compid):
    Component.generic.__init__(self,compid)

  def catchEvent(self,event,value):
    tz=pytz.timezone(self.getConfigVariable("timezone"))
    time = datetime.datetime.now(tz).strftime("%Y/%m/%d %H:%M:%S") 
    f = open("logging/" + self.getConfigVariable("filename"), 'a')
    f.write(time + "," + str(value["value"]) + '\n')
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


