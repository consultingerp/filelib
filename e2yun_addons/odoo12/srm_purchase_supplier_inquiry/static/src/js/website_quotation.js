odoo.define('srm_purchase_supplier_inquiry.srm_purchase_supplier_inquiry', function (require){
    "use strict";

    var ajax = require('web.ajax');
var core = require('web.core');
var Widget = require('web.Widget');
require('web.dom_ready');

    ajax.loadXML('/srm_purchase_supplier_inquiry/views/website_quotation.xml', qweb);

    var supplier_inquiry = Widget.extend({
    template: 'srm.supplier_inquiry',
    events: {
        'click #signature': 'clearSign',
    },
     init: function(parent, options) {
              alert('init')
            this._super.apply(this, arguments);
     },
    start: function () {
        alert('start')
    },
    clearSign: function () {
        alert('clearSign')
     }

});
    var empty_sign = false;
    $('#modelaccept').on('shown.bs.modal', function (e) {
        $("#signature").empty().jSignature({'decor-color' : '#D1D0CE'});
        empty_sign = $("#signature").jSignature("getData",'image');
    });
    $('#sign_clean').on('click', function (e) {
        $("#signature").jSignature('reset');
    });

    $('form.js_accept_json').submit(function(ev){
        ev.preventDefault();
        var $link = $(ev.currentTarget);
        var $confirm_btn = $link.find('button[type="submit"]');
        var href = $link.attr("action");
        var order_id = href.match(/accept\/([0-9]+)/);
        var token = href.match(/token=(.*)/);
        if (token)
            token = token[1];
        var signer_name = $("#name").val();
        var sign = $("#signature").jSignature("getData",'image');
        var is_empty = sign?empty_sign[1]==sign[1]:false;
        $('#signer').toggleClass('has-error', ! signer_name);
        $('#drawsign').toggleClass('panel-danger', is_empty).toggleClass('panel-default', ! is_empty);

        if (is_empty || ! signer_name)
            return false;

        $confirm_btn.prepend('<i class="fa fa-spinner fa-spin"></i> ');
        $confirm_btn.attr('disabled', true);
        openerp.jsonRpc("/quote_purchase/accept", 'call', {
            'order_id': parseInt(order_id[1]),
            'token': token,
            'signer': signer_name,
            'sign': sign?JSON.stringify(sign[1]):false,
        }).then(function (data) {
            var message_id = (data) ? 3 : 4;
            $('#modelaccept').modal('hide');
            window.location.href = '/quote_purchase/'+order_id[1]+'/'+token+'?message='+message_id;
        });
        return false;
    });


}());
