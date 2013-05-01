import threading,sys,traceback,os.path,logging
import Events

class generic:
   componentId=""
   def __init__(self,compid):
     self.componentId=compid
     if (hasattr(self, 'defaultState')):
       self.state = self.defaultState.copy()
     else:
       self.state = {}
     self.stateVersion = 0
     if (hasattr(self, 'defaultCopy')):
       self.config = self.defaultConfig.copy()
     else:
       self.config = {}
     # Create Lock
     self.lock = threading.Lock()     
     self.logger=logging.getLogger("component")

   def getState(self):
     return self.state
   def setState(self,state):
     self.state=state.copy()
   def getStateVersion(self):
     return self.stateVersion
   def setStateVariable(self,name,value):
     self.state[name]=value
     self.stateVersion+=1
   def getStateVariable(self,name):
     return self.state[name]
   def getConfig(self):
     return self.config.copy()
   def setConfig(self,config):
     self.config = config.copy()
   def getConfigVariable(self,name):
     return self.config[name]
   def setConfigVariable(self,name,value):
     self.config[name]=value
   def init(self):
     if(hasattr(self,"do_init")):
       self.do_init()
   def generateEvent(self,port,value):
     Events.generate(self.componentId,port,value)

   def catchEventThreadSafe(self,event,value):
     self.lock.acquire()
     try:
       self.catchEvent(event,value)
     except Exception, e:
       tb = traceback.extract_tb(sys.exc_info()[2])[-1] 
       self.logger.error("Component " + self.Name + " (" + event + " / " + str(value) + ") terminated: " + e.message 
                         + " (" +os.path.basename(tb[0]) + ":" + str(tb[1])+ ").")
     
     self.lock.release()
 

