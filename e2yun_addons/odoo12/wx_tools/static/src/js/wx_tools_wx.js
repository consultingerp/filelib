odoo.define('wx_tools.wx_address_location', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var AbstractAction = require('web.AbstractAction');
    var AbstractField = require('web.AbstractField');

    var qweb = core.qweb;

    var Counter = AbstractAction.extend({
        template: 'wx.address_location',
        events: {
            'click input': '_onClick',
        },
        _onClick: function () {
            console.log("hello");
            alert("aaaaa");
        },
    });

    core.action_registry.add('wx_tools.wx_address_location', Counter);
    return Counter;

});