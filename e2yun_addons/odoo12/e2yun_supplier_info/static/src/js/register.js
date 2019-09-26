odoo.define('e2yun_supplier_info.base_info', function (require) {
"use strict";
    $(document).ready(function() {
        $('#supplier_info_country_id').on('change',function(){
            var rpc = require('web.rpc');
            var country_id = $("#supplier_info_country_id").val();
            var blog_id = $("input[name='blog_post_id']").val();
            rpc.query({
                model: 'e2yun.supplier.info',
                method: 'get_states_by_country',
                args:[{'country_id':country_id}]
            }).then(function(state_ids){
                var select_state_id = $('#supplier_info_state_id');
                select_state_id.html('')
                if(state_ids && state_ids.length > 0){
                    _.each(state_ids, function (x) {
                        var opt = $('<option>').text(x.name)
                            .attr('value', x.id);
                            select_state_id.append(opt);
                    });
                }else{
                    var opt = $('<option>').text('')
                        .attr('value', '');
                        select_state_id.append(opt);
                }
            });
        })
    });

});
