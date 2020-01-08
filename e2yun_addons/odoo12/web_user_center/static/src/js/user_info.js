odoo.define('web_user_center.user_info', function (require) {
    'use strict';


    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var _t = core._t;
    $('div.o_footer_copyright').hide();

    $('#qrcode_img').bigic();
    $('#password_qrcode_img').bigic();
    $('#qrcode_img_head_src').bigic();
    $('.aui-btn-out').on('click', function (ev) {  //退出按钮
        var logouturl = "/web/session/logout?redirect=/web/login"
        if (self != top) {
            top.location.href = logouturl;
        } else {
            window.location.href = logouturl;
        }

    });

    $('.moreset').on('click', function (ev) {
        var user_id = $('#user_id').val();
        var url = "/web#id="+user_id+"&model=res.users&view_type=form&view_id=2065&menu_id=";
        if (self != top) {
            top.location.href = url;
        } else {
            window.location.href = url;
        }

    });


    var UserInfoRenderer = Widget.extend({
        className: "o_footer_copyright",

        /**
         * @constructor
         * @param {Object} fields_view
         * @param {Object} fields_view.arch
         * @param {Object} fields_view.fields
         * @param {String} fields_view.model
         */
        init: function (parent, fields_view) {  alert("aaaa");
            this._super.apply(this, arguments);
            // see SearchView init
            fields_view = this._processFieldsView(_.clone(fields_view));
            this.arch = fields_view.arch;
            this.fields = fields_view.fields;
            this.model = fields_view.model;
        },
        /**
         * @override
         */
        start: function () { alert("aaaa");
            this.$el.addClass(this.arch.attrs.class);
            this._render();
            return this._super.apply(this, arguments);
        },
    });


    return UserInfoRenderer;


});