(function () {
'use strict';
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
        var account_id = href.match(/accept\/([0-9]+)/);
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
        ajax.jsonRpc("/srm_inquiry_account/accept", 'call', {
            'account_id': parseInt(account_id[1]),
            'token': token,
            'signer': signer_name,
            'sign': sign?JSON.stringify(sign[1]):false,
        }).then(function (data) {
            var message_id = (data) ? 3 : 4;
            $('#modelaccept').modal('hide');
            window.location.href = '/srm_inquiry_account/'+account_id[1]+'/'+token+'?message='+message_id;
        });
        return false;
    });


}());
