;(function() {
	
  window.jsPlumbComponent = {
    init : function() {
      jsPlumb.importDefaults({
        // default drag options
        DragOptions : { cursor: 'pointer', zIndex:2000 },
                        // default to blue at one end and green at the other
                        EndpointStyles : [{ fillStyle:'#225588' }, { fillStyle:'#558822' }],
                        // blue endpoints 7 px; green endpoints 11.
                        Endpoints : [ [ "Dot", {radius:7} ], [ "Dot", { radius:11 } ]],
                        // the overlays to decorate each connection with.  
                        // note that the label overlay uses a function to generate the label text; in this
                        // case it returns the 'labelText' member that we set on each connection in the 
                        // 'init' method below.
				ConnectionOverlays : [
					[ "Arrow", { location:0.9 } ]
				]
			});			

				
			// listen for new connections; initialise them the 
                        // same way we initialise the connections at startup.
			//jsPlumb.bind("jsPlumbConnection", function(connInfo, originalEvent) { 
			//	init(connInfo.connection);
			//});
			
			//
			// listen for clicks on connections, and offer to delete connections on click.
			//
			jsPlumb.bind("click", function(conn, originalEvent) {
                          var sinkId=conn.endpoints[1].getUuid().split("-");
                          var sourceId=conn.endpoints[0].getUuid().split("-");
                          if (confirm("Delete connection from " + sourceId[1] + ":" + sourceId[3] 
                                      + " to " + sinkId[1] + ":" + sinkId[3] + "?")){
                            var connections = componentList[sourceId[1]]["connections"][sourceId[3]];
                            for(var i=0; i<connections.length; i++){
                              if((connections[i].sinkComponent==sinkId[1])&&(connections[i].sink==sinkId[3])){
                                componentList[sourceId[1]]["connections"][sourceId[3]].splice(i,1);
                              }
                            }
                            jsPlumb.detach(conn); 
                          }
			});	
			
			jsPlumb.bind("connectionDragStop", function(connection) {
                          // Check if it is a finished connection 
                          var sinkComponentId=connection.endpoints[1].anchor.elementId;
                          if (sinkComponentId!=null){
                            var sinkId=connection.endpoints[1].getUuid().split("-");
                            var sourceId=connection.endpoints[0].getUuid().split("-");
                            // Check if it is a dragged and dropped connection and remove suspended endpoint                   
                            var suspendedEndpoint = connection.suspendedEndpoint;
                            if (suspendedEndpoint){
                              var suspendedSinkId = suspendedEndpoint.getUuid().split("-");
                              var connections = componentList[sourceId[1]]["connections"][sourceId[3]];
                              for(var i=0; i<connections.length; i++){
                                if((connections[i].sinkComponent==suspendedSinkId[1])&&(connections[i].sink==suspendedSinkId[3])){
                                  componentList[sourceId[1]]["connections"][sourceId[3]].splice(i,1);
                                }
                              }
                            } 
 
                            // Check if connection already exits
                            var newConnection = true;
                            var connections = componentList[sourceId[1]]["connections"][sourceId[3]];
                            if(connections){
                              for(var i=0; i<connections.length; i++){
                                if((connections[i].sinkComponent==sinkId[1])&&(connections[i].sink==sinkId[3])){
                                  newConnection = false; 
                                }
                              }
                            }else{
                              componentList[sourceId[1]]["connections"][sourceId[3]] = new Array();
                            }
                            // Add connection if new, else delete it.
                            if(newConnection){
                              componentList[sourceId[1]]["connections"][sourceId[3]].push({sinkComponent:sinkId[1],
                                                  sink:sinkId[3],
                                                  workspace:workspaceActive});
                            }else{
                              jsPlumb.detach(connection);
                            }
                          }       
			});
		}
	};
})();


jsPlumb.bind("ready", function() {
  loadComponentList();
  loadModel();
  loadWorksheetList(); 
  //jsPlumbComponent.init();
  //loadComponents();
  //loadConnections();
});


function loadWorksheetList(){
  
  jQuery(document).ready(function(){
    $("#workspaceOption").change(function() {
       switchWorkspace($("#workspaceOption").val());
     })
  });
  
  
}

