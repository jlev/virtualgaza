/* Copyright (c) 2006-2008 MetaCarta, Inc., published under the Clear BSD
 * license.  See http://svn.openlayers.org/trunk/openlayers/license.txt for the
 * full text of the license. */

/**
 * @requires OpenLayers/Control.js
 */

/**
 * Class: OpenLayers.Control.Legend
 * The legend control adds legend from layers to the map display. 
 * It uses 'legend' property of each layer.
 *
 * Inherits from:
 *  - <OpenLayers.Control>
 */
OpenLayers.Control.Legend = 
  OpenLayers.Class(OpenLayers.Control, {
    
    /**
     * APIProperty: seperator
     * {String} String used to seperate layers.
     */
    separator: "<br>",
       
    /**
     * Constructor: OpenLayers.Control.Legend 
     * 
     * Parameters:
     * options - {Object} Options for control.
     */
    initialize: function(options) {
        OpenLayers.Control.prototype.initialize.apply(this, arguments);
    },

    /** 
     * Method: destroy
     * Destroy control.
     */
    destroy: function() {
        this.map.events.un({
            "removelayer": this.updateLegend,
            "addlayer": this.updateLegend,
            "changelayer": this.updateLegend,
            "changebaselayer": this.updateLegend,
            scope: this
        });
        
        OpenLayers.Control.prototype.destroy.apply(this, arguments);
    },    
    
    /**
     * Method: draw
     * Initialize control.
     * 
     * Returns: 
     * {DOMElement} A reference to the DIV DOMElement containing the control
     */    
    draw: function() {
        OpenLayers.Control.prototype.draw.apply(this, arguments);
        
        this.map.events.on({
            'changebaselayer': this.updateLegend,
            'changelayer': this.updateLegend,
            'addlayer': this.updateLegend,
            'removelayer': this.updateLegend,
            scope: this
        });
        this.updateLegend();
        
        return this.div;    
    },

    /**
     * Method: updateLegend
     * Update legend string.
     */
    updateLegend: function() {
        var legend = [];
        if (this.map && this.map.layers) {
            for(var i=0, len=this.map.layers.length; i<len; i++) {
                var layer = this.map.layers[i];
                if (layer.legend && layer.getVisibility()) {
                    legend.push( layer.legend );
                }
            }  
            this.div.innerHTML = legend.join(this.separator);
        }
    },

    CLASS_NAME: "OpenLayers.Control.Legend"
});
