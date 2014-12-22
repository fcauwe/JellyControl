# (C) 2012 Francois Cauwe
# This code can be freely distributed under the terms of the LGPL License.


#Load Global library's
import logging
import string,cgi,time,base64
from os import curdir, sep
import subprocess
import urllib2

#Load Private library's
import GlobalObjects
import Components
from Components import Events,Manager,Model 

def Process(filename,args):
    logger = logging.getLogger("WebInterface")
    
    if filename == "config.json":
        json_response=GlobalObjects.config_webinterface
        
    elif filename == "shutdown.json":
        logger.info("Closing application...")
        json_response={'result':'Application closed!'}
        logger.warning("Application is closing")
        GlobalObjects.running = False

    elif filename == "shutdown.json":
        json_response={'result':'Application closed!'}
    
    elif filename == "connect.openModel.json":
        name=args["name"].replace('.','').replace('/','')
        json_response=Manager.openModel("config/models/" + name)

    elif filename == "connect.saveModel.json":
        name=args["name"].replace('.','').replace('/','')
        model=base64.b64decode(urllib2.unquote(args["content"]).decode("utf8"))
        json_response={"result":"Saved!"}
        logger.info("Model "+ name + " saved.")
        try:
            subprocess.call(GlobalObjects.config_device["savingCommands"]["before"], shell=True)
            f = open("config/models/" + name, "w")
            f.write(model) # Write a string to a file
            f.close()
            subprocess.call(GlobalObjects.config_device["savingCommands"]["after"], shell=True)
        except IOError:
            json_response={"result":"IO error!"}
            pass

    elif filename == "connect.listComponents.json":
        json_response=Model.components

    elif filename == "panel.sendEvent.json":
        json_response={'result':True}
        value=args["value"]=='True'
        logger.info("Got event from webinterface "+ args["component"] + ":" + args["event"])
        Components.Events.generateTarget(args["component"],args["event"],{"value":value})
 
    elif filename == "panel.getState.json":
        components=args["components"].split(",")
        ## If a delay as been set, send state after the delay or when something changed
        if(args.has_key("delay")):
          refreshRate=0.1
          delay=float(args["delay"])
          if(delay>60):
            delay=60
          currentStateVersion=Manager.componentStateVersion(components)
          while((delay>=0) and (currentStateVersion==Manager.componentStateVersion(components)) and (GlobalObjects.running)):
            time.sleep(refreshRate)
            delay-=refreshRate
          ## wait a bit so that all needed events are processed
          time.sleep(0.2)
        state = dict()
        for component in components:
            if Model.modelComponents.has_key(component):
                state[component]=Model.modelComponents[component].getState()
            else:
		state[component]={"error":True}
        state["version"]=Manager.componentStateVersion(components)
        json_response=state

    elif filename == "panel.openPanel.json":
        name=args["name"].replace('.','').replace('/','')
        json_response=Manager.openModel("config/panels/" + name)

    elif filename == "panel.savePanel.json":
        name=args["name"].replace('.','').replace('/','')
        #print args["content"]
        model=base64.b64decode(urllib2.unquote(args["content"]).decode("utf8"))
        json_response={"result":"Saved!"}
        logger.info("Panel "+ name + " saved.")
        try:
            subprocess.call(GlobalObjects.config_device["savingCommands"]["before"], shell=True)
            f = open("config/panels/" + name, "w")
            f.write(model) # Write a string to a file
            f.close()
            subprocess.call(GlobalObjects.config_device["savingCommands"]["after"], shell=True)
        except IOError:
            json_response={"result":"IO error!"}
            pass

    elif filename == "panel.getEventList.json":
        json_response=Manager.listAllEvents()

    elif filename == "panel.getStateList.json":
        json_response=Manager.listAllStates()
 
    else:    
        json_response = { }




    return json_response
