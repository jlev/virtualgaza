//DECONFLICT JQUERY AND OPENLAYERS
$j = jQuery.noConflict();

//SELECT CONTROLS
var polygonSelectControl,pointSelectControl;

//ROLLOVER VARIABLES
var polygonToolTips,pointToolTips;

//the map
var map;

//STYLE MAPS
var polygonStyleMap = new OpenLayers.StyleMap(
				{"default":new OpenLayers.Style({strokeWidth:0,
								fillOpacity:0,
								pointerEvents: "all",
								label : "${name}",
								fontColor: "white",
								fontSize: "10px",
								fontFamily: "Arial, sans-serif",
								fontWeight: "bold",
								labelAlign: "center"}), 
				"select":new OpenLayers.Style({strokeWidth:1,
								strokeColor:'#FF6600',
								fillOpacity:0,
								pointerEvents: "all",
								label : "${name}",
								fontColor: "white",
								fontSize: "10px",
								fontFamily: "Arial, sans-serif",
								fontWeight: "bold",
								labelAlign: "center"})});
var lineStyleMap = new OpenLayers.StyleMap(
				{strokeWidth:3,
				strokeColor:'#FFFF00'});
var bombingStyleMap = new OpenLayers.StyleMap(
		{pointRadius: 7,
		fillOpacity:1,
		externalGraphic:"{{MEDIA_URL}}pins/bombing.png"});

function mapInit() {
	//var gazaBounds = new OpenLayers.Bounds(3801000,3660000,3850000,3710500);
	var gazaBounds = new OpenLayers.Bounds(3801000,3660000,3855000,3710500);
	//var gazaBounds = new OpenLayers.Bounds(3800000,3650000,3850000,3715000); 
	//left,bottom,right,top
	
	map = new OpenLayers.Map('map', {
		controls: [ ],
		projection : new OpenLayers.Projection("EPSG:900913"),
		displayProjection : new OpenLayers.Projection("EPSG:900913"), //EPSG:4326
		units : "m",
		maxResolution : "auto",
		maxExtent : gazaBounds,
		restrictedExtent : gazaBounds,
		minZoomLevel: 11,
		maxZoomLevel: 17});

	map.addControl(new OpenLayers.Control.Navigation());
	map.addControl(new OpenLayers.Control.KeyboardDefaults());
	map.addControl(new OpenLayers.Control.PanZoomBar());
	map.addControl(new OpenLayers.Control.customLayerSwitcher({'div':OpenLayers.Util.getElement('mapKey'),
	activeColor:'silver'}));
	map.addControl(new OpenLayers.Control.ScaleLine());
	map.addControl(new OpenLayers.Control.Attribution({"separator":","}));
	map.addControl(new OpenLayers.Control.Legend({}));
	
	//BASE LAYER
	var baseLayer = new OpenLayers.Layer.Google(
		"Google Aerial",{type: {{ mapType }},
			numZoomLevels:7,
			sphericalMercator:true,
			displayInLayerSwitcher:false
		});
	map.addLayer(baseLayer);
	
	//STREET MAP LAYER
	var osmLayer = new OpenLayers.Layer.OSM.Mapnik("Street Map",
	{
		type: 'png', getURL: osm_getTileURL,
		displayOutsideMaxExtent: true, opacity: 1,
		isBaseLayer: false, visibility: true,
		attribution:"OpenStreetMap (cc)",
		visibility:false
	});
	map.addLayer(osmLayer);
	osmLayer.events.register('visibilitychanged', this, onStreetMapVisibilityChanged);
	
	//UNOSAT LAYER
	unosat_buildings = new OpenLayers.Layer.GML("Damage", "/proxy/http://virtualgaza.media.mit.edu:81/media/openlayers/unosat/doc.kml", 
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
		visibility:false
	});
	map.addLayer(unosat_buildings);
	unosat_buildings.events.register('visibilitychanged', this, onDamageVisibiltyChanged);
	
	//VECTOR LAYERS
	var geojson_format = new OpenLayers.Format.GeoJSON();
	{% for layer in vectorLayers %}
		{{layer.name}}_layer = new OpenLayers.Layer.Vector("{{layer.name}}",
			{ {%if layer.attribution %}'attribution':"{{layer.attribution}}",{%endif%}
				{%if layer.legend%}'legend':"{{layer.legend}}",{%endif%}
				'styleMap':{{layer.styleName}}
		});
		{% for object in layer.list %}
			var {{layer.name}}_{{forloop.counter}} = geojson_format.read({{ object|safe }});
			{{layer.name}}_layer.addFeatures({{layer.name}}_{{forloop.counter}});
		{% endfor %}
		map.addLayer({{layer.name}}_layer);
	{%endfor%}
	
	//BOMBING LAYER
	{%if popupLayerName %}
		pointToolTips = new OpenLayers.Control.ToolTips({bgColor:"red",textColor :"black", bold : false, opacity : 0.75,
		widthValue:"200px"});
		map.addControl(pointToolTips);
		pointSelectControl = new OpenLayers.Control.newSelectFeature({{popupLayerName}}_layer,
						{onHoverSelect:toolTipsOver, onHoverUnselect:toolTipsOut});
		map.addControl(pointSelectControl);
		pointSelectControl.activate();
		//hide bombings by default
		{{popupLayerName}}_layer.setVisibility(false);
		{{popupLayerName}}_layer.attribution = "Bombing Tabulation: Alireza Doostdar (cc)";
	{%endif%}
	
	//NEIGHBORHOOD CONTROLS
	{% if polygonLayerName %}
		polygonTooltips = new OpenLayers.Control.ToolTips({bgColor:"silver",textColor :"black", bold : true, opacity : 0.75});
		map.addControl(polygonTooltips);
		polygonSelectControl = new OpenLayers.Control.newSelectFeature({{polygonLayerName}}_layer,
		{onClickSelect:zoomToNeighborhood,
			onHoverSelect:polygonOver,
			onHoverUnselect:polygonOut});
		map.addControl(polygonSelectControl);
		polygonSelectControl.activate();
	{%endif%}

	map.zoomToExtent(map.restrictedExtent);

	//REGISTER LISTENERS
	map.events.register('movestart',map,onMapMoveStart);
	map.events.register('moveend',map,onMapMoveEnd);
	
	//TRIGGER A MOVE EVENT ON INIT
	//to get visible neighborhoods
	map.events.triggerEvent('moveend');
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

