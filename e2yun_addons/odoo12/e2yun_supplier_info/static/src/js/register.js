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
    $(document).ready(function() {
        $('#supplier_info_state_id').on('change',function(){
            var rpc = require('web.rpc');
            var state_id = $("#supplier_info_state_id").val();
            var blog_id = $("input[name='blog_post_id']").val();
            rpc.query({
                model: 'e2yun.supplier.info',
                method: 'get_citys_by_state',
                args:[{'state_id':state_id}]
            }).then(function(city_ids){
                var select_city_id = $('#supplier_info_city');
                select_city_id.html('')
                if(city_ids && city_ids.length > 0){
                    _.each(city_ids, function (x) {
                        var opt = $('<option>').text(x.name)
                            .attr('value', x.id);
                            select_city_id.append(opt);
                    });
                }else{
                    var opt = $('<option>').text('')
                        .attr('value', '');
                        select_city_id.append(opt);
                }
            });
        })
    })
    $(document).ready(function() {
        $('#supplier_info_bank_country').on('change',function(){
            var rpc = require('web.rpc');
            var bank_country_id = $("#supplier_info_bank_country").val();
            var blog_id = $("input[name='blog_post_id']").val();
            rpc.query({
                model: 'e2yun.supplier.info',
                method: 'get_bank_states_by_country',
                args:[{'bank_country_id':bank_country_id}]
            }).then(function(bank_state_ids){
                var select_bank_state_id = $('#supplier_info_bank_state');
                select_bank_state_id.html('')
                if(bank_state_ids && bank_state_ids.length > 0){
                    _.each(bank_state_ids, function (x) {
                        var opt = $('<option>').text(x.name)
                            .attr('value', x.id);
                            select_bank_state_id.append(opt);
                    });
                }else{
                    var opt = $('<option>').text('')
                        .attr('value', '');
                        select_bank_state_id.append(opt);
                }
            });
        })
    });
    $(document).ready(function() {
        $('#supplier_info_bank_state').on('change',function(){
            var rpc = require('web.rpc');
            var bank_state_id = $("#supplier_info_bank_state").val();
            var blog_id = $("input[name='blog_post_id']").val();
            rpc.query({
                model: 'e2yun.supplier.info',
                method: 'get_bank_citys_by_state',
                args:[{'bank_state_id':bank_state_id}]
            }).then(function(bank_city_ids){
                var select_bank_city_id = $('#supplier_info_bank_city');
                select_bank_city_id.html('')
                if(bank_city_ids && bank_city_ids.length > 0){
                    _.each(bank_city_ids, function (x) {
                        var opt = $('<option>').text(x.name)
                            .attr('value', x.id);
                            select_bank_city_id.append(opt);
                    });
                }else{
                    var opt = $('<option>').text('')
                        .attr('value', '');
                        select_bank_city_id.append(opt);
                }
            });
        })
    });
    // $(document).ready(function() {
    //     $('#supplier_info_bank_city').on('change',function(){
    //         var rpc = require('web.rpc');
    //         var bank_city_id = $("#supplier_info_bank_city").val();
    //         var blog_id = $("input[name='blog_post_id']").val();
    //         rpc.query({
    //             model: 'e2yun.supplier.info',
    //             method: 'get_bank_regions_by_city',
    //             args:[{'bank_city_id':bank_city_id}]
    //         }).then(function(bank_region_ids){
    //             var select_bank_region_id = $('#supplier_info_bank_region');
    //             select_bank_region_id.html('')
    //             if(bank_region_ids && bank_region_ids.length > 0){
    //                 _.each(bank_region_ids, function (x) {
    //                     var opt = $('<option>').text(x.name)
    //                         .attr('value', x.id);
    //                         select_bank_region_id.append(opt);
    //                 });
    //             }else{
    //                 var opt = $('<option>').text('')
    //                     .attr('value', '');
    //                     select_bank_region_id.append(opt);
    //             }
    //         });
    //     })
    // });
});
