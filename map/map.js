// variables 
var url=window.location.href;
var local_dir=url.replace('map.html', '')
var json_file= local_dir.concat('../AdsbGuiPlanesData.json')

var counter = 0, counterInit=0, counterDataProcessed=0;
var intervalId = null, intervalInit=null;
var preferences=null;
var myLatitude, myLongitude;
var map, zoomLevel = 10, scale=1;
var markers=[], tracks=[];
var running=['*&nbsp;&nbsp;&nbsp;','**&nbsp;&nbsp;','***&nbsp;','****'];
var read = false;
var oldTimeStamp = 0;

function initialize(){
    
    // Check for the various File API support.
    if (window.File && window.FileReader && window.FileList && window.Blob) {
    // Great success! All the File APIs are supported.
    } else {
    document.getElementById("bip").innerHTML='The File APIs are not fully supported in this browser.';
    alert('The File APIs are not fully supported in this browser.');
    }
    
    //location 
    map = L.map('map').setView([50,0], zoomLevel);
    readPreferences();

    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
        maxZoom: 18
    }).addTo(map);

    myLocationMarker  = L.marker(map.getCenter()).addTo(map);
    myLocationMarker.bindPopup("Home");
    
    test_CORS_thread(); 
}

function resetMap() {
    // Stop pseudo thread
    read = false;
    counterDataProcessed=0;
    clearInterval(intervalId);
    markers.forEach(function(item){
        map.removeLayer(item);
        });
    markers=[];
    tracks.forEach(function(item){
        map.removeLayer(item);
        });
    tracks=[];
    document.getElementById("bip").innerHTML = "<pre>Starting...</pre>";
    updateMapThread(); // start Map update process
}

function getXMLHttpRequest() {
	var xhr = null;
	
	if (window.XMLHttpRequest || window.ActiveXObject) {
		if (window.ActiveXObject) {
			try {
				xhr = new ActiveXObject("Msxml2.XMLHTTP");
			} catch(e) {
				xhr = new ActiveXObject("Microsoft.XMLHTTP");
			}
		} else {
			xhr = new XMLHttpRequest(); 
		}
	} else {
		alert("Votre navigateur ne supporte pas l'objet XMLHTTPRequest...");
		return null;
	}
	
	return xhr;
}

function readPreferences()
{
    var file = local_dir.concat('../AdsbGuiPreferences.json');
    var rawFile = getXMLHttpRequest(); // Voyez la fonction getXMLHttpRequest() définie dans la partie précédente

    rawFile.open("GET", file, true);
    rawFile.onreadystatechange = function ()
    
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                preferences=JSON.parse(rawFile.responseText);
                updateMapLocation(preferences);
                return 'ok';
            }
        }
    }
    rawFile.send(null);
}

function updateMapLocation(preferences)
{
    myLatitude=preferences['my_location'][0]['Latitude'];
    myLongitude=preferences['my_location'][0]['Longitude'];
    // add test (exists)
    var position = new L.LatLng(myLatitude, myLongitude);
    myLocationMarker.setLatLng(position)
    map.panTo(position);
}




function finish() {
    counterInit=0;
    clearInterval(intervalInit);
}



function test_CORS_thread() {  
    // test if CORS is allowed after 0.1s (test_CORS)
    intervalInit = setInterval(test_CORS, 100); 
}

function test_CORS() {
    if(counterInit==1) 
    {
        if (preferences===null){
            counter=0; // stop next thread
            finishInit();
            document.getElementById("bip").innerHTML += "It seems that your Bowser Blocked Cross-Origin Request to local file AdsbGuiPreferences.json.<br>You must use a browser allowing CORS for this map to show.";
        }
        else {
            document.getElementById("bip").innerHTML = "<pre>Starting GUI...</pre>";
            updateMapThread(); // start Map update process
        }
    }
    counterInit++;
}

function updateMapfinish() {
  counter=0;
  clearInterval(intervalId);
}

function updateMapThread() {
    counter=0;
    // run mapUpdate every second
    intervalId = setInterval(updateMapReadNewData, 1000); 
}	

