from Components import Component

class RisingEdge(Component.generic):
  Name = 'RisingEdge'
  sinkList = ['In']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={}

  def __init__(self,componentId):
    Component.generic.__init__(self,componentId)

  def catchEvent(self,event,value):
    if (event=='In'):
      if((value['value']==True) and (self.getStateVariable('value')==False)):
        self.generateEvent('Out',{'value':True})
      else:
        self.generateEvent('Out',{'value':False})
      self.setStateVariable('value',value['value'])


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

class AndPort(Component.generic):
  Name = 'AndPort'
  sinkList = ['In1','In2']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={}

  def __init__(self,componentId):
    Component.generic.__init__(self,componentId)
    self.in1=False
    self.in2=False
  
  def catchEvent(self,event,value):
    if (event=='In1'):
      self.in1=bool(value['value'])
    elif(event=='In2'):
      self.in2=bool(value['value'])

    result = self.in1 and self.in2
 
    if (result != self.getStateVariable('value')):
      self.setStateVariable('value',result)
      self.generateEvent('Out',{'value':result})

class OrPort(Component.generic):
  Name = 'OrPort'
  sinkList = ['In1','In2']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={}

  def __init__(self,componentId):
    Component.generic.__init__(self,componentId)
    self.in1=False
    self.in2=False
  
  def catchEvent(self,event,value):
    if (event=='In1'):
      self.in1=bool(value['value'])
    elif(event=='In2'):
      self.in2=bool(value['value'])
 
    result = self.in1 or self.in2
   
    if (result != self.getStateVariable('value')):
      self.setStateVariable('value',result)
      self.generateEvent('Out',{'value':result})

class NotPort(Component.generic):
  Name = 'NotPort'
  sinkList = ['In']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={}
 
  def __init__(self,componentId):
    Component.generic.__init__(self,componentId)
  
  def catchEvent(self,event,value):
    result = not bool(value['value'])

    if (result != self.getStateVariable('value')):
      self.setStateVariable('value',result)
      self.generateEvent('Out',{'value':result})

class ProxyPort(Component.generic):
  Name = 'ProxyPort'
  sinkList = ['In']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={}

  def __init__(self,componentId):
    Component.generic.__init__(self,componentId)
  
  def catchEvent(self,event,value):
    result = value['value']

    if (result != self.getStateVariable('value')):
      self.setStateVariable('value',result)
      self.generateEvent('Out',{'value':result})

 

