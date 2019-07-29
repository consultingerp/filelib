odoo.define('wx_tools.nearby_stores', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var AbstractAction = require('web.AbstractAction');
    var AbstractField = require('web.AbstractField');
    var Widget = require('web.Widget');
    var config = require('web.config');

    var QWeb = core.qweb;


    var nearby_stores = AbstractAction.extend({
        template: 'nearby_stores',
        init: function (parent, action) {
            this._super(parent, action);
            var options = action.params || {};
            this.params = options;  // NOTE forwarded to embedded client action
        }, nearby_stores_templates: function (locations, isLocation) {
            var self = this;
            self._rpc({
                route: 'amap/nearby_stores',
                params: {location: locations},
            }).then(function (result) {
                var html = QWeb.render('store_list', {
                    stores: result.crm_team_list,
                    isLocation: isLocation
                });
                self.$('#aui-store-head').empty();
                self.$('#aui-store-head').append(html)

                var headhtml = QWeb.render('store_head', {name: 'store_head'});
                self.$('#aui-navBar-store').empty();
                self.$('#aui-navBar-store').append(headhtml)

            });

        },
        start: function () {
            var self = this;


            //this.$el.append(headhtml);
            var iswxstore = false;
            if (config.device.isMobile) {
                this.isMobile = config.device.isMobile;
            } else {
                this.isMobile = config.device.isMobile;
                self.nearby_stores_templates('116.38,39.90', false)
            }
            wx.getLocation({
                type: 'wgs84', // 默认为wgs84的gps坐标，如果要返回直接给openLocation用的火星坐标，可传入'gcj02'
                success: function (res) {
                    iswxstore = true;
                    var latitude = res.latitude; // 纬度，浮点数，范围为90 ~ -90
                    var longitude = res.longitude; // 经度，浮点数，范围为180 ~ -180。
                    var speed = res.speed; // 速度，以米/每秒计
                    var accuracy = res.accuracy; // 位置精度
                    var locations = res.longitude + "," + res.latitude; //微信位置
                    self.nearby_stores_templates(locations, this.isMobile)
                }, fail: function () {
                    self.nearby_stores_templates('116.38,39.90', false)
                }
            }); // end getLocation
        },
        events: {
            'click p': '_onClick',
            'click h2': '_onClick',
            'click .aui-store-addressgo': '_onClick',
            'click #locationbejing': '_stores_list',
            'click #locationsz': '_stores_list',
            'click #locationother': '_stores_list',
        }, _onClick: function (ev) {
            var self = this;
            var latitude = $(ev.currentTarget).attr('data-latitude')
            var longitude = $(ev.currentTarget).attr('data-longitude')
            var street = $(ev.currentTarget).attr('data-street')
            wx.openLocation({
                latitude: Number(latitude), // 纬度，浮点数，范围为90 ~ -90
                longitude: Number(longitude), // 经度，浮点数，范围为180 ~ -180。
                name: name, // 位置名
                address: street, // 地址详情说明
                scale: 14, // 地图缩放级别,整形值,范围从1~28。默认为最大
                infoUrl: street  // 在查看位置界面底部显示的超链接,可点击跳转
            });
        }, _stores_list(ev) {
            var self = this;
            var name = $(ev.currentTarget).attr('data-addresname')
            self._rpc({
                route: 'amap/stores_list',
                params: {name: name,
                },
            }).then(function (result) {
                var html = QWeb.render('store_list', {
                    stores: result.crm_team_list,
                    isLocation: false
                });
                self.$('#aui-store-head').empty();
                self.$('#aui-store-head').append(html)

            });
        }
    });
    core.action_registry.add('wx_tools.nearby_stores', nearby_stores);
    return nearby_stores;

});