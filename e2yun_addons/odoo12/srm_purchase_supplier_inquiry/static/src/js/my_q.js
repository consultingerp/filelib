odoo.define('srm_purchase_supplier_inquiry.srm_purchase_supplier_inquiry', function (require){
    "use strict";

    require('web_editor.ready');

    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var core = require('web.core');
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");

    var qweb = core.qweb;
    $('#sign_clean').on('click', function (e) {
        $("#signature").jSignature('reset');
    });
    var empty_sign = false;
    $("#signature").empty().jSignature({
                'decor-color': '#D1D0CE',
                'color': '#000',
                'background-color': '#fff',
                'height': '142px',
            });

    empty_sign = $("#signature").jSignature("getData",'image');
    $('form.js_accept_json').submit(function(ev){
        ev.preventDefault();
        var $link = $(ev.currentTarget);
        var href = $link.attr("action");
        var order_id = href.match(/accept\/([0-9]+)/);
        var signer_name = $("#name").val();
        var csrf_token= $("#csrf_token").val();
        var sign = $("#signature").jSignature("getData",'image');
        var is_empty = sign?empty_sign[1]==sign[1]:false;
        var token = href.match(/token=(.*)/);
        ajax.jsonRpc('/quote_purchase/accept','call',{
                  'order_id': parseInt(order_id[1]),
                   'token': csrf_token,
                   'signer': signer_name,
                   sign:sign?JSON.stringify(sign[1]):false,
        }).then(function (data) {
             window.location.href = '/quote_purchase/'+order_id[1]
        });

     /*
      ajax.jsonRpc('/test/1', 'call', {
            sign:sign?JSON.stringify(sign[1]):false,
        }).then(function (data) {
            alert(1)
        }); */


        return false
    });




});
