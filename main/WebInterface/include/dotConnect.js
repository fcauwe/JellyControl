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
  $( "#loading-status" ).html("Loading dialogs...");
  $( "#addmenu" ).menu({ position: { my: "right top", at: "left bottom" } });
  $( "#dialog-edit" ).dialog({
                              autoOpen:false,
                              resizable: false,
                              modal: true,
                              width: 450,
                              buttons: {
                                "Apply": function(){editChangeComponent();$(this).dialog("close");},
                                "Delete": function() {removeComp();$(this).dialog("close");},
                                "Cancel": function() {$(this).dialog("close");}
                              }
                      }); 
  $( "#dialog-add" ).dialog({
                              autoOpen:false,
                              resizable: false,
                              modal: true,
                              width: 450,
                              buttons: {
                                "Add": function(){editChangeComponent();$(this).dialog("close");},
                                "Cancel": function() {$(this).dialog("close");}
                              }
                      }); 
 

  $( "#loading-status" ).html("Loading components...");
  loadComponentList();
  loadModel();
  loadWorksheetList();
  $(window).bind("load", function() {$("#loading").hide(); }); 
//  $("#loading").hide(500);
 //jsPlumbComponent.init();
  //loadComponents();
  //loadConnections();
});

function editComponent(component){
  // set name
  $("#form-name").val(component);
  var componentTypeEdit=componentList[component].type;
  $("#form-type").html(componentTypeEdit);
  var tablehtml = "<table border='0'>";
  var count = 0;
  for (var config in componentType[componentTypeEdit].config ){
    var value = componentType[componentTypeEdit].config[config];
    if ("config" in componentList[component]){
      if (config in componentList[component]["config"]){
        value = componentList[component]["config"][config];
      }
    }
    tablehtml += "<tr><td>" + config + ":</td>";
    tablehtml += "<td><input id='form-config-" + config + "' value='" + value + "' ></td></tr>";
    count++;
  }
  tablehtml += "</table>";

  if (count==0){tablehtml = "(none)";}
 
  $("#form-properties").html(tablehtml);
  $("#dialog-edit" ).dialog( "open" );
  $("#dialog-edit" ).dialog( "option","title", "Edit component '" + component + "'?" )
} 

function editChangeComponent(component){
  // set name
  component = $("#form-name").val();
  var componentTypeEdit=componentList[component].type;
  if (!("config" in componentList[component])){ componentList[component]["config"]={}; }

  for (var config in componentType[componentTypeEdit].config ){
    componentList[component]["config"][config]= $("#form-config-" + config).val();
  }
}



function loadWorksheetList(){
  
  jQuery(document).ready(function(){
    $("#workspaceOption").change(function() {
       switchWorkspace($("#workspaceOption").val());
     })
  });
  
  
}

function saveModel(){
  updateComponentsPosition();
  var postModel = {};
  postModel["componentList"] = componentList;
  postModel["proxyList"] = proxyList;
  var jsonModel = JSON.stringify(postModel);
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
      $( "#loading-status" ).html("Loading model...");
      componentList=data["componentList"];
      proxyList=data["proxyList"];
      document.title = ".Connect: " + modelName;
      //document.getElementById("Title").innerHTML=workspaceName; 
      
      // reinitialise worspaces 
      workspaceActive = "default";
      workspaceList = listWorkspaces();
      // Restart jsplumb (clean up)
      jsPlumbComponent.init();
      $( "#loading-status" ).html("Loading components...");
      loadComponents();
      loadProxys();
      $( "#loading-status" ).html("Loading connection...");
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
      var select =  document.getElementById('form-add-type')
      for ( component in componentType ){
        new_option = document.createElement('option');
        new_option.value = component;
        new_option.text = component;
        select.appendChild(new_option);
      }
 
    });
}    