function updateMapReadNewData() {
    
    var rawFile = getXMLHttpRequest(); // Voyez la fonction getXMLHttpRequest() définie dans la partie précédente
    rawFile.open("GET", json_file, true);
    rawFile.onreadystatechange = function ()
    
    {
        if(rawFile.readyState === 4)
        {
            if(rawFile.status === 200 || rawFile.status == 0)
            {
                json_obj=JSON.parse(rawFile.responseText);
                read = true;
                updateMap(json_obj);
                
            }
        }
    }
    rawFile.send(null);
    if (!read) 
        counter=(counter+1) % 4 
        document.getElementById("bip").innerHTML = "<pre>Waiting for data : "+ running[counter]+ '</pre>'; 

}

function updateMap(data)
{
    // data is a json object 
    counter=(counter+1) % 4 
    document.getElementById("bip").innerHTML ="<pre>Processing : " + running[counter] + ' Time : ' + Math.round(oldTimeStamp) + '(s)   Frame received : ' + counterDataProcessed+ '</pre>'; 
    if (data['timeStamp'] != oldTimeStamp && typeof data['timeStamp'] !== 'undefined') {
        oldTimeStamp = data['timeStamp'];
        data['newLocation'].forEach(updateMarker);    
    }
}

function ChoosePlaneIcon(direction)
{
    // 0<=direction <360 : trigonometric angle 0 is East 90 is North
    // position rounded to 16 integer values [0 à 15] (16==0)
    var i = Math.round((direction % 360)/22.5);

    if (i==0) { icon_URL='plane_0.png';}
    else if (i==1) { icon_URL='plane_22_5.png';}
    else if (i==2) { icon_URL='plane_45.png';}
    else if (i==3) { icon_URL='plane_77_5.png';}
    else if (i==4) { icon_URL='plane_90.png';}
    else if (i==5) { icon_URL='plane_122_5.png';}
    else if (i==6) { icon_URL='plane_135.png';}
    else if (i==7) { icon_URL='plane_157_5.png';}
    else if (i==8) { icon_URL='plane_180.png';}
    else if (i==9) { icon_URL='plane_202_5.png';}
    else if (i==10) { icon_URL='plane_225.png';}
    else if (i==11) { icon_URL='plane_247_5.png';}
    else if (i==12) { icon_URL='plane_270.png';}
    else if (i==13) { icon_URL='plane_292_5.png';}
    else if (i==14) { icon_URL='plane_315.png';}
    else if (i==15) { icon_URL='plane_337_5.png';}
    else { icon_URL='plane_0.png';} // for 16

    var PlaneIcon = new L.Icon({
            iconUrl: icon_URL,
            iconSize:     [56/scale, 63/scale],
            iconAnchor:   [28/scale, 32/scale],
            popupAnchor:  [0,-63/2/scale]
        });
    return PlaneIcon;
}

function updateMarker(location, index) {
  var i =    location['Index'];
  var position= new L.LatLng(location['Latitude'],location['Longitude']);
  counterDataProcessed+=1;
  

  if (typeof markers[i] === 'undefined') {
    
    var Icon = ChoosePlaneIcon(location['Direction']);
    markers[i] = new L.marker(position, {icon: Icon}).addTo(map);
    markers[i].bindPopup(location['Label'], {'maxWidth': '500'});
    tracks[i]=L.polyline(position, {color: 'blue'}).addTo(map);

    markers[i].on('popupopen', function (e) {
        // map.addLayer(tracks[i]);//For show
        tracks[i].setStyle({color: 'red'});

       });
    
    markers[i].on('popupclose', function (e) {
        // map.removeLayer(tracks[i]);// For hide
        tracks[i].setStyle({color: 'blue'});
       });

      
} else {
    markers[i].setIcon(ChoosePlaneIcon(location['Direction']));
    markers[i].setLatLng(position);
    markers[i]._popup.setContent(location['Label'])
    tracks[i].addLatLng(position);
  }
}
