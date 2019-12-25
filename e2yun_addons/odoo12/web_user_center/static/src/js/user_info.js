odoo.define('web_user_center.user_info', function (require) {
    'use strict';


    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var _t = core._t;

    var $o_footer = $('.o_footer')
    $o_footer.empty()

    $('.openerp o_livechat_button d-print-none').hide()

    $('#qrcode_img').bigic();
    $('#password_qrcode_img').bigic();
    $('.aui-btn-out').on('click', function (ev) {  //退出按钮
        var logouturl = "/web/session/logout?redirect=/web/log"
        if (self != top) {
            top.location.href = logouturl;
        } else {
            window.location.href = logouturl;
        }

    });

    $('.moreset').on('click', function (ev) {
        var url = "/web#id=2&model=res.users&view_type=form&view_id=2065&menu_id=";
        if (self != top) {
            top.location.href = url;
        } else {
            window.location.href = url;
        }

    });


});