//EVENT HANDLERS
function zoomToNeighborhood(feature) {
	this.map.zoomToExtent(feature.geometry.bounds);
}

function polygonOver(feature) {
	feature.style = polygonStyleMap["select"];
}
function polygonOut(feature) {
	feature.style = polygonStyleMap["default"];
}
	
function onMapMoveStart() {
}

function onMapMoveEnd() {
	var viewGeom = this.calculateBounds().toGeometry();
	$j.post("/ajax/neighborhoods_within_bounds/", 
		{bounds:viewGeom.toString()},
		function(data) {
			$j("div").filter("#neighborhoods").html(data);
		}
	);
	
	if(unosat_buildings.visibility) {
		calculateVisibleDamage();
	}
	
	//if close, deactivate polygonSelectControl
	//hard coding is probably not the best solution
	if(this.zoom >= 2) {
		polygonSelectControl.deactivate();
		pointSelectControl.activate();
	} else {
		polygonSelectControl.activate();
		pointSelectControl.deactivate();
	}
	
	//retag floatbox links
	//probably ineffecient to do the whole page
	fb.tagAnchors(document.body);
}

function calculateVisibleDamage() {
	var counts = {
		"#destroyed":0,
		"#damaged":0,
		"#impact_field":0,
		"#impact_road":0
		};

	map_extent = this.map.getExtent();
	var minx = map_extent.left;
	var maxx = map_extent.right;
	var miny = map_extent.bottom;
	var maxy = map_extent.top;

	for(var i = 0; i < unosat_buildings.features.length; i++) {
		var b = unosat_buildings.features[i];
		if (b.geometry != null) {
			var x = b.geometry.x,
			    y = b.geometry.y;
			//calculate onScreen manually, instead of using Feature.onScreen(), way faster
			if (x >= minx && x <= maxx && y >= miny && y <= maxy) {
				counts[b.attributes.styleUrl]++;
			}
		}
	}
	
	var numDestroyed = counts["#destroyed"],
	   numDamaged = counts["#damaged"],
	   numImpact = counts["#impact_field"] + counts["#impact_road"];

	$j("div").filter("#damage").html( "<h3>Damage Analysis</h3>" +
		"Buildings Destroyed:" + numDestroyed + "<br>" +
		"Buildings Damaged:" + numDamaged + "<br>" +
		"Impact Craters:" + numImpact +
		"<div id='note'>Analysis released by UNITAR January 9, 2008. Due to the reduced resolution of available satellite imagery, it underestimates the damage extent in dense areas.</div>"
		);
}

function onDamageVisibiltyChanged(layer) {
	if (layer.object.visibility){
		//wait a little bit for the kml to render
		setTimeout('calculateVisibleDamage()',250);
		$j("div").filter("#damage").show();
	} else {
		$j("div").filter("#damage").hide();
	}
}

function onStreetMapVisibilityChanged(layer) {
  {% if polygonLayerName %}
    if (layer.object.visibility){
      //streetmap on, neighborhood labels off
  		{{polygonLayerName}}_layer.styleMap.styles.default.defaultStyle.fontSize = "0px";
  		{{polygonLayerName}}_layer.styleMap.styles.select.defaultStyle.fontSize = "0px";
  	} else {
  	  //streetmap off, neighborhood labels on
  		{{polygonLayerName}}_layer.styleMap.styles.default.defaultStyle.fontSize = "10px";
  		{{polygonLayerName}}_layer.styleMap.styles.select.defaultStyle.fontSize = "10px";
  	}
  	//console.log({{polygonLayerName}}_layer.styleMap.styles);
  	{{polygonLayerName}}_layer.redraw();
	{%endif%}
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

