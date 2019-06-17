odoo.define('e2yun_geoengine_map.BackgroundLayers', function (require) {
    "use strict";

    var BackgroundLayers = require('base_geoengine.BackgroundLayers');

    BackgroundLayers.include({
        handleCustomLayers: function (layer) {
            var out = this._super.apply(this, arguments);
            // 自定义分辨率和瓦片坐标系
            var resolutions=[];
            var maxZoom = 18;
            // 计算百度使用的分辨率
            for (var i=0; i<= maxZoom ; i++) {
                resolutions[i] = Math.pow(2, maxZoom - i);
            }
            var tileGrid = new ol.tilegrid.TileGrid({
                origin:[0, 0],
                resolutions: resolutions
            });
            // 创建百度行政区划
            var baiduSource = new ol.source.TileImage({
                projection: "EPSG:4326",
                tileGrid: tileGrid,
                tileUrlFunction: function(tileCoord, pixelRatio, proj) {
                    if (!tileCoord) {
                        return "";
                    }
                    var z = tileCoord[0];
                    var x = tileCoord[1];
                    var y = tileCoord[2];
                    // 百度瓦片服务url将负数使用M前缀来标识

                    if(x < 0) {
                        x = 'M'+ (-x);
                    }
                    if(y < 0) {
                        y = 'M'+ (-y);
                    }
                    return 'http://online'+ parseInt(Math.random() * 10) +
                        '.map.bdimg.com/tile/?qt=tile&x=' + x + '&y=' + y +'&z='
                        + z + '&styles=pl&scaler=2&udt=20190503';
                }
            });
            // 百度影像
            var baiduSourceRaster = new ol.source.TileImage({
                tileGrid: tileGrid,
                tileUrlFunction: function(tileCoord, pixelRatio, proj) {
                    var z = tileCoord[0];
                    var x = tileCoord[1];
                    var y = tileCoord[2];

                    // 百度瓦片服务url将负数使用M前缀来标识
                    if (x < 0) {
                        x = 'M' + (-x);
                    }
                    if (y < 0) {
                        y = 'M' + (-y);
                    }
                   return 'http://shangetu' + parseInt(Math.random() * 10) + '.map.bdimg.com/it/u=x=' + x +
                        ';y=' + y + ';z=' + z + ';v=009;type=sate&fm=46&udt=20170606';
                }
            });
            // 百度标注
            var baiduSourceLabel = new ol.source.TileImage({
                tileGrid: tileGrid,
                tileUrlFunction: function(tileCoord, pixelRatio, proj) {
                    var z = tileCoord[0];
                    var x = tileCoord[1];
                    var y = tileCoord[2];

                    // 百度瓦片服务url将负数使用M前缀来标识
                    if (x < 0) {
                        x = 'M' + (-x);
                    }
                    if (y < 0) {
                        y = 'M' + (-y);
                    }
                    return 'http://online' + parseInt(Math.random() * 10) + '.map.bdimg.com/onlinelabel/?qt=tile&x=' +
                        x + '&y=' + y + '&z=' + z + '&styles=sl&udt=20170620&scaler=1&p=1';
                }
            });

            var mapUrl = {
                /****
                 * 高德地图
                 * lang可以通过zh_cn设置中文，en设置英文，size基本无作用，scl设置标注还是底图，scl=1代表注记，
                 * scl=2代表底图（矢量或者影像），style设置影像和路网，style=6为影像图，
                 * vec——街道底图
                 * img——影像底图
                 * roadLabel---路网+标注
                 */
                "aMap-img": "http://webst0{1-4}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
                "aMap-vec": "http://webrd0{1-4}.is.autonavi.com/appmaptile?size=1&scale=1&style=8&x={x}&y={y}&z={z}",
                "aMap-roadLabel": "http://webst0{1-4}.is.autonavi.com/appmaptile?style=8&x={x}&y={y}&z={z}",

                /***
                 * 天地图 要key的
                 * vec——街道底图
                 * img——影像底图
                 * ter——地形底图
                 * cva——中文注记
                 * cta/cia——道路+中文注记 ---roadLabel
                 */
                "tian-img": "http://t{0-7}.tianditu.gov.cn/DataServer?T=img_w&x={x}&y={y}&l={z}&tk=你的密钥",
                "tian-roadLabel": "http://t{0-7}.tianditu.gov.cn/DataServer?T=cta_w&x={x}&y={y}&l={z}&tk=你的密钥",
                "tian-label": "http://t{0-7}.tianditu.gov.cn/DataServer?T=cva_w&x={x}&y={y}&l={z}&tk=你的密钥",
                "tian-vec": "http://t{0-7}.tianditu.gov.cn/DataServer?T=vec_w&x={x}&y={y}&l={z}&tk=你的密钥",
                "tian-ter": "http://t{0-7}.tianditu.gov.cn/DataServer?T=ter_w&x={x}&y={y}&l={z}&tk=你的密钥",

                /***
                 *geoq地图
                 * http://cache1.arcgisonline.cn
                 * http://map.geoq.cn
                 * vec：标准彩色地图
                 * gray、blue、warm
                 * line 中国轮廓图
                 * china 中国轮廓图+标注
                 * Hydro 水系
                 * green 植被
                 */
                "geoq-vec": "http://cache1.arcgisonline.cn/arcgis/rest/services/ChinaOnlineCommunity/MapServer/tile/{z}/{y}/{x}",
                "geoq-gray": "http://cache1.arcgisonline.cn/arcgis/rest/services/ChinaOnlineStreetGray/MapServer/tile/{z}/{y}/{x}",
                "geoq-blue": "http://cache1.arcgisonline.cn/arcgis/rest/services/ChinaOnlineStreetPurplishBlue/MapServer/tile/{z}/{y}/{x}",
                "geoq-warm": "http://cache1.arcgisonline.cn/arcgis/rest/services/ChinaOnlineStreetWarm/MapServer/tile/{z}/{y}/{x}",
                "geoq-line": "http://cache1.arcgisonline.cn/arcgis/rest/services/SimpleFeature/ChinaBoundaryLine/MapServer/tile/{z}/{y}/{x}",//不稳定
                "geoq-china": "http://thematic.geoq.cn/arcgis/rest/services/ThematicMaps/administrative_division_boundaryandlabel/MapServer/tile/{z}/{y}/{x}",//不稳定
                "geoq-Hydro": "http://thematic.geoq.cn/arcgis/rest/services/ThematicMaps/WorldHydroMap/MapServer/tile/{z}/{y}/{x}",//不稳定
                "geoq-green": "http://thematic.geoq.cn/arcgis/rest/services/ThematicMaps/vegetation/MapServer/tile/{z}/{y}/{x}",//不稳定
                /***
                 * Google
                 * m 街道
                 * s 影像
                 */
                "google-vec": "http://www.google.cn/maps/vt?lyrs=m@189&x={x}&y={y}&z={z}",
                "google-img": "http://www.google.cn/maps/vt?lyrs=s@189&x={x}&y={y}&z={z}"

            };

            ol.source.onlineMap = function (options) {
                var options = options ? options : {};

                var attributions;//右下角标识
                var lang; //语言

                if (options.attributions !== undefined) {
                    attributions = option.attributions;
                } else if (options.mapType.indexOf("aMap") != -1) {
                    lang = "&lang=zh_cn";
                    if (options.lang !== undefined){
                        lang = "&lang=" + options.lang ;
                    }
                    attributions = new ol.Attribution({
                        html: '&copy; <a class="ol-attribution-amap" ' + 'href="http://ditu.amap.com/">' + '高德地图</a>'
                    });
                } else if (options.mapType.indexOf("tian") != -1) {
                    attributions = new ol.Attribution({
                        html: '&copy; <a class="ol-attribution-tianmap" ' + 'href="http://www.tianditu.cn/">' + '天地图</a>'
                    });
                } else if (options.mapType.indexOf("geoq") != -1) {
                    attributions = new ol.Attribution({
                        html: '&copy; <a class="ol-attribution-geoqmap" ' + 'href="http://www.geoq.net/basemap.html">' + '智图地图</a>'
                    });
                } else if (options.mapType.indexOf("google_cn") != -1) {
                    lang = "&gl=cn";
                    if (options.lang !== undefined){
                        lang = "&gl=" + options.lang ;
                    }
                    attributions = new ol.Attribution({
                        html: '&copy; <a class="ol-attribution-googlemap" ' + 'href="http://www.google.cn/maps">' + '谷歌地图</a>'
                    });
                }

                var url = mapUrl[options.mapType];

                if (options.lang !== undefined) {
                    url = url + lang;
                }


                ol.source.XYZ.call(this, {
                    crossOrigin: 'anonymous',   //跨域
                    cacheSize: options.cacheSize,
                    projection: ol.proj.get('EPSG:3857'),
                    url: url,
                    attributions: attributions,
                    wrapX: options.wrapX !== undefined ? options.wrapX : true
                });
            };
            ol.inherits(ol.source.onlineMap, ol.source.XYZ);//必需

            if (layer.raster_type == 'bing') {
                if (layer.bing_imagery_set == undefined ) {
                    layer.bing_imagery_set = 'CanvasLight'
                }
                if (layer.bing_key == undefined ) {
                    layer.bing_key = 'AqY4IFeQhJPHi5FjGBNc7hfgUNcaVf7S_qyyP_dlVCesSJUqI7dBA-gsyoAIUvGu'
                }
                var lang='zh-cn';
                if (layer.culture != 'zh_CN') {
                    lang = 'en-us';
                }
                var layer_opt = {
                    title: layer.name,
                    visible: !layer.overlay,
                    type: 'base',
                    source: new ol.source.BingMaps({
                        layer: layer.name,
                        key: layer.bing_key,
                        imagerySet: layer.bing_imagery_set,
                        culture: lang,
                    }),
                };
                out.push(new ol.layer.Tile(layer_opt));
            }
            if (layer.raster_type == 'baidu') {
                if (layer.baidu_imagery_set == undefined ) {
                    layer.baidu_imagery_set = 'baidu-sourcelabel'
                }
                var baidusource = baiduSource;
                if (layer.baidu_imagery_set == 'baidu-sourcelabel'){
                    baidusource = baiduSourceLabel;
                }
                if (layer.baidu_imagery_set == 'baidu-sourceraster'){
                    baidusource = baiduSourceRaster;
                }
                var layer_opt = {
                    title: layer.name,
                    visible: !layer.overlay,
                    type: 'base',
                    source: baidusource,
                };
                out.push(new ol.layer.Tile(layer_opt));
            }
            if (layer.raster_type == 'amap') {
                var lang='zh_cn';
                if (layer.culture != 'zh_CN') {
                    lang = 'en';
                }
                if (layer.amap_imagery_set == undefined ) {
                    layer.amap_imagery_set = 'aMap-roadLabel'
                }
                var layer_opt = {
                    title: layer.name,
                    visible: layer.overlay,
                    type: 'base',
                    source: new ol.source.onlineMap({mapType: layer.amap_imagery_set,lang:lang}),
                };
                out.push(new ol.layer.Tile(layer_opt));
            }
            if (layer.raster_type == 'google_cn') {
                var lang='cn';
                if (layer.culture != 'zh_CN') {
                    lang = 'en';
                }
                if (layer.google_cn_imagery_set == undefined ) {
                    layer.google_cn_imagery_set = 'google-vec'
                }
                var layer_opt = {
                    title: layer.name,
                    visible: layer.overlay,
                    type: 'base',
                    source: new ol.source.onlineMap({mapType: layer.google_cn_imagery_set,lang:lang}),
                };
                out.push(new ol.layer.Tile(layer_opt));
            }
            return out;
        }
    });
});

