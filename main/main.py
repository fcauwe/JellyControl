#!/usr/bin/env python

# (C) 2012 Francois Cauwe


#Global libs
import sys, time, threading
import logging, logging.config
import subprocess
#, shutil
#from xml.etree.ElementTree import ElementTree
import json
import Queue

#Private libs
import GlobalObjects
import WebInterface
import XmlDict
import Components
from Components import Model,Manager,Events
#import ComponentFactory

def load_config():
    logger.info("Loading Config...")
    conf=XmlDict.loadXml("config/global.xml")
    GlobalObjects.config_webinterface = conf["webinterface"]
    GlobalObjects.config_device = conf["device"]
    GlobalObjects.config_model = conf["componentModel"]
#    GlobalObjects.config_events = conf["events"]

def launch_web_interface():
    logger.info("Loading WebInterface...")
    WebInterface.Launch()


 
def main():
  
    GlobalObjects.running = True
    logging.config.fileConfig("config/logger.conf")
    global logger
    logger=logging.getLogger("main")
  
    # Loading global configuration
    load_config()
  
    # Loading model and start worker threads
    Components.Manager.loadModel("config/" + GlobalObjects.config_model["filename"])     
##    Components.Manager.addService("ModbusIOClient","ModbusIOMain","config/io.xml")
##    Components.Manager.addService("RFID","RFIDMain","config/rfid.xml")


    Components.Manager.start(2) 
  
    # Start Webinterface
    webInterfaceThread = threading.Thread(target=launch_web_interface)
    webInterfaceThread.start()

    # Wait for closing
    webInterfaceThread.join()
    Components.Model.eventQueue.join()
    logger.info("Closing...")
    time.sleep(0.1)    
  
    # Close all threads
    for thread in threading.enumerate():
      if thread.isAlive():
        try:
          thread._Thread__stop()
        except:
          print(str(thread.getName()) + ' could not be terminated')

if __name__ == '__main__':
    main()

