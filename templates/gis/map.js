//Global variables
var pointToolTips, polygonToolTips;
var polygonStyleMap;


function mapInit() {
	var map = new OpenLayers.Map('map', {
		controls: [ ],
		projection : new OpenLayers.Projection("EPSG:900913"),
		displayProjection : new OpenLayers.Projection("EPSG:4326"), //EPSG:4326
		units : "m",
		maxResolution : "auto",
//		maxExtent : new OpenLayers.Bounds(-20037508,-20037508,20037508,20037508), //whole world
		maxExtent : new OpenLayers.Bounds(3801000,3660000,3850000,3710500), //gaza strip
		restrictedExtent : new OpenLayers.Bounds(3801000,3660000,3850000,3710500), //gaza strip
		minZoomLevel: 11,
		maxZoomLevel: 17});

	{% if mapNavigate %}
	map.addControl(new OpenLayers.Control.Navigation());
	{%endif%}
	map.addControl(new OpenLayers.Control.customLayerSwitcher({'div':OpenLayers.Util.getElement('mapKey'),
	activeColor:'silver'}));
	map.addControl(new OpenLayers.Control.ScaleLine());
	map.addControl(new OpenLayers.Control.Attribution({"separator":","}));
	
	map.addControl(new OpenLayers.Control.Legend({}));
	
	//this first one is global so rollover functions can access it
	polygonStyleMap = new OpenLayers.StyleMap(
					{"default":new OpenLayers.Style({strokeWidth:0,
									fillOpacity:0,
									pointerEvents: "all",
									label : "${name}",
									fontColor: "white",
									fontSize: "10px",
									fontFamily: "Arial, sans-serif",
									fontWeight: "bold",
									labelAlign: "center"}), 
					"select":new OpenLayers.Style({strokeWidth:0,
									strokeColor:'#FF6600',
									fillColor:'#FF6600',
									fillOpacity:0.5,
									pointerEvents: "all",
									label : "${name}",
									fontColor: "white",
									fontSize: "10px",
									fontFamily: "Arial, sans-serif",
									fontWeight: "bold",
									labelAlign: "center"})});
	var bombingStyleMap = new OpenLayers.StyleMap(
			{pointRadius: 7,
			fillOpacity:1,
			externalGraphic:"{{MEDIA_URL}}pins/bombing.png"});
	var lineStyleMap = new OpenLayers.StyleMap(
					{strokeWidth:3,
					strokeColor:'#FFFF00'});
	
	var baseLayer = new OpenLayers.Layer.Google(
		"Google Aerial",{type: {{ mapType }},
			numZoomLevels:7,
			sphericalMercator:true,
			displayInLayerSwitcher:false,
		});
	map.addLayer(baseLayer);
	
	var osmLayer = new OpenLayers.Layer.OSM.Mapnik("Street Map",
	{
		type: 'png', getURL: osm_getTileURL,
		displayOutsideMaxExtent: true, opacity: 0.5,
		isBaseLayer: false, visibility: true,
		attribution:"OpenStreetMap (cc)",
		visibility:false,
	});
	map.addLayer(osmLayer);
	
	/*
	//Transparent OSM data
	var osmLayer = new OpenLayers.Layer.TMS("Street Map",
	["http://t1-overlay.hypercube.telascience.org/tiles/1.0.0/osm-merc-google-hybrid/",
	"http://t3-overlay.hypercube.telascience.org/tiles/1.0.0/osm-merc-google-hybrid/",
	"http://t2-overlay.hypercube.telascience.org/tiles/1.0.0/osm-merc-google-hybrid/"],
	{
		type: 'png', getURL: osm_getTileURL,
		displayOutsideMaxExtent: true, opacity: 0.5,
		isBaseLayer: false, visibility: true,
	});
	*/
	
	unosat_buildings = new OpenLayers.Layer.GML("Damage", "{{MEDIA_URL}}openlayers/unosat/doc.kml", 
	{
		format: OpenLayers.Format.KML, 
		projection: map.displayProjection,
		formatOptions: {
			extractStyles: true, 
			extractAttributes: true
		},
		attribution:"Damage Analysis: UNITAR-UNOSAT",
		legend:"<img src='{{MEDIA_URL}}openlayers/unosat/destroyed.png'> Building Likely Destroyed<br>"+
				"<img src='{{MEDIA_URL}}openlayers/unosat/damaged.png'> Building Likely Severely Damaged<br>"+
				"<img src='{{MEDIA_URL}}openlayers/unosat/impact_field.png'> Impact Crater (Field)<br>"+
				"<img src='{{MEDIA_URL}}openlayers/unosat/impact_road.png'> Impact Crater (Road)",
		visibility:false,
	});
	map.addLayer(unosat_buildings);

	
	var geojson_format = new OpenLayers.Format.GeoJSON();
	
	{% for layer in vectorLayers %}
		var {{layer.name}}_layer = new OpenLayers.Layer.Vector("{{layer.name}}",
			{'styleMap':{{layer.styleName}},
			{%if layer.attribution %}'attribution':"{{layer.attribution}}",{%endif%}
			{%if layer.legend%}'legend':"{{layer.legend}}",{%endif%}
		});
		{% for object in layer.list %}
			var {{layer.name}}_{{forloop.counter}} = geojson_format.read({{ object|safe }});
			{{layer.name}}_layer.addFeatures({{layer.name}}_{{forloop.counter}});
		{% endfor %}
		map.addLayer({{layer.name}}_layer);
	{%endfor%}
	
	map.zoomToExtent({{zoomLayer}}_layer.getDataExtent());

	//select controls
	//bombings
	{%if popupLayerName %}
		pointToolTips = new OpenLayers.Control.ToolTips({bgColor:"red",textColor :"black", bold : false, opacity : 0.75,
		widthValue:"200px"});
		map.addControl(pointToolTips);
		var pointSelectControl = new OpenLayers.Control.newSelectFeature({{popupLayerName}}_layer,
						{onHoverSelect:toolTipsOver, onHoverUnselect:toolTipsOut});
		map.addControl(pointSelectControl);
		pointSelectControl.activate();
		//set bombing visibility
		{%if hideBombings %}
			{{popupLayerName}}_layer.setVisibility(false);
		{%endif%}
		{{popupLayerName}}_layer.attribution = "Bombing Tabulation: Alireza Doostdar (cc)";
	{%endif%}

	//neighborhoods
	{% if polygonLayerName %}
		polygonTooltips = new OpenLayers.Control.ToolTips({bgColor:"silver",textColor :"black", bold : true, opacity : 0.75});
		map.addControl(polygonTooltips);
		var polygonSelectControl = new OpenLayers.Control.newSelectFeature({{polygonLayerName}}_layer,
						{onClickSelect:gotoWindowLink, onHoverSelect:polygonOver, onHoverUnselect:polygonOut});
		map.addControl(polygonSelectControl);
		polygonSelectControl.activate();
	{%endif%}
} //end mapInit

