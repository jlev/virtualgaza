function init() {
	var map = new OpenLayers.Map('map', {
		projection : new OpenLayers.Projection("EPSG:900913"),
		displayProjection : new OpenLayers.Projection("EPSG:900913"), //EPSG:4326
		units : "m",
		maxResolution : 156543.0339,
		maxExtent : new OpenLayers.Bounds(-20037508,-20037508,20037508,20037508), //whole world
		restrictedExtent : new OpenLayers.Bounds(3801000,3660000,3850000,3710500), //gaza strip
		minZoomLevel: 11,
		maxZoomLevel: 17});
//	map.addControl(new OpenLayers.Control.MousePosition());
//	map.addControl(new OpenLayers.Control.Permalink('permalink'));
	map.addControl(new OpenLayers.Control.customLayerSwitcher({'div':OpenLayers.Util.getElement('mapKey'),
	activeColor:'silver'}));
	
	//could pass these in from views, but easy enough to just define them here...
	var polygonStyleMap = new OpenLayers.StyleMap(
					{strokeWidth:1,
					strokeColor:'#FF6600',
					fillColor:'#FF6600',
					fillOpacity:0.1,
					pointerEvents: "visiblePainted",
					label : "${name}",
					fontColor: "white",
					fontSize: "10px",
					fontFamily: "Arial, sans-serif",
					fontWeight: "bold",
					labelAlign: "center"});
	var pointStyleMap = new OpenLayers.StyleMap(
				{pointRadius: 10,
				fillOpacity:1,
				externalGraphic:"{{MEDIA_URL}}pins/male.png"});
	var bombingStyleMap = new OpenLayers.StyleMap(
			{pointRadius: 10,
			fillOpacity:1,
			externalGraphic:"{{MEDIA_URL}}pins/hospital.png"});
	var lineStyleMap = new OpenLayers.StyleMap(
					{strokeWidth:3,
					strokeColor:'#FFFF00'});
	
	var baseLayer = new OpenLayers.Layer.Google(
		"Google Aerial",{type: {{ mapType }}, numZoomLevels: 20,sphericalMercator:true,displayInLayerSwitcher:false}
	);
	map.addLayer(baseLayer);
	
	var geojson_format = new OpenLayers.Format.GeoJSON();
	
	{% for layer in vectorLayers %}
		var {{layer.name}}_layer = new OpenLayers.Layer.Vector("{{layer.name}}",{'styleMap':{{layer.styleName}}});
		{% for object in layer.list %}
			var {{layer.name}}_{{forloop.counter}} = geojson_format.read({{ object|safe }});
			{{layer.name}}_layer.addFeatures({{layer.name}}_{{forloop.counter}});
		{% endfor %}
		map.addLayer({{layer.name}}_layer);
		map.zoomToExtent({{layer.name}}_layer.getDataExtent());
	{%endfor%}

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
function toolTipsOver(feature) {
	tooltips.show({html:feature.attributes.displayName});
}
function toolTipsOut(feature){
	tooltips.hide();
}

//select controls
var tooltips = new OpenLayers.Control.ToolTips({bgColor:"red",textColor :"black", bold : true, opacity : 0.50});
map.addControl(tooltips);
var pointSelectControl = new OpenLayers.Control.newSelectFeature({{tooltipLayerName}}_layer,
				{onClickSelect:gotoWindowLink, onHoverSelect:toolTipsOver, onHoverUnselect:toolTipsOut});
map.addControl(pointSelectControl);
pointSelectControl.activate();
} //end init