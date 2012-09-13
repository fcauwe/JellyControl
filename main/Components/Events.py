import Model
import Queue
import logging, logging.config

logger=logging.getLogger("events")

def generate(component,source,value):
  logger=logging.getLogger("events")
  logger.debug("Recieved event " + component + ":" + source + ".");
  try:
    for connection in Model.model[component]["connections"][source]:
      logger.debug("    Send event " + component + ":" + source + " --> "  + connection["sinkComponent"] + ":" + connection["sink"]);
      Model.eventQueue.put([connection["sinkComponent"], connection["sink"], value])
  except KeyError:
    logger.error("Component or event not found " + component + ":" + source + " does not exist.")

def generateTarget(component,sink,value):
  logger.debug("Send one event to " + component + ":" + sink );
  Model.eventQueue.put([component, sink, value])


