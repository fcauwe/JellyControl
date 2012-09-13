import Queue
import json
import logging, logging.config
import sys, time, threading

import Model,Events
import Factory,Services
from Factory import *
from Services import *

def openModel(filename):
  logger=logging.getLogger("manager")
  logger.info("Opening model " + filename + "...")
  myFile = open(filename,'r')
  model=json.loads(myFile.read())
  myFile.close()
  return model
  

def loadModel(filename):
  logger=logging.getLogger("manager")
  logger.info("Loading model " + filename + "...")
  Model.model=openModel(filename)

def createLocks():
  Model.locks = dict()
  for name in Model.model.keys():
    Model.locks[name]=threading.Lock() 

def createState():
  logger=logging.getLogger("manager")
  Model.intstate = dict()
  Model.state = dict()
  for name in Model.model.keys():
    componentPath=Model.model[name]["type"].split('.')
    try:
      if(componentPath[0]!="service"):
        component=getattr(getattr(Factory,componentPath[0]),componentPath[1]) 
        Model.state[name]=dict(getattr(getattr(Factory,componentPath[0]),componentPath[1]).defaultState)
        Model.intstate[name]=dict(getattr(getattr(Factory,componentPath[0]),componentPath[1]).defaultInternalState)
    except Exception, e:
      logger.error("Component " + name + " / " + Model.model[name]["type"] + " has no state vector.")
      continue


def processEvent():
  # Load Logger
  logger=logging.getLogger("manager")
  # Start endless loop
  while True:
    ## Get an event from the queue
    event = Model.eventQueue.get()
    logger.info("Processing event " + str(event))
    ## Get event type
    componentType=Model.model[event[0]]["type"]
    if(Model.components.has_key(componentType)):
      componentPath=componentType.split('.')
      Model.locks[event[0]].acquire()
      try:
        if(componentPath[0]=="service"):
          Model.services[componentPath[1]].catchEvent(event[0],event[1],event[2])
        else:
          getattr(getattr(Factory,componentPath[0]),componentPath[1]).catchEvent(event[0],event[1],event[2]) 
        # callComponentEvent(componentType,event[0],event[1],event[2])
      except Exception, e:
        logger.error("Component " + componentType + " (" + event[0] + ") terminated: " + e.message)
      
      Model.locks[event[0]].release()
    else:  
      logger.error("ComponentType not found: " + componentType + " (" + event[0] + ")")
    Model.eventCount+=1 
    Model.eventQueue.task_done()


def listAllComponents():
  logger=logging.getLogger("manager")
  componentList=dict()
  for module in dir(Factory):
    if module[0]!="_":
      moduleObject=getattr(Factory,module)
      for component in dir(moduleObject):
        try:
          if ((component[0]!="_") and (component !="Events") and (component !="Model")):
            componentObject=getattr(moduleObject,component)
            componentList[module + "." + component]={'sources':componentObject.sourceList,
                                                     'sinks':componentObject.sinkList}
        except Exception, e:
          logger.error("Could not load " + component + ": " + e.message)
          continue
  for module in Model.services:
     componentList["service." + module] = {'sources':Model.services[module].sourceList,
                                            'sinks':Model.services[module].sinkList}
  return componentList


def listAllStates():
  stateList = []
  for component in Model.state.keys():
    for state in Model.state[component].keys():
      stateList.append(component + "." + state)
  return stateList

def listAllEvents():
  logger=logging.getLogger("manager")
  eventList = []
  for componentName in Model.model.keys(): 
    componentType = Model.model[componentName]["type"]
    try:
      for eventsink in Model.components[componentType]["sinks"]:
        eventList.append(componentName + "." + eventsink)
    except KeyError, e:
      logger.error("Component type not found: " + componentType + " in " + componentName + ".")
      pass
  return eventList

def addService(componentType,componentName,configurationXml):
  Model.services[componentName] = Services.ModbusIO.ModbusIO(componentName,configurationXml)

def start(num_worker_threads):
  logger=logging.getLogger("manager")
  Model.components = listAllComponents()
  createLocks()
  createState()
  logger.info("Starting model with " + str(num_worker_threads) + " threads...")
  # Start event workers
  for i in range(num_worker_threads):
    t = threading.Thread(target=processEvent)
    t.daemon = True
    t.start()
  # Start services
  for name in Model.services:
    logger.info("Starting service " + name + ".")
    t = threading.Thread(target=Model.services[name].start)
    t.daemon = True
    t.start()
 
def stop():
  print "test" 
