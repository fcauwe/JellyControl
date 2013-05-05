from Components import Component
from threading import Timer

class SetReset(Component.generic):
  Name = 'SetReset'
  sinkList = ['Set','Reset','Toggle']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={}

  def __init__(self,componentId):
    Component.generic.__init__(self,componentId)

  def catchEvent(self,event,value):
    if (value['value']==True):
      if (event=='Set'):
        result=True
      elif(event=='Reset'):
        result=False
      elif(event=='Toggle'):
        result=not self.getStateVariable('value')
      if (result != self.getStateVariable('value')):
        self.setStateVariable('value',result)
        self.generateEvent('Out',{'value':result})

class MultiClick2(Component.generic):
  Name = 'MultiClick2'
  sinkList = ['In','Reset']
  sourceList = ['Out1','Out2']
  defaultState={'Out1':False,'Out2':False}
  defaultConfig={'clickdelay':0.5}
  currentvalue=False
  counter=0
  timer_running=False

  def __init__(self,compid):
    Component.generic.__init__(self,compid)

  def catchEvent(self,event,value):
    if (event=='In'):
      if (value['value']==True):
        if (self.timer_running==False):
          #create a timer
          self.timer_running=True
          self.counter=1;
          self.t = Timer(float(self.getConfigVariable("clickdelay")), self.timerFinished)
          self.t.start()
        else:
          self.t.cancel()
          self.counter+=1
          self.t = Timer(float(self.getConfigVariable("clickdelay")), self.timerFinished)
          self.t.start()
    elif (event=='Reset'):
      if (self.timer_running):
        self.t.cancel()
        self.timer_running=False
        self.setStateVariable('Out1',False)
        self.generateEvent('Out1',{'value':False})
        self.setStateVariable('Out2',False)
        self.generateEvent('Out2',{'value':False})

  def timerFinished(self):
    self.timer_running=False
    if (self.counter==1):
      if ((self.getStateVariable('Out1')==True) or (self.getStateVariable('Out2')==True)):
        self.setStateVariable('Out1',False)
        self.generateEvent('Out1',{'value':False})
        self.setStateVariable('Out2',False)
        self.generateEvent('Out2',{'value':False})
      else:
        self.setStateVariable('Out1',True)
        self.generateEvent('Out1',{'value':True})
        self.setStateVariable('Out2',False)
        self.generateEvent('Out2',{'value':False})
    elif (self.counter==2):
      self.setStateVariable('Out1',True)
      self.generateEvent('Out1',{'value':True})
      self.setStateVariable('Out2',True)
      self.generateEvent('Out2',{'value':True})
    else:
      self.setStateVariable('Out1',False)
      self.generateEvent('Out1',{'value':False})
      self.setStateVariable('Out2',True)
      self.generateEvent('Out2',{'value':True})
 





