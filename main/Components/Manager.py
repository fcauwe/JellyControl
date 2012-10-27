import Queue
import json
import logging, logging.config
import sys, time, threading,traceback,os.path

import Model,Events,Component
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

def loadComponents():
  logger=logging.getLogger("manager")
  #Model.modelComponents = dict()
  for name in Model.model.keys():
    componentPath=Model.model[name]["type"].split('.')
    if(componentPath[0]!='service'):
      try:
        component=getattr(getattr(Factory,componentPath[0]),componentPath[1]) 
        Model.modelComponents[name]=component()
      except Exception, e:
        tb = traceback.extract_tb(sys.exc_info()[2])[-1]      
        logger.error("Could not load component " + name + " / " + Model.model[name]["type"] + ": "
                      + e.message + " (" +os.path.basename(tb[0]) + ":" + str(tb[1])+ ").")
        continue


def processEvent():
  # Load Logger
  logger=logging.getLogger("manager")
  # Start endless loop
  while True:
    ## Get an event from the queue
    event = Model.eventQueue.get()
    logger.info("Processing event " + str(event))
    try:
      Model.modelComponents[event[0]].catchEventThreadSafe(event[0],event[1],event[2]) 
    except Exception, e:  
      tb = traceback.extract_tb(sys.exc_info()[2])[-1]      
      logger.error("Could not execute " + event[0] + " (" + event[1] + "): "
                      + e.message + " (" +os.path.basename(tb[0]) + ":" + str(tb[1])+ ").")

    Model.eventQueue.task_done()


def listAllComponents():
  logger=logging.getLogger("manager")
  componentList=dict()
  for module in dir(Factory):
    if module[0]!="_":
      moduleObject=getattr(Factory,module)
      for component in dir(moduleObject):
        try:
          componentObject=getattr(moduleObject,component)
          if(type(componentObject)==type(Component.generic)):
            if(issubclass(componentObject,Component.generic)):
              componentList[module + "." + component]={'sources':componentObject.sourceList,
                                                       'sinks':componentObject.sinkList}
        except Exception, e:
          logger.error("Could not inspect " + component + ": " + e.message)
          continue
  for module in Model.services:
     componentList["service." + module] = {'sources':Model.services[module].sourceList,
                                            'sinks':Model.services[module].sinkList}
  return componentList


def listAllStates():
  stateList = []
  for component in Model.modelComponents.keys():
    for state in Model.modelComponents[component].getState().keys():
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

def componentStateVersion(components):
  version = 0
  for component in components:
    if Model.modelComponents.has_key(component):
      version += Model.modelComponents[component].getStateVersion()
  return version


def addService(componentType,componentName,configurationXml):
  Model.modelComponents[componentName] = Services.ModbusIO.ModbusIO(componentName,configurationXml)
  Model.services[componentName]=Model.modelComponents[componentName]
#  Model.services[componentName] = Services.ModbusIO.ModbusIO(componentName,configurationXml)

def start(num_worker_threads):
  logger=logging.getLogger("manager")
  Model.components = listAllComponents()
  loadComponents()
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