function saveModel(){
  updateComponentsPosition();
  var jsonModel = JSON.stringify(componentList);
  var jsonDase64Model = Base64.encode(jsonModel);
  var name = prompt("Model name?",modelName);
  var postLink = location.href.substring(0,location.href.lastIndexOf("/")+1);
  $.post(postLink + "connect.saveModel.json?jsoncallback=?", { "name": name, "content": jsonDase64Model},
   function(data){
     alert(data.result);
   }, "json");

}

function loadModel(){
  
  var modelName = location.search.substring(1).split("&");
  if (modelName==""){
    var modelName="default";
  }
  // do a ajax request
  var getLink = location.href.substring(0,location.href.lastIndexOf("/")+1);
  $.getJSON(getLink + "connect.openModel.json?name=" + modelName + "&jsoncallback=?",
    function(data){
      componentList=data;
      document.title = ".Connect: " + modelName;
      //document.getElementById("Title").innerHTML=workspaceName; 
      
      // reinitialise worspaces 
      workspaceActive = "default";
      workspaceList = listWorkspaces();
      // Restart jsplumb (clean up)
      jsPlumbComponent.init();
      loadComponents();
      loadConnections();
    });
}    

function loadComponentList(){
  
  // do a ajax request
  var getLink = location.href.substring(0,location.href.lastIndexOf("/")+1);
  $.getJSON(getLink + "connect.listComponents.json?jsoncallback=?",
    function(data){
      componentType=jQuery.extend(data,componentTypeExtra)
      //componentType=data;
    });
}    

function listWorkspaces(){
  var list = ["default"]
  for (var comp in componentList ){
    if(list.indexOf(componentList[comp]["workspace"])==-1){ 
      list.push(componentList[comp]["workspace"]);
    }
  }
  return list
}



function test2(){

}


function addComp(){
  var type = prompt("component type?");
  var name = prompt("Component name?",type);
  if ((name!=null)&&(type!=null))
    addComponent(name,type);
}


function addComponent(name,type){
  componentList[name] = {"type":type,position:[0,0],workspace:workspaceActive,connections:{}};
  createVisualComponent(name,componentList[name]["type"],componentList[name]["position"]);
}

function removeComp(){
  var name = prompt("component name?");
  if (name!="")
    removeComponent(name);

}

function removeComponent(name){
  // remove existing connection 
  for (var component in componentList ){
    for (var source in componentList[component]["connections"] ){
      for (var i = componentList[component]["connections"][source].length-1; i >= 0; i--){
        if(componentList[component]["connections"][source][i].sinkComponent==name){
          //var connection = componentList[component]["connections"][source][i];
          //var sinkUuid = "comp-" + connection.sinkComponent;
          //var sourceUuid = "comp-" + component ;
          //jsPlumb.select({source:sourceUuid, target:sinkUuid}).detach();
          componentList[component]["connections"][source].splice(i,1);
        } 
      }
    }
  }
  
  //var sourceUuid = "comp-" + name
  //jsPlumb.select({source:sourceUuid}).detach();
  delete componentList[name]
  switchWorkspace(workspaceActive)
  //$("#comp-"+name).remove();
}

function switchWorkspace(name){
  updateComponentsPosition();
  jsPlumb.reset();   
  $('#workspace').empty();
  jsPlumbComponent.init();
  workspaceActive=name;
  loadComponents();
  loadConnections();
} 

