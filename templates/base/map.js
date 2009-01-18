function init() {
	map = new OpenLayers.Map('map', {
		projection : new OpenLayers.Projection("EPSG:900913"),
		displayProjection : new OpenLayers.Projection("EPSG:4326"),
		units : "m",
		maxResolution : 156543.0339,
		maxExtent : new OpenLayers.Bounds(-20037508,-20037508,20037508,20037508)
	});
	map.addControl(new OpenLayers.Control.LayerSwitcher());
	
	var polygonStyleMap = new OpenLayers.StyleMap(
					{'strokeWidth':1,
					'strokeColor':'#FF6600',
					'fillColor':'#FF6600',
					'fillOpacity':0.1,
					});
	var pointStyleMap = new OpenLayers.StyleMap(
					{'pointRadius': 10, //why does this control image size?
					'fillOpacity':1,
					'externalGraphic':'/media/pins/male.png'
					});
	var lineStyleMap = new OpenLayers.StyleMap(
					{'strokeWidth':3,
					'strokeColor':'#FFFF00',
					});
	
	var baseLayer = new OpenLayers.Layer.Google(
		"Google Aerial",{type: {{ mapType }}, numZoomLevels: 20,sphericalMercator:true,}
	);
	map.addLayer(baseLayer);
	
	var geojson_format = new OpenLayers.Format.GeoJSON();
	var polygon_layer = new OpenLayers.Layer.Vector(" {{ vector_layer_name }} ",{'styleMap': polygonStyleMap});

	{% if poly_list %}
		{% for poly in poly_list %}
			var polygon_bounds_{{ forloop.counter }} = {{ poly|safe }}; 
			var polygon_feature_{{forloop.counter}} = geojson_format.read(polygon_bounds_{{ forloop.counter }});
			polygon_layer.addFeatures(polygon_feature_{{ forloop.counter }});
		{% endfor %}
		map.addLayer(polygon_layer);
		map.zoomToExtent(polygon_layer.getDataExtent());
	{% endif %}

	{% if point_list %}
		var point_layer = new OpenLayers.Layer.Vector(" {{ point_layer_name }} ",{'styleMap': pointStyleMap});
		{% for point in point_list %}
			var point_{{ forloop.counter }} = {{ point|safe }};
			point_layer.addFeatures(geojson_format.read(point_{{ forloop.counter }}));
		{% endfor %}
		map.addLayer(point_layer);
		{% if not poly_list %}
			map.zoomToExtent(point_layer.getDataExtent());
			map.zoomOut();
			map.zoomOut(); //there isn't imagery at the closest levels
		{% endif %}
	{% endif %}

	{% if line_list %}
		var line_layer = new OpenLayers.Layer.Vector(" {{ line_layer_name }} ",{'styleMap': lineStyleMap});
		{% for line in line_list %}
			var line_{{ forloop.counter }} = {{ line|safe }}; 
			var line_feature_{{forloop.counter}} = geojson_format.read(line_{{ forloop.counter }});
			line_layer.addFeatures(line_feature_{{ forloop.counter }});
		{% endfor %}
		map.addLayer(line_layer);
	{% endif %}
	
	
	//center manually?
	
	//SELECT CONTROLS
	var selectControl, selectedFeature;
	function onPopupClose(evt) {
		selectControl.unselect(selectedFeature);
	}
	function onFeatureSelect(feature) {
		selectedFeature = feature;
		popup = new OpenLayers.Popup.FramedCloud("chicken", 
			feature.geometry.getBounds().getCenterLonLat(),
			null,
			"<div style='font-size:.8em'>Feature: " + feature.id + "</div>",
			null, true, onPopupClose);
		feature.popup = popup;
		map.addPopup(popup);
	 }
	function onFeatureUnselect(feature) {
		map.removePopup(feature.popup);
		feature.popup.destroy();
		feature.popup = null;
	}
	selectControl = new OpenLayers.Control.SelectFeature(polygon_layer,
	                {onSelect: onFeatureSelect, onUnselect: onFeatureUnselect});
	
}