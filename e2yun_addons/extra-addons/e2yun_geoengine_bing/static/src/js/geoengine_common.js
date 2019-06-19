odoo.define('e2yun_geoengine_bing.BackgroundLayers', function (require) {
    "use strict";

    var BackgroundLayers = require('base_geoengine.BackgroundLayers');

    BackgroundLayers.include({
        handleCustomLayers: function (layer) {
            var out = this._super.apply(this, arguments);
            if (layer.is_bing) {
                if (layer.bing_imagery_set == undefined ) {
                    layer.bing_imagery_set = 'CanvasLight'
                }
                if (layer.bing_key == undefined ) {
                    layer.bing_key = 'AqY4IFeQhJPHi5FjGBNc7hfgUNcaVf7S_qyyP_dlVCesSJUqI7dBA-gsyoAIUvGu'
                }
                var layer_opt = {
                    title: layer.name,
                    visible: !layer.overlay,
                    type: 'base',
                    source: new ol.source.BingMaps({
                        layer: layer.name,
                        key: layer.bing_key,
                        imagerySet: layer.bing_imagery_set,
                        culture: layer.culture,
                    }),
                };
                out.push(new ol.layer.Tile(layer_opt));
            }
            return out;
        },
    });
});

