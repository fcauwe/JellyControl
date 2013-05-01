#!/usr/bin/env python
import XmlDict,GlobalObjects
from Components import Component
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
import time
import logging, logging.config

class ModbusIO(Component.generic):
  Name = "ModbusIO"
  xmlname=""
  sinkList = ['In']
  sourceList = ['Out']
  defaultConfig={}
  defaultState={}
  configuration={}  
  
  modbus_ip=""
  modbus_period=0.1

  modbus_read_adres=0
  modbus_read_size=0
  modbus_read_type=[] 
  modbus_read_analog_threshold=[] 
 
  modbus_write_adres=0
  modbus_write_size=0
  modbus_write_dict={}
  modbus_write_image=[]
  modbus_write_event=[]
  
  def __init__(self,componentId,xmlname):
    Component.generic.__init__(self,componentId)
    self.configuration=XmlDict.loadXml(xmlname)
    self.xmlname=xmlname
    #self.configuration=XmlDict.loadXml("global.xml")
    # Load Configuration for reading (input)
    self.modbus_ip=self.configuration["ip"];
    self.modbus_period=1/float(self.configuration["update_frequency"])
    self.modbus_read_adres=int(self.configuration["input"]["modbus_adres"])
    self.modbus_read_size=int(self.configuration["input"]["modbus_register_count"])
    self.modbus_read_type=[''] * self.modbus_read_size
    self.modbus_read_analog_threshold=[''] * self.modbus_read_size
    self.modbus_read_analog_scale=[''] * self.modbus_read_size
    self.modbus_read_event=[]

    # Load Configuration for writing (output)
    self.modbus_write_adres=int(self.configuration["output"]["modbus_adres"])
    self.modbus_write_size=int(self.configuration["output"]["modbus_register_count"])
    self.modbus_write_dict={}
    self.modbus_write_image=[0] * self.modbus_write_size
    self.modbus_write_event=[]
    self.prepareInputs()
    self.prepareOutputs()

    self.state_read_old = [0] * self.modbus_read_size
    self.state_read_new = [0] * self.modbus_read_size
 
    self.state_write = [0] * self.modbus_write_size
    self.state_write_changed=True
    #self.state_write[2]=1
    #self.state_write[1]=16000


  def prepareInputs(self):
    # Check inputs, if something is defined
    if (int(self.configuration["input"]["modbus_register_count"])>0):
      adres_definition=self.configuration["input"]["adres_definition"]["adres"]
      # Check that de definition fits with the reality
      if(self.modbus_read_size==len(adres_definition)):
        for adres in range(self.modbus_read_size):
          if(adres_definition[adres]["type"].lower()=="digital"):
            self.modbus_read_type[adres]="D"
            for bit in range(16):
              # add event to the list
              event_name=None
              if(adres_definition[adres].has_key("event_" + str(bit))):
                event_name = adres_definition[adres]["event_" + str(bit)]
              if(event_name==None):
                event_name="DI" + str(adres) + "." + str( bit )
              self.modbus_read_event.append(event_name)
              adres_definition[adres]["event_" + str(bit)] = event_name
            # end for bit
          elif(adres_definition[adres]["type"].lower()=="analog"):
            self.modbus_read_type[adres]="A"
            threshold=float(adres_definition[adres]["threshold"])*float(adres_definition[adres]["scale"])
            self.modbus_read_analog_threshold[adres]=int(threshold)
            self.modbus_read_analog_scale[adres]=float(adres_definition[adres]["scale"])
            # Add event to the list
            event_name = adres_definition[adres]["event"]
            if(event_name==None):
              event_name="AI" + str(adres)
            adres_definition[adres]["event"] = event_name
            self.modbus_read_event.append(event_name)
        # end for adres
      # end if
      self.sourceList = self.modbus_read_event
  
  def prepareOutputs(self):
    # Check outputs, if something is defined
    if (int(self.configuration["output"]["modbus_register_count"])>0):
      adres_definition=self.configuration["output"]["adres_definition"]["adres"]
      # Check that de definition fits with the reality
      if(self.modbus_write_size==len(adres_definition)):
        for adres in range(self.modbus_write_size):
          if(adres_definition[adres]["type"].lower()=="digital"):
            for bit in range(16):
              # add event to the list
              event_name=None
              if(adres_definition[adres].has_key("event_" + str(bit))):
                event_name = adres_definition[adres]["event_" + str(bit)]
              if(event_name==None):
                event_name="DO" + str(adres) + "." + str( bit )
              self.modbus_write_event.append(event_name)
              self.modbus_write_dict[event_name]={"adres":adres,"bit":bit,"type":"D"}
              adres_definition[adres]["event_" + str(bit)] = event_name
            # end for bit
          elif(adres_definition[adres]["type"].lower()=="analog"):
            # Add event to the list
            event_name = adres_definition[adres]["event"]
            if(event_name==None):
              event_name="AO" + str(adres)
            adres_definition[adres]["event"] = event_name
            self.modbus_write_dict[event_name]={"adres":adres,"type":"A"}
            self.modbus_write_event.append(event_name)
        # end for adres
      # end if
      self.sinkList = self.modbus_write_event

  def catchEvent(self,event,value):
    logger=logging.getLogger("service")
    if (self.modbus_write_dict.has_key(event)):
      if(self.modbus_write_dict[event]["type"]=="D"):
        current=self.state_write[self.modbus_write_dict[event]["adres"]]
        bitposition=self.modbus_write_dict[event]["bit"]
        if(bool(value["value"])):
          target = (current | ( 1 << bitposition))
        else:
          target =(current & (~(1<<bitposition)))
        self.state_write[self.modbus_write_dict[event]["adres"]]=int(target)
      elif(modbus_write_dict[event]["type"]=="A"):
        self.state_write[self.modbus_write_dict[event]["adres"]]=int(value["value"])
      self.state_write_changed=True
    else:
      logger.error("Event not found(modbus): " + eventName)  


  def start(self):
    # Connect the client
    self.client = ModbusTcpClient(self.modbus_ip)
    logger=logging.getLogger("service")
    logger.info("Starting Service: " + self.componentId + " (ModbusIO: " + self.xmlname + ").")
    while (GlobalObjects.running):
     
      if(self.client.connect()):
        # Check if the output variables changed, if needed send the new state
        if (self.state_write_changed):
          self.state_write_changed = False
          try:
            self.client.write_registers(self.modbus_write_adres,self.state_write)
          except (AttributeError, ConnectionException):
            state_read_new=self.state_read_old
            pass
     
        # sleep a while
        time.sleep(self.modbus_period)
          
        # try to read new state of the inputs, if connection fails, continue
        try:
          state_read_new = self.client.read_holding_registers(self.modbus_read_adres,
                                                              self.modbus_read_size).registers
        except (AttributeError, ConnectionException):
          state_read_new=self.state_read_old
          pass

        # Read check every register for changes
        for i in range( len(state_read_new)):
          if (state_read_new[i]!=self.state_read_old[i]):
            # When the change is in a DI
            if (self.modbus_read_type[i]=='D'):
              # Mark changed positions
              changed=state_read_new[i]^self.state_read_old[i]
              for j in range(16):
                if((changed >> j) & 1):
                  # Generate event
                  eventName=self.configuration["input"]["adres_definition"]["adres"][i]["event_" + str(j)]
                  self.generateEvent(eventName,{'value':((state_read_new[i]>>j) & 1)})
                  #print str(time.time()) + " " + str(i) + "." + str(j) + ": " + str((state_read_new[i]>>j) & 1)
              ## Save the new state
              self.state_read_old[i]=state_read_new[i]
            # When the change is in a AI
            elif (self.modbus_read_type[i]=='A'):
              diff = (state_read_new[i]-self.state_read_old[i])
              if ((diff>self.modbus_read_analog_threshold[i]) or (diff < -self.modbus_read_analog_threshold[i])):
                # Generate event
                eventName=self.configuration["input"]["adres_definition"]["adres"][i]["event"]
                value = float(state_read_new[i]) / self.modbus_read_analog_scale[i]
                self.generateEvent(self.componentId,eventName,{'value':value})
                #print str(i) + ": " + str(value)
 
                ## Save new state
                self.state_read_old[i]=state_read_new[i]
           
      else:
         logger.warning("Lost connection to modbus module.")
         self.state_write_changed=True 
         time.sleep(1)


