odoo.define('web_user_center.user_center', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var AbstractAction = require('web.AbstractAction');
    var AbstractField = require('web.AbstractField');
    var Widget = require('web.Widget');
    var config = require('web.config');

    var QWeb = core.qweb;


    var UserCenter = AbstractAction.extend({
        template: 'user_center_views',
        init: function (parent, action) {
            this._super(parent, action);
            var options = action.params || {};
            this.params = options;  // NOTE forwarded to embedded client action
        },
        start: function () {
            var self = this;
            //QWeb.add_template("/web_user_center/static/src/xml/user_center_base.xml");
            if (config.device.isMobile) {
                this.isMobile = config.device.isMobile;
            } else {
                this.isMobile = config.device.isMobile;
            }
            // return this._super.apply(this, arguments);
        },
    });
    core.action_registry.add('web_user_center.user_center', UserCenter);
    return UserCenter;

});