//OSM
function osm_getTileURL (bounds) {
	var res = this.map.getResolution();
	var x = Math.round ((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
	var y = Math.round ((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
	var z = this.map.getZoom();

	var path = (z+this.map.baseLayer.minZoomLevel) + "/" + x + "/" + y + "." + this.type; 
	var url = this.url;
	if (url instanceof Array) {
	    url = this.selectUrl(path, url);
	}
	return url + path;
}

//event handlers
function gotoFloatboxLink(feature) {
	fb.loadAnchor(feature.attributes.link,'title');
}
function gotoWindowLink(feature) {
	window.location.href = feature.attributes.link;
}
function gotoTabLink(feature) {
	//tabs array is zero based
	jQuery("#tabs").tabs("url", 2, feature.attributes.link).tabs("select", 2).tabs("load", 2);
	var linkLocation = new OpenLayers.LonLat(feature.geometry.x,feature.geometry.y);
	map.moveTo(linkLocation,5); //move and zoom
}
function polygonOver(feature) {
	var numAuthors = feature.attributes.numAuthors;
	var numPosts = feature.attributes.numPosts;
	var numPhotos = feature.attributes.numPhotos;
	var numVideos = feature.attributes.numVideos;
	
	if ((numAuthors > 0) || (numPosts > 0) || (numPhotos > 0) || (numVideos > 0)) {
		var display = "";
		
		if (numAuthors > 0) {
			display += numAuthors + " author";
			if (numAuthors > 1) { display += "s"; }
			display += "<br>";	
		}
		
		if (numPosts > 0) {
			display += numPosts + " post";
			if (numPosts > 1) { display += "s"; }
			display += "<br>";	
		}
		
		if (numPhotos > 0) {
			display += '<div class="numPhotos">';
			display += numPhotos + " photo galler";
			if (numPhotos == 1) { display += "y"; }
			else { display += "ies"; }
			display += "<br>";
		}
		
		if (numVideos > 0) {
			display += '<div class="numVideos">';
			display += numVideos + " video";
			if (numVideos > 1) { display += "s"; }
			display += "<br>";
		}
	
		polygonTooltips.show({html:display});
	}
	feature.style = polygonStyleMap["select"];
}
function polygonOut(feature) {
	polygonTooltips.hide();
	feature.style = polygonStyleMap["default"];
}

function toolTipsOver(feature) {
	var displayText = '';
	displayText += '<div class="bombingName">' + feature.attributes.name + '</div>';
	displayText += '<div class="bombingDesc">' + feature.attributes.description + '</div>';
	if (feature.attributes.casualties != "None") {
		displayText += '<div class="bombingCasualties">Casualties: ' + feature.attributes.casualties + '</div>';
	}
	pointToolTips.show({html:displayText});
}
function toolTipsOut(feature){
	pointToolTips.hide();
}