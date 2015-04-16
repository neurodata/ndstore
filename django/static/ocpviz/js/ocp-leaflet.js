// for smooth scrolling through z-indices 
L.TileLayer.SmoothReload = L.TileLayer.extend({

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
        console.log('unloading tiles');
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
});


L.tileLayer.SmoothReload = function (url, options) {
    return new L.TileLayer.SmoothReload(url, options);
};


