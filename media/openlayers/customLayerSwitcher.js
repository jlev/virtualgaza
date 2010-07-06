/* Copyright (c) 2006-2008 MetaCarta, Inc., published under the Clear BSD
 * license.  See http://svn.openlayers.org/trunk/openlayers/license.txt for the
 * full text of the license. */

/** 
 * @requires OpenLayers/Control.js
 */

/**
 * Class: OpenLayers.Control.LayerSwitcher
 *
 * Inherits from:
 *  - <OpenLayers.Control>
 */
OpenLayers.Control.customLayerSwitcher = 
  OpenLayers.Class(OpenLayers.Control, {

    /**  
     * Property: activeColor
     * {String}
     */
    activeColor: "darkblue",
    
    /**  
     * Property: layerStates 
     * {Array(Object)} Basically a copy of the "state" of the map's layers 
     *     the last time the control was drawn. We have this in order to avoid
     *     unnecessarily redrawing the control.
     */
    layerStates: null,
    

  // DOM Elements
  
    /**
     * Property: layersDiv
     * {DOMElement} 
     */
    layersDiv: null,
    
    /** 
     * Property: baseLayersDiv
     * {DOMElement}
     */
    baseLayersDiv: null,

    /** 
     * Property: baseLayers
     * {Array(<OpenLayers.Layer>)}
     */
    baseLayers: null,
    
    
    /** 
     * Property: dataLbl
     * {DOMElement} 
     */
    dataLbl: null,
    
    /** 
     * Property: dataLayersDiv
     * {DOMElement} 
     */
    dataLayersDiv: null,

    /** 
     * Property: dataLayers
     * {Array(<OpenLayers.Layer>)} 
     */
    dataLayers: null,


    /** 
     * Property: minimizeDiv
     * {DOMElement} 
     */
    minimizeDiv: null,

    /** 
     * Property: maximizeDiv
     * {DOMElement} 
     */
    maximizeDiv: null,
    
    /**
     * APIProperty: ascending
     * {Boolean} 
     */
    ascending: true,

    /**
     * Property: groupDivs
     * Object with {DOMElements}, {Booleans} and {Strings}
     */
     groups: {
              groupDivs:{},
              checked: {},
              layers:{},
              display: {}
              },

    /**
     * Constructor: OpenLayers.Control.LayerSwitcher
     * 
     * Parameters:
     * options - {Object}
     */
    initialize: function(options) {
        OpenLayers.Control.prototype.initialize.apply(this, arguments);
        this.layerStates = [];
    },

    /**
     * APIMethod: destroy 
     */    
    destroy: function() {
        
        OpenLayers.Event.stopObservingElement(this.div);

        OpenLayers.Event.stopObservingElement(this.minimizeDiv);
        OpenLayers.Event.stopObservingElement(this.maximizeDiv);

        //clear out layers info and unregister their events 
        this.clearLayersArray("base");
        this.clearLayersArray("data");
        
        this.map.events.un({
            "addlayer": this.redraw,
            "changelayer": this.redraw,
            "removelayer": this.redraw,
            "changebaselayer": this.redraw,
            scope: this
        });
        
        OpenLayers.Control.prototype.destroy.apply(this, arguments);
    },

    /** 
     * Method: setMap
     *
     * Properties:
     * map - {<OpenLayers.Map>} 
     */
    setMap: function(map) {
        OpenLayers.Control.prototype.setMap.apply(this, arguments);

        this.map.events.on({
            "addlayer": this.redraw,
            "changelayer": this.redraw,
            "removelayer": this.redraw,
            "changebaselayer": this.redraw,
            scope: this
        });
    },

    /**
     * Method: draw
     *
     * Returns:
     * {DOMElement} A reference to the DIV DOMElement containing the 
     *     switcher tabs.
     */  
    draw: function() {
        OpenLayers.Control.prototype.draw.apply(this);

        // create layout divs
        this.loadContents();

        // set mode to minimize
        if(!this.outsideViewport) {
            this.minimizeControl();
        }

        // populate div with current info
        this.redraw();    

        return this.div;
    },

    /** 
     * Method: clearLayersArray
     * User specifies either "base" or "data". we then clear all the
     *     corresponding listeners, the div, and reinitialize a new array.
     * 
     * Parameters:
     * layersType - {String}  
     */
    clearLayersArray: function(layersType) {
        var layers = this[layersType + "Layers"];
        if (layers) {
            for(var i=0, len=layers.length; i<len ; i++) {
                var layer = layers[i];
                OpenLayers.Event.stopObservingElement(layer.inputElem);
                OpenLayers.Event.stopObservingElement(layer.labelSpan);
            }
        }
        this[layersType + "LayersDiv"].innerHTML = "";
        this[layersType + "Layers"] = [];
        this.groups.groupDivs = {};
    },


    /**
     * Method: checkRedraw
     * Checks if the layer state has changed since the last redraw() call.
     * 
     * Returns:
     * {Boolean} The layer state changed since the last redraw() call. 
     */
    checkRedraw: function() {
        var redraw = false;
        if ( !this.layerStates.length ||
             (this.map.layers.length != this.layerStates.length) ) {
            redraw = true;
        } else {
            for (var i=0, len=this.layerStates.length; i<len; i++) {
                var layerState = this.layerStates[i];
                var layer = this.map.layers[i];
                if ( (layerState.name != layer.name) || 
                     (layerState.inRange != layer.inRange) || 
                     (layerState.id != layer.id) || 
                     (layerState.visibility != layer.visibility) ) {
                    redraw = true;
                    break;
                }    
            }
        }    
        return redraw;
    },
    
    /** 
     * Method: redraw
     * Goes through and takes the current state of the Map and rebuilds the
     *     control to display that state. Groups base layers into a 
     *     radio-button group and lists each data layer with a checkbox.
     *
     * Returns: 
     * {DOMElement} A reference to the DIV DOMElement containing the control
     */  
    redraw: function() {
        //if the state hasn't changed since last redraw, no need 
        // to do anything. Just return the existing div.
        if (!this.checkRedraw()) { 
            return this.div; 
        } 

        //clear out previous layers 
        this.clearLayersArray("base");
        this.clearLayersArray("data");
        
        var containsOverlays = false;
        var containsBaseLayers = false;
        var i;
        var layer;
        
        // Save state -- for checking layer if the map state changed.
        // We save this before redrawing, because in the process of redrawing
        // we will trigger more visibility changes, and we want to not redraw
        // and enter an infinite loop.
        var len = this.map.layers.length;
        this.layerStates = new Array(this.map.layers.length);
        for (i=0; i <len; i++) {
            layer = this.map.layers[i];
            this.layerStates[i] = {
                'name': layer.name, 
                'visibility': layer.visibility,
                'inRange': layer.inRange,
                'id': layer.id
            };
           
           // create group divs
           if (layer.group && !layer.isBaseLayer) {
               layer.group = layer.group.replace(/\/$/,"");
               layer.group = layer.group.replace(/^\//,"");
               this.createGroupDiv(layer.group);
           }
        }    

        var layers = this.map.layers.slice();
        if (!this.ascending) { layers.reverse(); }
        for(i=0, len=layers.length; i<len; i++) {
            layer = layers[i];
            var baseLayer = layer.isBaseLayer;
            var layerDiv = null;

            if (layer.displayInLayerSwitcher) {

                if (baseLayer) {
                    containsBaseLayers = true;
                } else {
                    containsOverlays = true;
                }    

                // only check a baselayer if it is *the* baselayer, check data
                //  layers if they are visible
                var checked = (baseLayer) ? (layer == this.map.baseLayer) : layer.getVisibility();
    
                // create input element
                var inputElem = document.createElement("input");
                inputElem.id = this.id + "_input_" + layer.name;
                inputElem.name = (baseLayer) ? "baseLayers" : layer.name;
                inputElem.type = (baseLayer) ? "radio" : "checkbox";
                inputElem.value = layer.name;
                inputElem.checked = checked;
                inputElem.defaultChecked = checked;

                if (!baseLayer && !layer.inRange) {
                    inputElem.disabled = true;
                }
                var context = {
                    'inputElem': inputElem,
                    'layer': layer,
                    'layerSwitcher': this
                };
                OpenLayers.Event.observe(inputElem, "mouseup", 
                    OpenLayers.Function.bindAsEventListener(this.onInputClick,
                                                            context)
                );
                
                // create span
                var labelSpan = document.createElement("span");
                if (!baseLayer && !layer.inRange) {
                    labelSpan.style.color = "gray";
                }
                labelSpan.innerHTML = layer.name;
                labelSpan.style.verticalAlign = (baseLayer) ? "bottom" : "baseline";
                OpenLayers.Event.observe(labelSpan, "click", 
                    OpenLayers.Function.bindAsEventListener(this.onInputClick,
                                                            context)
                );
                // create line break
                //var br = document.createElement("br");
//added this instead of line break between elems
                labelSpan.style.paddingRight = "5px";
                
                var groupArray = (baseLayer) ? this.baseLayers : this.dataLayers;
                groupArray.push({
                    'layer': layer,
                    'inputElem': inputElem,
                    'labelSpan': labelSpan
                });
                                                     
    
                var groupDiv = (baseLayer) ? this.baseLayersDiv
                                           : this.dataLayersDiv;
               // layer group for data layers 
               if (!baseLayer) {
                   // no group
                   if (layer.group == null)  {
                       this.dataLayersDiv.appendChild(inputElem);
                       this.dataLayersDiv.appendChild(labelSpan);
                       //this.dataLayersDiv.appendChild(br);
                   }
                   // group exists it is most probably allready there
                   else {
                       var groupname = layer.group;
                       var div = this.groups.groupDivs[groupname];
                       div.appendChild(inputElem);
                       div.appendChild(labelSpan);
                       //div.appendChild(br);
                       // append layer to the group
                       this.appendLayerToGroups(layer);
                   }
               }
               // base layers
               else {
                   this.baseLayersDiv.appendChild(inputElem);
                   this.baseLayersDiv.appendChild(labelSpan);
                   //this.baseLayersDiv.appendChild(br);
               }
            }
        }

        // if no overlays, dont display the overlay label
        this.dataLbl.style.display = (containsOverlays) ? "" : "none";        
        
        // if no baselayers, dont display the baselayer label
        this.baseLbl.style.display = (containsBaseLayers) ? "" : "none";        

        return this.div;
    },

    /** 
     * Method:
     * A label has been clicked, check or uncheck its corresponding input
     * 
     * Parameters:
     * e - {Event} 
     *
     * Context:  
     *  - {DOMElement} inputElem
     *  - {<OpenLayers.Control.LayerSwitcher>} layerSwitcher
     *  - {<OpenLayers.Layer>} layer
     */

    onInputClick: function(e) {

        if (!this.inputElem.disabled) {
            if (this.inputElem.type == "radio") {
                this.inputElem.checked = true;
                this.layer.map.setBaseLayer(this.layer);
            } else {
                this.inputElem.checked = !this.inputElem.checked;
                this.layerSwitcher.updateMap();
            }
        }
        OpenLayers.Event.stop(e);
    },

    /** 
     * Method:
     * A group label has been clicked, check or uncheck its corresponding input
     * 
     * Parameters:
     * e - {Event} 
     *
     * Context:  
     *  - {DOMElement} inputElem
     *  - {<OpenLayers.Control.LayerSwitcher>} layerSwitcher
     *  - {DOMElement} groupDiv
     */

    onInputGroupClick: function(e) {

        // setup the check value
        var check = !this.inputElem.checked;

        // get all <input></input> tags in this div
        var inputs = this.groupDiv.getElementsByTagName("input");

        // check the group input, other inputs are in groupDiv,
        // inputElem is in parent div
        this.inputElem.checked=check;

        // store to groupCheckd structure, where it can be later found
        this.layerSwitcher.groups.checked[this.inputElem.value] = check;

        for (var i = 0; i < inputs.length; i++) {
            // same as above
            inputs[i].checked=check;
            this.layerSwitcher.groups.checked[inputs[i].value] = check;
        }

        // groups are done, now the layers
        var dataLayers = this.layerSwitcher.dataLayers;
        for (var j = 0; j < dataLayers.length; j++) {
            var layerEntry = dataLayers[j];   
            if (this.layerSwitcher.isInGroup(
                    this.inputElem.value,layerEntry.layer)) {
                layerEntry.inputElem.checked = check;
                layerEntry.layer.setVisibility(check);
            }
        }

        OpenLayers.Event.stop(e);
    },
    
    /**
     * Method: onLayerClick
     * Need to update the map accordingly whenever user clicks in either of
     *     the layers.
     * 
     * Parameters: 
     * e - {Event} 
     */
    onLayerClick: function(e) {
        this.updateMap();
    },

    /**
     * Method: onGroupClick
     * Make the div with layers invisible
     * 
     * Context: 
     * layergroup - {String} 
     * groups - {Array} of {DOMElements}
     */
    onGroupClick: function(e) {
        var layergroup = this.layergroup;
        var div = this.groups.groupDivs[layergroup];
        if (div) {
            if (div.style.display != "block") {
                div.style.display = "block";
                this.groups.display[layergroup] = "block";
            }
            else {
                div.style.display = "none";
                this.groups.display[layergroup] = "none";
            }
        }
    },

    /** 
     * Method: onRemoveLayerClick
     * 
     * 
     * Parameters:
     * e - {Event} 
     *
     * Context:  
     *  - {Layer} Layer
     */

    onRemoveLayerClick: function(e) {
        
        var map = this.layer.map;
        map.removeLayer(this.layer,true);

        OpenLayers.Event.stop(e);
    },

    /** 
     * Method: onMoveLayerClick
     * 
     * 
     * Parameters:
     * e - {Event} 
     *
     * Context:  
     *  - {Layer} Layer
     *  - {Boolean} up
     *  - layerSwitcher {OpenLayers.Control}
     */

    onMoveLayerClick: function(e) {
        
        var map = this.layer.map;
        var idx = null;
        var newidx = null;
        var layers = map.layers;
        var tmplayer = null;

        // get layer index
        for (var i = 0; i < map.layers.length; i++) {
            if (this.layer == map.layers[i]) {
                idx = i;
                break;
            }
        }

        // move up index
        if (this.up == true) {
            i = 1;
            while (1) {
                newidx = idx-i;
                if (newidx <= 0 ) {
                    newidx = 0;
                    break;
                }
                else if (map.layers[newidx].displayInLayerSwitcher == true && 
                    map.layers[newidx].group == map.layers[idx].group) {
                    break;
                }
                else {
                    i += 1;
                }
            }
        }
        // get down index
        else {
            i = 1;
            while (1) {
                newidx = idx+i;
                if (newidx >= map.getNumLayers()) {
                    newidx = map.getNumLayers()-1;
                    break;
                }
                else if (map.layers[newidx].displayInLayerSwitcher == true &&
                    map.layers[newidx].group == map.layers[idx].group) {
                    break;
                }
                else {
                    i += 1;
                }
            }
        }

        // switch
        map.raiseLayer(map.layers[idx], newidx-idx);

        this.layerSwitcher.redraw();
        OpenLayers.Event.stop(e);
    },

    /** 
     * Method: onOpacityLayerClick
     * 
     * 
     * Parameters:
     * e - {Event} 
     *
     * Context:  
     *  - {Layer} Layer
     *  - {Boolean} up
     *  - layerSwitcher {OpenLayers.Control}
     */

    onOpacityLayerClick: function(e) {
        
        if (this.layer.opacity == undefined) {
            this.layer.opacity = 1;
        }

        var opacity = this.layer.opacity;



        opacity = this.up == true ? opacity+0.1 : opacity-0.1;
        opacity = opacity < 0 ? 0 : opacity;
        opacity = opacity > 1 ? 1 : opacity;
        this.layer.setOpacity(opacity);

        //this.layerSwitcher.redraw();
        OpenLayers.Event.stop(e);
    },

    /** 
     * Method: onZoomToLayer
     * 
     * 
     * Parameters:
     * e - {Event} 
     *
     * Context:  
     *  - {Layer} Layer
     *  - layerSwitcher {OpenLayers.Control}
     */

    onZoomToLayer: function(e) {
        
        var map = this.layer.map;
        map.zoomToExtent(this.layer.maxExtent);

        //this.layerSwitcher.redraw();
        OpenLayers.Event.stop(e);
    },

    /** 
     * Method: updateMap
     * Cycles through the loaded data and base layer input arrays and makes
     *     the necessary calls to the Map object such that that the map's 
     *     visual state corresponds to what the user has selected in 
     *     the control.
     */
    updateMap: function() {

        // set the newly selected base layer        
        for(var i=0, len=this.baseLayers.length; i<len; i++) {
            var layerEntry = this.baseLayers[i];
            if (layerEntry.inputElem.checked) {
                this.map.setBaseLayer(layerEntry.layer, false);
            }
        }

        // set the correct visibilities for the overlays
        for(var i=0, len=this.dataLayers.length; i<len; i++) {
            var layerEntry = this.dataLayers[i];   
            layerEntry.layer.setVisibility(layerEntry.inputElem.checked);
        }

    },

    /** 
     * Method: maximizeControl
     * Set up the labels and divs for the control
     * 
     * Parameters:
     * e - {Event} 
     */
    maximizeControl: function(e) {

        //HACK HACK HACK - find a way to auto-size this layerswitcher
        /*this.div.style.width = "20em";
        this.div.style.height = "";*/

        this.showControls(false);

        if (e != null) {
            OpenLayers.Event.stop(e);                                            
        }
    },
    
    /** 
     * Method: minimizeControl
     * Hide all the contents of the control, shrink the size, 
     *     add the maximize icon
     *
     * Parameters:
     * e - {Event} 
     */
    minimizeControl: function(e) {

        this.div.style.width = "0px";
        this.div.style.height = "0px";

        this.showControls(true);

        if (e != null) {
            OpenLayers.Event.stop(e);                                            
        }
    },

    /**
     * Method: showControls
     * Hide/Show all LayerSwitcher controls depending on whether we are
     *     minimized or not
     * 
     * Parameters:
     * minimize - {Boolean}
     */
    showControls: function(minimize) {

        this.maximizeDiv.style.display = minimize ? "" : "none";
        this.minimizeDiv.style.display = minimize ? "none" : "";

        this.layersDiv.style.display = minimize ? "none" : "";
    },
    
    /** 
     * Method: loadContents
     * Set up the labels and divs for the control
     */
    loadContents: function() {

        //configure main div
        /*this.div.style.position = "absolute";
        this.div.style.top = "25px";
        this.div.style.right = "0px";
        this.div.style.left = "";
        this.div.style.fontFamily = "sans-serif";
        this.div.style.fontWeight = "bold";
        this.div.style.marginTop = "3px";
        this.div.style.marginLeft = "3px";
        this.div.style.marginBottom = "3px";
        this.div.style.fontSize = "smaller";   
        this.div.style.color = "white";   
        this.div.style.backgroundColor = "transparent";
*/
    
        OpenLayers.Event.observe(this.div, "mouseup", 
            OpenLayers.Function.bindAsEventListener(this.mouseUp, this));
        OpenLayers.Event.observe(this.div, "click",
                      this.ignoreEvent);
        OpenLayers.Event.observe(this.div, "mousedown",
            OpenLayers.Function.bindAsEventListener(this.mouseDown, this));
        OpenLayers.Event.observe(this.div, "dblclick", this.ignoreEvent);


        // layers list div        
        this.layersDiv = document.createElement("div");
        this.layersDiv.id = "layersDiv";
        this.layersDiv.style.paddingTop = "0px";
        this.layersDiv.style.paddingLeft = "10px";
        this.layersDiv.style.paddingBottom = "5px";
        this.layersDiv.style.paddingRight = "75px";
        //this.layersDiv.style.backgroundColor = this.activeColor;        

        // had to set width/height to get transparency in IE to work.
        // thanks -- http://jszen.blogspot.com/2005/04/ie6-opacity-filter-caveat.html
        //
        /*this.layersDiv.style.width = "100%";
        this.layersDiv.style.height = "100%";*/

				//this.layersDiv.style.width = "600px";
        //this.layersDiv.style.height = "50px";


        this.baseLbl = document.createElement("div");
        this.baseLbl.innerHTML = OpenLayers.i18n("baseLayer");
        this.baseLbl.style.marginTop = "3px";
        this.baseLbl.style.marginLeft = "3px";
        this.baseLbl.style.marginBottom = "3px";
        
        this.baseLayersDiv = document.createElement("div");
        this.baseLayersDiv.style.paddingLeft = "10px";
        /*OpenLayers.Event.observe(this.baseLayersDiv, "click", 
            OpenLayers.Function.bindAsEventListener(this.onLayerClick, this));
        */
                     

        this.dataLbl = document.createElement("div");
				this.dataLbl.id = "dataLbl";
        //this.dataLbl.innerHTML = OpenLayers.i18n("Layers:"); //Data label name
        
        this.dataLayersDiv = document.createElement("div");
				this.dataLayersDiv.id = "dataLayersDiv";


        if (this.ascending) {
            this.layersDiv.appendChild(this.baseLbl);
            this.layersDiv.appendChild(this.baseLayersDiv);
            this.layersDiv.appendChild(this.dataLbl);
            this.layersDiv.appendChild(this.dataLayersDiv);
        } else {
            this.layersDiv.appendChild(this.dataLbl);
            this.layersDiv.appendChild(this.dataLayersDiv);
            this.layersDiv.appendChild(this.baseLbl);
            this.layersDiv.appendChild(this.baseLayersDiv);
        }    
 
        this.div.appendChild(this.layersDiv);

        /*OpenLayers.Rico.Corner.round(this.div, {corners: "tl bl",
                                        bgColor: "transparent",
                                        color: this.activeColor,
                                        blend: false});

        OpenLayers.Rico.Corner.changeOpacity(this.layersDiv, 0.75);
				

        var imgLocation = OpenLayers.Util.getImagesLocation();
        var sz = new OpenLayers.Size(18,18);        

        // maximize button div
        var img = imgLocation + 'layer-switcher-maximize.png';
        this.maximizeDiv = OpenLayers.Util.createAlphaImageDiv(
                                    "OpenLayers_Control_MaximizeDiv", 
                                    null, 
                                    sz, 
                                    img, 
                                    "absolute");
        this.maximizeDiv.style.top = "5px";
        this.maximizeDiv.style.right = "0px";
        this.maximizeDiv.style.left = "";
        this.maximizeDiv.style.display = "none";
        OpenLayers.Event.observe(this.maximizeDiv, "click", 
            OpenLayers.Function.bindAsEventListener(this.maximizeControl, this)
        );
        
        this.div.appendChild(this.maximizeDiv);

        // minimize button div
        img = imgLocation + 'layer-switcher-minimize.png';
        sz = new OpenLayers.Size(18,18);        
        this.minimizeDiv = OpenLayers.Util.createAlphaImageDiv(
                                    "OpenLayers_Control_MinimizeDiv", 
                                    null, 
                                    sz, 
                                    img, 
                                    "absolute");
        this.minimizeDiv.style.top = "5px";
        this.minimizeDiv.style.right = "0px";
        this.minimizeDiv.style.left = "";
        this.minimizeDiv.style.display = "none";
        OpenLayers.Event.observe(this.minimizeDiv, "click", 
            OpenLayers.Function.bindAsEventListener(this.minimizeControl, this)
        );

        this.div.appendChild(this.minimizeDiv);
*/
    },
    
    /** 
     * Method: ignoreEvent
     * 
     * Parameters:
     * evt - {Event} 
     */
    ignoreEvent: function(evt) {
        OpenLayers.Event.stop(evt);
    },

    /** 
     * Method: mouseDown
     * Register a local 'mouseDown' flag so that we'll know whether or not
     *     to ignore a mouseUp event
     * 
     * Parameters:
     * evt - {Event}
     */
    mouseDown: function(evt) {
        this.isMouseDown = true;
        this.ignoreEvent(evt);
    },

    /** 
     * Method: mouseUp
     * If the 'isMouseDown' flag has been set, that means that the drag was 
     *     started from within the LayerSwitcher control, and thus we can 
     *     ignore the mouseup. Otherwise, let the Event continue.
     *  
     * Parameters:
     * evt - {Event} 
     */
    mouseUp: function(evt) {
        if (this.isMouseDown) {
            this.isMouseDown = false;
            this.ignoreEvent(evt);
        }
    },


    /** 
     * Method: createGroupDiv
     * Creates <div></div> element for group of layers defined by input string.
     * 
     * Parameters:
     * layergroup - {Strin} with group structure as "Parent Group/It's child"
     *  
     * Returns:
     * {DOMElement} <div></div> object for this group of layers
     */
    createGroupDiv: function(layergroup) {
        var groupNames = layergroup.split("/"); // array with layer names
        var groupName = groupNames[groupNames.length-1]; // name of the last group in the line
        //var br = document.createElement("br"); 
        var groupDiv = this.groups.groupDivs[layergroup];
        
        // groupDiv does not exist: create
        if (!groupDiv) {

            // search for the parent div - it can be another group div, or 
            // this dataLayersDiv directly
            var parentDiv = this.groups.groupDivs[groupNames.slice(0,groupNames.length-2).join("/")];

            if (!parentDiv) {

                // dataLayersDiv is parent div
                if (groupNames.length == 1) {
                    parentDiv = this.dataLayersDiv;
                }
                // there is no such thing, like parent div,
                else {
                    parentDiv = this.createGroupDiv( groupNames.slice(0,groupNames.length-1).join("/"));
                }
            }

            // create the div
            groupDiv = document.createElement("div");
            groupDiv.setAttribute('class', 'olLayerGroup');
            //groupDiv.style.marginLeft="10px";
            //groupDiv.style.marginBottom="5px";
            if (!this.groups.display[layergroup]) {
                this.groups.display[layergroup] = "block";
            }
            groupDiv.style.display= this.groups.display[layergroup];
            this.groups.groupDivs[layergroup] = groupDiv;

            // create the label
            var groupLbl = document.createElement("span");
            groupLbl.innerHTML="<u>"+groupName+"</u>"; //<br/>";
            //groupLbl.style.marginTop = "3px";
            //groupLbl.style.marginLeft = "3px";
            //groupLbl.style.marginBottom = "3px";
            groupLbl.style.fontWeight = "bold";

            // setup mouse click event on groupLbl
            OpenLayers.Event.observe(groupLbl, "mouseup", 
                OpenLayers.Function.bindAsEventListener(
                    this.onGroupClick, {layergroup: layergroup, groups:
                    this.groups}));
            
            // create input checkbox
            /*var groupInput = document.createElement("input");
            groupInput.id = "input_" + groupNames.join("_");
            groupInput.name = groupNames.join("_");
            groupInput.type = "checkbox";
            groupInput.value = layergroup;
            groupInput.checked = false;
            groupInput.defaultChecked = false;
            if (!this.groups.checked[layergroup]) {
                this.groups.checked[layergroup] = false;
            }
            groupInput.checked = this.groups.checked[layergroup];
            groupInput.defaultChecked = this.groups.checked[layergroup];
            */
            // create empty array of layers
            if (!this.groups.layers[layergroup]) {
                this.groups.layers[layergroup] = [];
            }
            
            // setup mouse click event on groupInput
            var context = {groupDiv: groupDiv,
                            layerSwitcher: this};
             //               inputElem: groupInput};

/*            OpenLayers.Event.observe(groupInput, "mouseup", 
                OpenLayers.Function.bindAsEventListener(
                    this.onInputGroupClick, context));*/
            
            // append to parent div
            //parentDiv.appendChild(groupInput);
            parentDiv.appendChild(groupLbl);
            parentDiv.appendChild(groupDiv);

        }

        return this.groups.groupDivs[layergroup];
    },

    appendLayerToGroups: function(layer) {
        var groupNames = layer.group.split("/");
        var groupName = null;

        for (var i = 1; i <= groupNames.length; i++) {
            var groupName = groupNames.slice(0,i).join("/");
            if (!this.isInGroup(groupName,layer.id)) {
                this.groups.layers[groupName].push(layer);
            }
        }
    },
    
    isInGroup: function (groupName, id) {
        for (var j = 0; j < this.groups.layers[groupName].length; j++) {
            if (this.groups.layers[groupName][j].id == id) {
                return true;
            }
        }
        return false;
    },
  

    CLASS_NAME: "OpenLayers.Control.customLayerSwitcher"
});