function listWorkspaces(){
  var list = ["default"]
  var select =  document.getElementById('workspaceOption')

  for (var comp in componentList ){
    if(list.indexOf(componentList[comp]["workspace"])==-1){ 
      list.push(componentList[comp]["workspace"]);
      new_option = document.createElement('option');
      new_option.value = componentList[comp]["workspace"];
      new_option.text = componentList[comp]["workspace"];
      select.appendChild(new_option);
      
    }
  }
  return list
}

function addComp(){
  var type = prompt("component type?");
  var name = prompt("Component name?",type);
  if ((name!=null)&&(type!=null))
    addComponent(name,type);
}

function addProx(){
  var porttype = prompt("Port type (source/sink)?");
  var component = prompt("Component name?");
  var port = prompt("Port name?");
  if ((component!=null)&&(port!=null))
    addProxy(component,port,porttype);
}


function addComponent(name,type){
  componentList[name] = {"type":type,position:[0,0],workspace:workspaceActive,connections:{}};
  createVisualComponent(name,componentList[name]["type"],componentList[name]["position"]);
}

function addProxy(component,port,porttype){
  name = workspaceActive + "-" + component + "-" + port + "-" + porttype
  proxyList[name] = {position:[0,0],workspace:workspaceActive,"component":component,"port":port,"porttype":porttype};
  createVisualProxy(name);
}

function removeComp(){
  //var name = prompt("component name?");
  var name=$("#form-name").val();
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
  loadProxys();
  loadConnections();
} 

function createVisualComponent(name, type, position){   
  //TODO: Check if type exists

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
  // Make component editable
  $('#' + divname).dblclick(function(){editComponent(name);})
}


function createVisualProxy(name){   
  // define variables 
  var divname = "proxy-" + proxyList[name]["component"] + "-" + proxyList[name]["porttype"] 
                +"-"+ proxyList[name]["port"] ;
  var position = proxyList[name]["position"] 
  var type = name
  var smalltype = name

  $('#workspace').append("<div class='proxy' id='" + divname + "'>"
                       + "<strong>" +  proxyList[name]["component"] 
                       + "</strong><br><small>[<em><span title='proxy'>proxy</span></em>]</small></div>");
  
  // resize div to fitt connection 
  $("#"+divname).height(45);
  
  // Set the right position
  $("#"+divname).css({"top": position[1]+"px", "left": position[0]+"px"}); 
  
  // Make the div draggable
  jsPlumb.draggable(jsPlumb.getSelector("#"+divname));

  // Add sinks
  if ( proxyList[name]["porttype"] == "sink" ) {
      sinks=proxyList[name]["port"];
      var UUID = "comp-" + proxyList[name]["component"] + "-sink-" + sinks;
      jsPlumb.addEndpoint(divname, sinkEndpoint, {anchor:[0,0.5,-1,0], 
						  uuid:UUID, 
						  overlays:[["Label", {location:[0.5,-0.6], 
								       label:sinks, 
								       cssClass:"endpointSinkLabel"}]]
						 });
  }
   
  // Add source
  if ( proxyList[name]["porttype"] == "source" ) {
      sources=proxyList[name]["port"]
      var UUID = "comp-" + proxyList[name]["component"] + "-source-" + sources;
      jsPlumb.addEndpoint(divname, sourceEndpoint, {anchor:[1,0.5,1,0], 
						  uuid:UUID, 
						  overlays:[["Label", {location:[0.5,-0.6], 
								       label:sources, 
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

function loadProxys (){
  for (var proxy in proxyList ){
    // Check if component is listed in current workspace
    if(proxyList[proxy]["workspace"]==workspaceActive){ 
      createVisualProxy(proxy);
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

  for (var proxy in proxyList ){
    // Check if component is listed in current workspace
    if(proxyList[proxy]["workspace"]==workspaceActive){ 
      var divname = "#proxy-" + proxyList[proxy]["component"] + "-" + proxyList[proxy]["porttype"] 
                +"-"+ proxyList[proxy]["port"] ;
      var position=$(divname).position();
      proxyList[proxy]["position"]=[position.left,position.top];
    }
  }

}

var componentType = {};
var componentTypeExtra = {};

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
