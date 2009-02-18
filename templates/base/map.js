function mapInit() {
	var map = new OpenLayers.Map('map', {
		controls: [ new OpenLayers.Control.Navigation() ],
		projection : new OpenLayers.Projection("EPSG:900913"),
		displayProjection : new OpenLayers.Projection("EPSG:4326"), //EPSG:4326
		units : "m",
		maxResolution : "auto",
//		maxExtent : new OpenLayers.Bounds(-20037508,-20037508,20037508,20037508), //whole world
		maxExtent : new OpenLayers.Bounds(3801000,3660000,3850000,3710500), //gaza strip
		restrictedExtent : new OpenLayers.Bounds(3801000,3660000,3850000,3710500), //gaza strip
		minZoomLevel: 11,
		maxZoomLevel: 17});
	map.addControl(new OpenLayers.Control.MousePosition());
	map.addControl(new OpenLayers.Control.customLayerSwitcher({'div':OpenLayers.Util.getElement('mapKey'),
	activeColor:'silver'}));
	map.addControl(new OpenLayers.Control.ScaleLine());
	
	//could pass these in from views, but easy enough to just define them here...	
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
		"Google Aerial",{type: {{ mapType }}, numZoomLevels:7,sphericalMercator:true,displayInLayerSwitcher:false}
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
	{%endfor%}
	
	map.zoomToExtent({{zoomLayer}}_layer.getDataExtent());

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
	
	if (numAuthors > 0) {
		var display = "";
		if (numAuthors == 1) {
			display += numAuthors + " author<br>";
		} else {
			display += numAuthors + " authors<br>";
		}

		display += '<div class=authorFaces>';
		var i = 1;
		for (i=1;i<=numAuthors;i++) {
			display += '<img src="{{MEDIA_URL}}pins/male.png">';
			if ((i % 5) == 0) {
				display += '<br>';
			}
		}
		display += '</div>';
	
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

//select controls
//bombings
{%if popupLayerName %}
	var pointToolTips = new OpenLayers.Control.ToolTips({bgColor:"red",textColor :"black", bold : false, opacity : 0.75,
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
{%endif%}

//neighborhoods
{% if polygonLayerName %}
	var polygonTooltips = new OpenLayers.Control.ToolTips({bgColor:"silver",textColor :"black", bold : true, opacity : 0.75});
	map.addControl(polygonTooltips);
	var polygonSelectControl = new OpenLayers.Control.newSelectFeature({{polygonLayerName}}_layer,
					{onClickSelect:gotoWindowLink, onHoverSelect:polygonOver, onHoverUnselect:polygonOut});
	map.addControl(polygonSelectControl);
	polygonSelectControl.activate();
{%endif%}
} //end mapInit