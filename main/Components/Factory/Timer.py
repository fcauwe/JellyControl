#import blocks,events
import time
from Components import Events,Model
## ObjectName,eventName,eventValue 

class DelayOn1Sec:
  Name = "DelayOn1Sec"
  sinkList = ['In']
  sourceList = ['Out']
  visibleState=[]
  defaultConfig={}
  defaultState={}
  defaultInternalState={'value':False}
  @staticmethod
  def catchEvent(component,event,value):
    if (event=="In"):
      if(value["value"]==True):
        Model.intstate[component]["value"]=True
        time.sleep(1)
        Events.generateTarget(component,"Trigger",{'value':True})
      else:
        Model.intstate[component]["value"]=False
        Events.generate(component,"Out",{'value':False})
    elif (event=="Trigger"):
      if (Model.state[component]["value"]):
        Events.generate(component,"Out",{'value':True})
      

class DelayOff1Sec:
  Name = "DelayOff1Sec"
  sinkList = ['In']
  sourceList = ['Out']
  visibleState=[]
  defaultConfig={}
  defaultState={}
  defaultInternalState={'value':False}
  @staticmethod
  def catchEvent(component,event,value):
    if (event=="In"):
      if(value["value"]==False):
        Model.intstate[component]["value"]=False
        time.sleep(1)
        Events.generateTarget(component,"Trigger",{'value':False})
      else:
        Model.intstate[component]["value"]=True
        Events.generate(component,"Out",{'value':True})
    elif (event=="Trigger"):
      if (Model.state[component]["value"]):
        Events.generate(component,"Out",{'value':False})
      




class DoubleClick:
  Name = "DoubleClick"
  sinkList = ['In']
  sourceList = ['Out1Click','Out2Click','OutLong']
  visibleState=[]
  defaultConfig={}
  defaultState={}
  defaultInternalState={'state':False,'time':0,'clicks':0}
  @staticmethod
  def catchEvent(component,event,value):
    if (event=="In"):
      if(value["value"]==True):
        Model.instate[component]["clicks"]=Model.instate[component]["clicks"]+1
      
      Model.instate[component]["time"]=0

      if(Model.intstate[component]["state"]==False):
        time.sleep(0.1)
        Model.intstate[component]["state"]=True
        Events.generateTarget(component,"Trigger",{'value':True})

    elif (event=="Trigger"):
      if(int(Model.instate[component]["time"])<3):
        time.sleep(0.1)
        Model.instate[component]["time"]=int(Model.instate[component]["time"])+1 
        Events.generateTarget(component,"Trigger",{'value':True})
      else:
        
        Events.generate(component,"Out",{'value':True})

        Model.instate[component]["time"]=0
        Model.instate[component]["state"]=False
        Model.instate[component]["clicks"]=0




