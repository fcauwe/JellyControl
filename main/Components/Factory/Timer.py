from Components import Component
from threading import Timer

class DelayOn(Component.generic):
  """This allows a value to be delayed """
  Name = 'DelayOn'
  sinkList = ['In']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={'delay':1}
  newvalue=False
  timer_running=False

  def __init__(self,compid):
    Component.generic.__init__(self,compid)

  def catchEvent(self,event,value):
    if (value['value']==True):
      #create a timer
      self.timer_running=True
      self.t = Timer(float(self.getConfigVariable("delay")), self.timerFinished)
      self.t.start()
    else:
      #Cancel timer
      if(self.timer_running):
        self.t.cancel()
      else:
        self.setStateVariable('value',False)
        self.generateEvent('Out',{'value':False})

  def timerFinished(self):
    self.timer_running=False
    self.setStateVariable('value',True)
    self.generateEvent('Out',{'value':True})

class DelayOff(Component.generic):
  Name = 'DelayOff'
  sinkList = ['In']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={'delay':1}
  newvalue=False
  timer_running=False

  def __init__(self,compid):
    Component.generic.__init__(self,compid)

  def catchEvent(self,event,value):
    if (value['value']==False):
      #create a timer
      self.timer_running=True
      self.t = Timer(float(self.getConfigVariable("delay")), self.timerFinished)
      self.t.start()
    else:
      #Cancel timer
      if(self.timer_running):
        self.t.cancel()
      else:
        self.setStateVariable('value',True)
        self.generateEvent('Out',{'value':True})

  def timerFinished(self):
    self.timer_running=False
    self.setStateVariable('value',False)
    self.generateEvent('Out',{'value':False})


class OnePulse(Component.generic):
  Name = 'OnePulse'
  sinkList = ['In']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={'delay':1}
  newvalue=False
  timer_running=False

  def __init__(self,compid):
    Component.generic.__init__(self,compid)

  def catchEvent(self,event,value):
    if (value['value']==True):
      #create a timer
      if(self.timer_running):
        self.t.cancel()

      self.timer_running=True
      self.t = Timer(float(self.getConfigVariable("delay")), self.timerFinished)
      self.t.start()
      self.setStateVariable('value',True)
      self.generateEvent('Out',{'value':True})

  def timerFinished(self):
    self.timer_running=False
    self.setStateVariable('value',False)
    self.generateEvent('Out',{'value':False})


class Pulse(Component.generic):
  Name = 'Pulse'
  sinkList = ['In']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={'delayOn':1,'delayOff':1}
  newvalue=False
  timer_running=False

  def __init__(self,compid):
    Component.generic.__init__(self,compid)

  def catchEvent(self,event,value):
    if (value['value']==True):
      #create a timer

      if not self.timer_running:
        self.timer_running=True
        self.t = Timer(float(self.getConfigVariable("delayOn")), self.timerFinished)
        self.t.start()
        self.setStateVariable('value',True)
        self.generateEvent('Out',{'value':True})
    else:
      if(self.timer_running):
        self.t.cancel()
      self.timer_running=False
      self.setStateVariable('value',False)
      self.generateEvent('Out',{'value':False})

  def timerFinished(self):
    if (self.getStateVariable('value')):
      self.setStateVariable('value',False)
      self.generateEvent('Out',{'value':False})
      self.t = Timer(float(self.getConfigVariable("delayOff")), self.timerFinished)
      self.t.start()
    else:
      self.setStateVariable('value',True)
      self.generateEvent('Out',{'value':True})
      self.t = Timer(float(self.getConfigVariable("delayOn")), self.timerFinished)
      self.t.start()



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


