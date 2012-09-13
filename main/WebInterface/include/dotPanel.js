
// Define Arrays
var timeCounter=0;
var timeCounterMax=40;
var timer;
var reloadCounter=0;
var editMode=false
var editStateList={};
var editEventList={};
var actorList={};
var sourceList="";
var sourceMap={};
var state={};
var statePresent=false;
var stateForceDirectUpdate=true
var panelClass="panelBack";
var panelName;

function compareObject(x,y)
{
  var p;
  for(p in y) {
      if(typeof(x[p])=='undefined') {return false;}
  }

  for(p in y) {
      if (y[p]) {
          switch(typeof(y[p])) {
              case 'object':
                  if (!compareObject(y[p],x[p])) { return false; } break;
              case 'function':
                  if (typeof(x[p])=='undefined' ||
                      (p != 'equals' && y[p].toString() != x[p].toString()))
                      return false;
                  break;
              default:
                  if (y[p] != x[p]) { return false; }
          }
      } else {
          if (x[p])
              return false;
      }
  }

  for(p in x) {
      if(typeof(y[p])=='undefined') {return false;}
  }

  return true;
}


function generatePanel(){
  $('#content').hide();
  $('#content').empty();
  
  // show Edit mode specific
  if(editMode){
    $("#addActor").show();
    $("#savePanel").show();
  }else{
    $("#addActor").hide();
    $("#savePanel").hide();
  }
 
  // Create sourcelist
  sourceList=""
  sourceMap=Object()
  for (var actor in actorList){
    var source =  actorList[actor].source.split('.')[0];
    if(source!=''){
      if (sourceList.indexOf(source)==-1){ 
        sourceList += source + ",";
        sourceMap[source]=Array();
      }
      sourceMap[source].push(actor);
    }
    createVisualActor(actor);
  }
  sourceList = sourceList.substr(0,sourceList.length-1);
  state={};
  statePresent=false;
  timeCounter=timeCounterMax+1;
  stateForceUpdate=true;
  clearTimeout(timer)
  cycleTimer();
  if (editMode)
    $('#content').show(1000);
}

function updateActor(name,data){
  
  // update value
  $('#' + name).find(".actorValue").text(data.value);
  
  // assign CSS
  var css="actor" + actorList[name].css;
  if(data.value==true){
     $('#' + name).switchClass(css + "False", css + "True",10);
  }else{
     $('#' + name).switchClass(css+ "True", css + "False",10);
  }
}

function createVisualActor(actor){
  // Create actor
  var content = "<div id='" + actor + "'><span class='actorTitle'></span>";
  content += "<span class='actorValue'></span></div>";
  $('#content').append(content);
  
  // set Title  
  $('#' + actor).find(".actorTitle").text(actorList[actor].title)

  // Set Position
  if(actorList[actor].position[0]!=0){
    $("#" + actor).css({"top": actorList[actor].position[1]+"px"}); 
    $("#" + actor).css({"left": actorList[actor].position[0]+"px"});
    $("#" + actor).css({"position": "absolute"});
  }
  
  //Set size
  if(actorList[actor].resizable==true){
    try{
      $("#" + actor).css({"width": actorList[actor].size[0]}); 
      $("#" + actor).css({"height": actorList[actor].size[1]}); 
    }catch(err){}
  }
   
  // Add class
  $("#" + actor).addClass("actor" + actorList[actor].css)
  
  // Add image
  if((actorList[actor].image!="") && (actorList[actor].image!=null)){
    $("#" + actor).prepend("<img class='actorImage' src='" + actorList[actor].image  + "'>");
    
  }
  
  
  // Set Action   
  if (((actorList[actor].actionEvent.length>1) || (actorList[actor].actionLink.length>1)) && ( !editMode)){
   $('#' + actor).click(function(){actionActor(actor);})
   $('#' + actor).css('cursor','pointer');
  }
  if(editMode){
    $('#' + actor).dblclick(function(){editActor(actor);})
    $('#' + actor).css('cursor','pointer');
    $("#" + actor).draggable();
    if(actorList[actor].resizable)
      $("#" + actor).resizable();

  } 
}


function actionActor(actor){
  if(actorList[actor].actionLink.length>1){
    loadPanel(actorList[actor].actionLink);
  }else{
    var eventaction = actorList[actor].actionEvent.split('.');
    sendEvent(eventaction[0],eventaction[1],"True");
    stateForceUpdate=true;
  }
}

function newActor(){
  actor = "actor" + (new Date()).getTime();
  actorList[actor]={"resizable": false, "title": actor, "actionLink": "", "source": "", "position": [100,100], "actionEvent": "", "css": "Button3D", "image":""};
  createVisualActor(actor);
  editActor(actor);
}

function editActor(actor){
  // set name
  $("#form-actorname").val(actor);

  // set values
  $("#form-title").val(actorList[actor].title);
  $("#form-source").val(actorList[actor].source);
  $("#form-actionlink").val(actorList[actor].actionLink);
  $("#form-actionevent").val(actorList[actor].actionEvent);
  $("#form-css").val(actorList[actor].css);
  $("#form-image").val(actorList[actor].image);
  $("#form-resizable").attr("checked",actorList[actor].resizable)


  $("#dialog-edit" ).dialog( "open" );
}

function editChangeActor(){
  actor = $("#form-actorname").val();
  actorList[actor].title=$("#form-title").val();
  actorList[actor].source = $("#form-source").val();
  actorList[actor].actionLink = $("#form-actionlink").val();
  actorList[actor].actionEvent = $("#form-actionevent").val();
  actorList[actor].css = $("#form-css").val();
  actorList[actor].image = $("#form-image").val();
  actorList[actor].resizable = $("#form-resizable").attr("checked")


  // Save position
  var position=$("#" + actor).position();
  actorList[actor].position=[position.left,position.top];

  // remove old div, recreate new one
  $("#" + actor).remove();
  createVisualActor(actor);
}

