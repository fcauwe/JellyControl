#import blocks,events
from Components import Events,Model
## ObjectName,eventName,eventValue 

class RisingEdge:
  Name = "RisingEdge"
  sinkList = ['In']
  sourceList = ['Out']
  defaultConfig={}
  defaultState={'value':False}
  defaultInternalState={}
  @staticmethod
  def catchEvent(component,event,value):
    if (event=="In"):
      #print component + " Event: " + event + " " + str(Model.state[component])
      if((value["value"]==True) and (Model.state[component]["value"]==False)):
        Events.generate(component,"Out",{'value':True})
      else:
        Events.generate(component,"Out",{'value':False})
      Model.state[component]["value"]=value["value"]


class SetReset:
  Name = "SetReset"
  sinkList = ['Set','Reset','Toggle']
  sourceList = ['Out']
  defaultConfig={}
  defaultState={'value':False}
  defaultInternalState={}
  @staticmethod
  def catchEvent(component,event,value):
    if (value["value"]==True):
      if (event=="Set"):
        Model.state[component]["value"]=True
      elif(event=="Reset"):
        Model.state[component]["value"]=False
      elif(event=="Toggle"):
        Model.state[component]["value"]= not Model.state[component]["value"]
      Events.generate(component,"Out",Model.state[component])

class AndPort:
  Name = "AndPort"
  sinkList = ['In1','In2']
  sourceList = ['Out']
  visibleState=['value']
  defaultState={'value':False}
  defaultInternalState={'in1':False,'in2':False}
  @staticmethod
  def catchEvent(component,event,value):
    if (event=='In1'):
      Model.intstate[component]['in1']=bool(value['value'])
    elif(event=='In2'):
      Model.intstate[component]['in2']=bool(value['value'])
    
    Model.state[component]['value']=Model.intstate[component]['in1'] and Model.intstate[component]['in2']
    Events.generate(component,'Out',{'value':Model.state[component]['value']})

class OrPort:
  Name = "OrPort"
  sinkList = ['In1','In2']
  sourceList = ['Out']
  defaultConfig={}
  defaultState={'value':False}
  defaultInternalState={'in1':False,'in2':False}
  @staticmethod
  def catchEvent(component,event,value):
    if (event=='In1'):
      Model.intstate[component]['in1']=bool(value['value'])
    elif(event=='In2'):
      Model.intstate[component]['in2']=bool(value['value'])
    
    Model.state[component]['value']=Model.intstate[component]['in1'] or Model.intstate[component]['in2']
    Events.generate(component,'Out',{'value':Model.state[component]['value']})

class NotPort:
  Name = "NotPort"
  sinkList = ['In']
  sourceList = ['Out']
  defaultState={'value':False}
  defaultInternalState={}
  @staticmethod
  def catchEvent(component,event,value):
    Model.state[component]['value']=not bool(value['value'])
    Events.generate(component,'Out',{'value':(not bool(value['value']))})

class ProxyPort:
  Name = "ProxyPort"
  sinkList = ['In']
  sourceList = ['Out']
  defaultState={}
  defaultState={'value':False}
  defaultInternalState={}
  @staticmethod
  def catchEvent(component,event,value):
    Model.state[component]['value']=value['value']
    Events.generate(component,'Out',{'value':value['value']})






