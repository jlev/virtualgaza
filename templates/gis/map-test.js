//DECONFLICT JQUERY AND OPENLAYERS
$j = jQuery.noConflict();

//ROLLOVER VARIABLES
var polygonToolTips;

//STYLE MAPS
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
lineStyleMap = new OpenLayers.StyleMap(
				{strokeWidth:3,
				strokeColor:'#FFFF00'});

function mapInit() {
	map = new OpenLayers.Map('map', {
		controls: [ ],
		projection : new OpenLayers.Projection("EPSG:900913"),
		displayProjection : new OpenLayers.Projection("EPSG:4326"), //EPSG:4326
		units : "m",
		maxResolution : "auto",
		maxExtent : new OpenLayers.Bounds(3801000,3660000,3850000,3710500), //gaza strip
		restrictedExtent : new OpenLayers.Bounds(3801000,3660000,3850000,3710500), //gaza strip
		minZoomLevel: 11,
		maxZoomLevel: 17});

	map.addControl(new OpenLayers.Control.Navigation());
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
			displayInLayerSwitcher:false,
		});
	map.addLayer(baseLayer);
	
	//STREET MAP LAYER
	var osmLayer = new OpenLayers.Layer.OSM.Mapnik("Street Map",
	{
		type: 'png', getURL: osm_getTileURL,
		displayOutsideMaxExtent: true, opacity: 1,
		isBaseLayer: false, visibility: true,
		attribution:"OpenStreetMap (cc)",
		visibility:false,
	});
	map.addLayer(osmLayer);
	
	//UNOSAT LAYER
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
	unosat_buildings.events.register('visibilitychanged', this, onDamageVisibiltyChanged);
	
	//VECTOR LAYERS
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
	
	//NEIGHBORHOOD CONTROLS
	{% if polygonLayerName %}
		polygonTooltips = new OpenLayers.Control.ToolTips({bgColor:"silver",textColor :"black", bold : true, opacity : 0.75});
		map.addControl(polygonTooltips);
		var polygonSelectControl = new OpenLayers.Control.newSelectFeature({{polygonLayerName}}_layer,
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
	view = map.getExtent();
	bounds = feature.geometry.bounds;
//	console.log(view);
//	console.log(bounds);
//doesn't work yet
	if (bounds.contains(view)) {
		//we're too close, don't zoom
		return;
	} else {
		map.zoomToExtent(bounds);	
	}
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
	$j.post("/test/neighborhoods_within_bounds/", 
		{bounds:map.calculateBounds().toGeometry().toString()},
		function(data) {
			$j("div").filter("#neighborhoods").html(data);
		}
	);
	
	if(unosat_buildings.visibility) {
		calculateVisibleDamage();
	}
}

function calculateVisibleDamage() {
	var counts = {
		"#destroyed":0,
		"#damaged":0,
		"#impact_field":0,
		"#impact_road":0,
		};

	var map_extent = map.getExtent();
	var minx = map_extent.left,
	   maxx = map_extent.right,
	   miny = map_extent.bottom,
	   maxy = map_extent.top;

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

	$j("div").filter("#damage").html( "Damage Analysis:<br>" +
		"Buildings Destroyed:" + numDestroyed + "<br>" +
		"Buildings Damaged:" + numDamaged + "<br>" +
		"Impact Craters:" + numImpact
		);
}

function onDamageVisibiltyChanged(layer) {
	if (layer.object.visibility){
		//wait a little bit for the kml to render
		setTimeout('calculateVisibleDamage()',250);
		$j("div").filter("#buildings").show();
	} else {
		$j("div").filter("#buildings").hide();
	}
}

