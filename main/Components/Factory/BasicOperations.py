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


class SetResetValue(Component.generic):
  Name = 'SetReset'
  sinkList = ['Set','Reset','Toggle','Value']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={}
 
  def __init__(self,componentId):
    Component.generic.__init__(self,componentId)

  def catchEvent(self,event,value):
    result = self.getStateVariable('value')
  
    if (value['value']==True):
      if (event=='Set'):
        result=True
      elif(event=='Reset'):
        result=False
      elif(event=='Toggle'):
        result=not self.getStateVariable('value')
     
    if(event=='Value'): 
       result = value['value']

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

class OrPort6(Component.generic):
  Name = 'OrPort6'
  sinkList = ['In1','In2','In3','In4','In5','In6']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={}

  def __init__(self,componentId):
    Component.generic.__init__(self,componentId)
    self.in1=False
    self.in2=False
    self.in3=False
    self.in4=False
    self.in5=False
    self.in6=False
  
  def catchEvent(self,event,value):
    if (event=='In1'):
      self.in1=bool(value['value'])
    elif(event=='In2'):
      self.in2=bool(value['value'])
    elif(event=='In3'):
      self.in3=bool(value['value'])
    elif(event=='In4'):
      self.in4=bool(value['value'])
    elif(event=='In5'):
      self.in5=bool(value['value'])
    elif(event=='In6'):
      self.in6=bool(value['value'])
 
    result = self.in1 or self.in2 or self.in3 or self.in4 or self.in5 or self.in6
   
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

class Bigger(Component.generic):
  Name = 'Bigger'
  sinkList = ['In']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={'threshold':0}

  def __init__(self,componentId):
    Component.generic.__init__(self,componentId)
  
  def catchEvent(self,event,value):
    if (value['value']>float(self.getConfigVariable("threshold"))):
      result=True
    else:
      result=False
    
    if (result != self.getStateVariable('value')):
      self.setStateVariable('value',result)
      self.generateEvent('Out',{'value':result})

 
class Smaller(Component.generic):
  Name = 'Smaller'
  sinkList = ['In']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultConfig={'threshold':0}

  def __init__(self,componentId):
    Component.generic.__init__(self,componentId)
  
  def catchEvent(self,event,value):
    if (float(value['value'])<float(self.getConfigVariable("threshold"))):
      result=True
    else:
      result=False

    if (result != self.getStateVariable('value')):
      self.setStateVariable('value',result)
      self.generateEvent('Out',{'value':result})

 


