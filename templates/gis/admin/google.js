{% extends "gis/admin/openlayers-modified.js" %}
{% block base_layer %}new OpenLayers.Layer.Google("Google Base Layer", {'type': G_SATELLITE_MAP, 'sphericalMercator' : true, 'layerswitcher':true});
{% endblock %}

{% block extra_layers %}

var osmLayer = new OpenLayers.Layer.OSM.Mapnik("Street Map",
{
	type: 'png', getURL: osm_getTileURL,
	displayOutsideMaxExtent: true, opacity: 0.75,
	isBaseLayer: false, visibility: true,
	attribution:"OpenStreetMap (cc)",
	visibility:false,
});
{{ module }}.map.addLayer(osmLayer);

{% endblock %}


{%block extrafunctions %}
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
{%endblock%}