function deleteActor(){
  actor = $("#form-actorname").val();
  
  // Delete actor
  delete actorList[actor]

  $("#" + actor).remove();
}

function updateState(){
  var getLink = location.href.substring(0,location.href.lastIndexOf("/")+1);
  // Define delaytime / forced update
  delayargs=""
  if(!stateForceUpdate)
    delayargs = "&delay=" + (timeCounterMax/2-2);
  
  // Do update
  $.getJSON(getLink + "panel.getState.json?components=" + sourceList + delayargs + "&jsoncallback=?",
    function(data){
      if(!editMode){
        stateForceUpdate=false;
        timeCounter=timeCounterMax-1;
        for (var source in data){
          // First time the state is undefined
          if(typeof(state[source])=='undefined')
            state[source]={};
          // compare new state with old, and update if needed
          if (!compareObject(state[source],data[source])){
            for (var i=0; i<sourceMap[source].length; i++)
              updateActor(sourceMap[source][i],data[source])
          }
        }
      }
      // copy new state to variable
      state=data; 
    })
  
  // Display panel
  if(!statePresent){
    setTimeout(showContent,200)
    statePresent=true
  }
}

function showContent(){
  $('#content').show(1000)
}

function sendEvent(component,componentevent,componentvalue){

  $.getJSON("panel.sendEvent.json?component=" + component + "&event=" + componentevent + "&value=" + componentvalue +  "&jsoncallback=?",
    function(data){
      if(data.result!=true)
       alert(data.result);
    });
}


function cycleTimer(){
  
  if (editMode)
    return;
  // Update the interface
  timeCounter++;  
  //if(timeCounter>globalConfig.updateDelay){
  if(timeCounter>timeCounterMax){
    updateState();
    timeCounter=0;    
    // reload the page after a while
    reloadCounter++;
    if(reloadCounter>1000){
       window.location.reload();
    }
  }
  
  // Update progressbar
  $('#progress').css({ 'width' : Math.round((1 - timeCounter/timeCounterMax)*100) + '%'});
  
  // Repeat this function every second   
  timer=setTimeout(cycleTimer,500);
}


function loadEditModeVariables(){
  // do a ajax request
  var getLink = location.href.substring(0,location.href.lastIndexOf("/")+1);

  $.getJSON(getLink + "panel.getStateList.json?jsoncallback=?",
    function(data){
      editStateList=data;
      $('#form-source').find('option').remove()
      $('<option/>').val("").html("none").appendTo('#form-source');
      for (i=0;i<editStateList.length;i++){
        $('<option/>').val(editStateList[i]).html(editStateList[i]).appendTo('#form-source');
      }
    });

  $.getJSON(getLink + "panel.getEventList.json?jsoncallback=?",
    function(data){
      editEventList=data;
      $('#form-actionevent').find('option').remove()
      $('<option/>').val("").html("none").appendTo('#form-actionevent');
      for (i=0;i<editEventList.length;i++){
        $('<option/>').val(editEventList[i]).html(editEventList[i]).appendTo('#form-actionevent');
      }
    });
}


function loadPanel(name){
  panelName=name;
  // do a ajax request
  var getLink = location.href.substring(0,location.href.lastIndexOf("/")+1);
  $.getJSON(getLink + "panel.openPanel.json?name=" + name + "&jsoncallback=?",
    function(data){
      actorList=data.actorList;
      $("body").switchClass(panelClass,data.panelClass);
      panelClass=data.panelClass;
      document.title = ".Panel: " + panelName;
      generatePanel(); 
    });
		
}

function savePanel(){
  if(editMode)
    updateActorSettings();
  var panel = {'name':panelName,'panelClass':panelClass,'actorList':actorList}
  var jsonPanel = JSON.stringify(panel);
  var jsonDase64Panel = Base64.encode(jsonPanel);
  var name = prompt("Panel name?",panelName);
  if (name==null)
    return;
  var postLink = location.href.substring(0,location.href.lastIndexOf("/")+1);
  $.post(postLink + "panel.savePanel.json?jsoncallback=?", { "name": name, "content": jsonDase64Panel},
   function(data){
     alert(data.result);
   }, "json");

}

function switchMode(){
  if(editMode)
    updateActorSettings();
  else
    loadEditModeVariables()
  
  editMode = !editMode;
  generatePanel();
}

function updateActorSettings(){

  for (var actor in actorList){
    var position=$("#" + actor).position();
    actorList[actor].position=[position.left,position.top];
    if (actorList[actor].resizable)
      actorList[actor].size=[$("#" + actor).css("width"),$("#" + actor).css("height")]
  }
}

$(document).ready(function(){
  $( "#dialog-edit" ).dialog({
                        autoOpen:false,
			resizable: false,
			modal: true,
			buttons: {
				 "Apply": function(){
                                        editChangeActor();
                                        $(this).dialog("close");
                                },
                                "Delete Actor": function() {
                                        deleteActor();
					$(this).dialog("close");
				},

				Cancel: function() {
					$(this).dialog("close");
				}
			}
		});

  panelName = location.search.substring(1).split("?");
  if (panelName==""){
    panelName="default";
  }

  $("#progress").dblclick(function(){switchMode();});
  $("#progressBackground").dblclick(function(){switchMode();});
  loadPanel(panelName); 
});

