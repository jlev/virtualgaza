/* Copyright (c) 2006-2008 MetaCarta, Inc., published under the Clear BSD
 * license.  See http://svn.openlayers.org/trunk/openlayers/license.txt for the
 * full text of the license. */


/**
 * @requires OpenLayers/Control.js
 * @requires OpenLayers/Feature/Vector.js
 * @requires OpenLayers/Handler/Feature.js
 */

/**
 * Class: OpenLayers.Control.SelectFeature
 * Selects vector features from a given layer on click or hover.
 *
 * Inherits from:
 *  - <OpenLayers.Control>
 */
OpenLayers.Control.newSelectFeature = OpenLayers.Class(OpenLayers.Control, {

    /**
     * Property: multipleKey
     * {String} An event modifier ('altKey' or 'shiftKey') that temporarily sets
     *     the <multiple> property to true.  Default is null.
     */
    multipleKey: null,

    /**
     * Property: toggleKey
     * {String} An event modifier ('altKey' or 'shiftKey') that temporarily sets
     *     the <toggle> property to true.  Default is null.
     */
    toggleKey: null,

    /**
     * APIProperty: multiple
     * {Boolean} Allow selection of multiple geometries.  Default is false.
     */
    multiple: false,

    /**
     * APIProperty: clickout
     * {Boolean} Unselect features when clicking outside any feature.
     *     Default is true.
     */
    clickout: true,

    /**
     * APIProperty: toggle
     * {Boolean} Unselect a selected feature on click.  Default is false.  Only
     *     has meaning if hover is false.
     */
    toggle: false,

    /**
     * APIProperty: hover
     * {Boolean} Select on mouse over and deselect on mouse out.  If true, this
     * ignores clicks and only listens to mouse moves.
     */
    hover: false,

    /**
     * APIProperty: onSelect
     * {Function} Optional function to be called when a feature is selected.
     * The function should expect to be called with a feature.
     */
    onSelect: function() {},

    /**
     * APIProperty: onUnselect
     * {Function} Optional function to be called when a feature is unselected.
     *                  The function should expect to be called with a feature.
     */
    onUnselect: function() {},

    /**
     * APIProperty: onHoverSelect
     * {Function} Optional function to be called when a feature is selected.
     * The function should expect to be called with a feature.
     */
    onHoverSelect: function() {},

    /**
     * APIProperty: onHoverUnselect
     * {Function} Optional function to be called when a feature is selected.
     * The function should expect to be called with a feature.
     */
    onHoverUnselect: function() {},

    /**
     * APIProperty: onClickSelect
     * {Function} Optional function to be called when a feature is selected.
     * The function should expect to be called with a feature.
     */
    onClickSelect: function() {},

    /**
     * APIProperty: onClickUnselect
     * {Function} Optional function to be called when a feature is selected.
     * The function should expect to be called with a feature.
     */
    onClickUnselect: function() {},

    /**
     * APIProperty: geometryTypes
     * {Array(String)} To restrict selecting to a limited set of geometry types,
     *     send a list of strings corresponding to the geometry class names.
     */
    geometryTypes: null,

    /**
     * Property: layer
     * {<OpenLayers.Layer.Vector>}
     */
    layer: null,

    /**
     * APIProperty: callbacks
     * {Object} The functions that are sent to the handler for callback
     */
    callbacks: null,

    /**
     * APIProperty: selectStyle
     * {Object} Hash of styles
     */
    selectStyle: null,

    /**
     * Property: renderIntent
     * {String} key used to retrieve the select style from the layer's
     * style map.
     */
    renderIntent: "select",

    /**
     * Property: handler
     * {<OpenLayers.Handler.Feature>}
     */
    handler: null,

    /**
     * Constructor: <OpenLayers.Control.SelectFeature>
     *
     * Parameters:
     * layer - {<OpenLayers.Layer.Vector>}
     * options - {Object}
     */
    initialize: function(layer, options) {
        OpenLayers.Control.prototype.initialize.apply(this, [options]);
        this.layer = layer;
        this.callbacks = OpenLayers.Util.extend({
                                                  click: this.clickFeature,
                                                  clickout: this.clickoutFeature,
                                                  over: this.overFeature,
                                                  out: this.outFeature
                                                }, this.callbacks);
        var handlerOptions = { geometryTypes: this.geometryTypes};
        this.handler = new OpenLayers.Handler.Feature(this, layer,
                                                      this.callbacks,
                                                      handlerOptions);
    },

    /**
     * Method: unselectAll
     * Unselect all selected features.  To unselect all except for a single
     *     feature, set the options.except property to the feature.
     *
     * Parameters:
     * options - {Object} Optional configuration object.
     */
    unselectAll: function(options) {
        // we'll want an option to supress notification here
        var feature;
        for(var i=this.layer.selectedFeatures.length-1; i>=0; --i) {
            feature = this.layer.selectedFeatures[i];
            if(!options || options.except != feature) {
                this.unselect(feature, "click");
            }
        }
    },

    /**
     * Method: clickFeature
     * Called on click in a feature
     * Only responds if this.hover is false.
     *
     * Parameters:
     * feature - {<OpenLayers.Feature.Vector>}
     */
    clickFeature: function(feature) {
        if((this.onSelect.name != "" || this.onClickSelect.name != "") && !this.hover) {
            var selected = (OpenLayers.Util.indexOf(this.layer.selectedFeatures,
                                                    feature) > -1);
            if(selected) {
                if(this.toggleSelect()) {
                    this.unselect(feature);
                } else if(!this.multipleSelect()) {
                    this.unselectAll({except: feature});
                }
            } else {
                if(!this.multipleSelect()) {
                    this.unselectAll({except: feature});
                }
            }
            this.select(feature, "click");
        }
    },

    /**
     * Method: multipleSelect
     * Allow for multiple selected features based on <multiple> property and
     *     <multipleKey> event modifier.
     *
     * Returns:
     * {Boolean} Allow for multiple selected features.
     */
    multipleSelect: function() {
        return this.multiple || this.handler.evt[this.multipleKey];
    },

    /**
     * Method: toggleSelect
     * Event should toggle the selected state of a feature based on <toggle>
     *     property and <toggleKey> event modifier.
     *
     * Returns:
     * {Boolean} Toggle the selected state of a feature.
     */
    toggleSelect: function() {
        return this.toggle || this.handler.evt[this.toggleKey];
    },

    /**
     * Method: clickoutFeature
     * Called on click outside a previously clicked (selected) feature.
     * Only responds if this.hover is false.
     *
     * Parameters:
     * feature - {<OpenLayers.Vector.Feature>}
     */
    clickoutFeature: function(feature) {
        /* FIXME  atm, this does not allow the clickout when a hover is defined
                  this is because when there is a function defined for hover, the feature
                  gets unselected, so there is nothing relating the click out */
        if(((this.onClickUnselect.name != "" || this.onHoverSelect.name == "") && !this.hover) && this.clickout) {
            this.unselectAll();
        }
    },

    /**
     * Method: overFeature
     * Called on over a feature.
     * Only responds if this.hover is true.
     *
     * Parameters:
     * feature - {<OpenLayers.Feature.Vector>}
     */
    overFeature: function(feature) {
        if((this.onHoverSelect.name != "" || this.hover) &&
           (OpenLayers.Util.indexOf(this.layer.selectedFeatures, feature) == -1)) {
            this.select(feature, "hover");
        }
    },

    /**
     * Method: outFeature
     * Called on out of a selected feature.
     * Only responds if this.hover is true.
     *
     * Parameters:
     * feature - {<OpenLayers.Feature.Vector>}
     */
    outFeature: function(feature) {
        /* FIXME working here */
        if(this.onHoverUnselect.name != "" || this.hover) {
            this.unselect(feature, "hover");
        }
    },

    /**
     * Method: select
     * Add feature to the layer's selectedFeature array, render the feature as
     * selected, and call the onSelect function.
     *
     * Parameters:
     * feature - {<OpenLayers.Feature.Vector>}
     */
    select: function(feature, evt) {
        this.layer.selectedFeatures.push(feature);

        var selectStyle = this.selectStyle || this.renderIntent;

        this.layer.drawFeature(feature, selectStyle);
        this.layer.events.triggerEvent("featureselected", {feature: feature});

        switch(evt) {
            case "hover":
               this.onHoverSelect(feature);
               break;
            case "click":
               if(this.onClickSelect.name != "") {
                  this.onClickSelect(feature);
               } else if (this.onSelect.name != "") {
                  this.onSelect(feature);
               }
               break;
            default:
               this.onSelect(feature);
               break;
        }
    },

    /**
     * Method: unselect
     * Remove feature from the layer's selectedFeature array, render the feature as
     * normal, and call the onUnselect function.
     *
     * Parameters:
     * feature - {<OpenLayers.Feature.Vector>}
     */
    unselect: function(feature, evt) {
        // Store feature style for restoration later
        this.layer.drawFeature(feature, "default");
        OpenLayers.Util.removeItem(this.layer.selectedFeatures, feature);
        this.layer.events.triggerEvent("featureunselected", {feature: feature});

        switch(evt) {
            case "hover":
               this.onHoverUnselect(feature);
               break;
            case "click":
               if(this.onClickUnselect.name != "") {
                  this.onClickUnselect(feature);
               } else if (this.onUnselect.name != "") {
                  this.onUnselect(feature);
               }
               break;
            default:
               this.onUnselect(feature);
               break;
        }
    },

    /**
     * Method: setMap
     * Set the map property for the control.
     *
     * Parameters:
     * map - {<OpenLayers.Map>}
     */
    setMap: function(map) {
        this.handler.setMap(map);
        OpenLayers.Control.prototype.setMap.apply(this, arguments);
    },

    CLASS_NAME: "OpenLayers.Control.newSelectFeature"
});
