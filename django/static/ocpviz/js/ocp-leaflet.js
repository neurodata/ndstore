// for smooth scrolling through z-indices 
// TODO
// Implement blend mode, fix other modes for safari and fx 
//
L.TileLayer.OCPLayer = L.TileLayer.extend({

	options: {
		minZoom: 0,
		maxZoom: 18,
		tileSize: 256,
		subdomains: 'abc',
		errorTileUrl: '',
		attribution: '',
		zoomOffset: 0,
		opacity: 1,
    /* begin ocpviz added */
    brightness: 100,
    contrast: 100,
    curtime: 0,
    /* end ocpviz added */
		/*
		maxNativeZoom: null,
		zIndex: null,
		tms: false,
		continuousWorld: false,
		noWrap: false,
		zoomReverse: false,
		detectRetina: false,
		reuseTiles: false,
		bounds: false,
		*/
		unloadInvisibleTiles: L.Browser.mobile,
		updateWhenIdle: L.Browser.mobile
	},

  _tileOnLoad: function () {
    var layer = this._layer;

    //Only if we are loading an actual image
    if (this.src !== L.Util.emptyImageUrl) {
      L.DomUtil.addClass(this, 'leaflet-tile-loaded');
      // mark classes by index 
      L.DomUtil.addClass(this, 'index-' + zindex);

      layer.fire('tileload', {
        tile: this,
        url: this.src
      });
    }

    layer._tileLoaded();
  },

  smoothRedraw: function () {
    if (this._map) {
      var old_tiles = this._tiles;
      this._tiles = {};
      this._tilesToLoad = 0;
      this._update();
      this._clearBgBuffer();
      
      function unloadTiles() {
        for (key in old_tiles) {
          this._tileContainer.removeChild(old_tiles[key]);
        }
        old_tiles = {};
      };
      
      this.on('load', function () {
          setTimeout(unloadTiles.bind(this), 300);
      });
    }
    return this;
  },

  _smoothRemoveTile: function(tile) {
    this._tileContainer.removeChild(tile);
  },
	
  setBrightness: function (brightness) {
		this.options.brightness = brightness;

		if (this._map) {
			this._updateBrightness();
		}

		return this;
	},

  _updateBrightness: function () { 
    L.DomUtil.setBrightnessContrast(this._container, this.options.brightness, this.options.contrast);
  },
  
  setContrast: function (contrast) {
		this.options.contrast = contrast;

		if (this._map) {
			this._updateContrast();
		}

		return this;
	},
  
  _updateContrast: function () { 
    L.DomUtil.setBrightnessContrast(this._container, this.options.brightness, this.options.contrast);

  },

  setBlendMode: function (blendmode) {
    if (this._map) {
      L.DomUtil.setBlendMode(this._container, blendmode);
    }
    return this;
  },

});

// add updateBrightness and updateContrast methods
// TODO support for Fx
L.extend(L.DomUtil, {
  setBrightnessContrast: function(el, brightness, contrast) {
    if ('filter' in el.style) {
      el.style.setProperty('-webkit-filter', 'brightness(' + brightness + '%) ' + 'contrast(' + contrast + '%)')
    }
  },
  setBlendMode: function(el, mode) {
    // TODO validate this somehow? 
    console.log(el.style);
    el.style.setProperty('mix-blend-mode', mode);
  },
 
});

L.tileLayer.OCPLayer = function (url, options) {
    return new L.TileLayer.OCPLayer(url, options);
};