function createVisualComponent(name, type, position){   
  // define variables 
  var divname = "comp-" + name;
  var sinks = componentType[type]["sinks"];
  var sources = componentType[type]["sources"];
  

  // Add div to workspace
  if(type.length>10)
    var smalltype = "..." + type.substr(type.length-10,10)
    
  else
    var smalltype = type

  $('#workspace').append("<div class='component' id='" + divname + "'>"
                       + "<strong>" + name + "</strong><br><small>[<em><span title='" + type + "'>" + smalltype  + "</span></em>]</small>"
                       + "</div>");
  
  // resize div to fitt connection 
  var maxconnections = Math.max(sinks.length,sources.length); 
  var height=maxconnections*15+30; 
  $("#"+divname).height(height);
  
  // Set the right position
  $("#"+divname).css({"top": position[1]+"px", "left": position[0]+"px"}); 
  
  // Make the div draggable
  jsPlumb.draggable(jsPlumb.getSelector("#"+divname));

  // Add sinks
  for (var i = 0; i < sinks.length; i++) {
      var UUID = divname + "-sink-" + sinks[i];
      var pos = (i+1) / (sinks.length + 1);
      jsPlumb.addEndpoint(divname, sinkEndpoint, {anchor:[0,pos,-1,0], 
						  uuid:UUID, 
						  overlays:[["Label", {location:[0.5,-0.6], 
								       label:sinks[i], 
								       cssClass:"endpointSinkLabel"}]]
						 });
  }
   
  // Add source
  for (var i = 0; i < sources.length; i++) {
      var UUID = divname + "-source-" + sources[i];
      var pos = (i+1) / (sources.length + 1);
      jsPlumb.addEndpoint(divname, sourceEndpoint, {anchor:[1,pos,1,0], 
						  uuid:UUID, 
						  overlays:[["Label", {location:[0.5,-0.6], 
								       label:sources[i], 
								       cssClass:"endpointSourceLabel"}]]
						 });
  }
}

function loadComponents (){
  for (var comp in componentList ){
    // Check if component is listed in current workspace
    if(componentList[comp]["workspace"]==workspaceActive){ 
      createVisualComponent(comp,componentList[comp]["type"],componentList[comp]["position"]);
    }
  }
}

function loadConnections (){
  for (var component in componentList ){
    for (var source in componentList[component]["connections"] ){
      for (var i = 0; i < componentList[component]["connections"][source].length; i++){
        var connection = componentList[component]["connections"][source][i];
        if (connection.workspace==workspaceActive){
          var sourceUuid = "comp-" + component + "-source-" + source;
          var sinkUuid = "comp-" + connection.sinkComponent + "-sink-" + connection.sink;
          jsPlumb.connect({uuids:[sourceUuid, sinkUuid]}); 
        }
      }
    }
  }
}


function updateComponentsPosition (){
  for (var comp in componentList ){
    // Check if component is listed in current workspace
    if(componentList[comp]["workspace"]==workspaceActive){ 
      var divname = "#comp-" + comp;
      var position=$(divname).position();
      componentList[comp]["position"]=[position.left,position.top];
    }
  }
}


var componentType = {};
var componentTypeExtra = { Input:{sinks:[],sources:["In1OnChange","In2OnChange","In3OnChange","In4OnChange"]},
                      Output:{sinks:["Out1","Out2","Out3","Out4"],sources:[]}};

var componentList =  {};
var modelName="default";
var workspaceList = ["default"];
var workspaceActive = "default";
var connectorPaintStyle = {
	lineWidth:2,
	strokeStyle:"#deea18",
	joinstyle:"round",
	outlineColor:"white",
	outlineWidth:4
};
// .. and this is the hover style. 
var connectorHoverStyle = {
	lineWidth:4,
	strokeStyle:"#2e2aF8"
};
// the definition of source endpoints (the small blue ones)
var sourceEndpoint = {
	endpoint:"Dot",
	paintStyle:{ fillStyle:"#225588",radius:5 },
	isSource:true,
        maxConnections:-1,
	connector:[ "Flowchart", { stub:20, gap:10 } ],
		connectorStyle:connectorPaintStyle,
		hoverPaintStyle:connectorHoverStyle,
		connectorHoverStyle:connectorHoverStyle,
                dragOptions:{}
};
// the definition of target endpoints (will appear when the user drags a connection) 
var sinkEndpoint = {
	endpoint:"Dot",					
	paintStyle:{ fillStyle:"#558822",radius:5 },
		hoverPaintStyle:connectorHoverStyle,
		maxConnections:-1,
		dropOptions:{ hoverClass:"hover", activeClass:"active" },
		isTarget:true			
};			

var connTest = {};
