odoo.define('srm_stock_delivery', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');
    var _t = core._t;
    var change_lines = [];
    var data = [];
    var dnnum = '';
    var Dialog = require('web.Dialog');

var deliveryMain = Widget.extend({
    template: 'delivery_main',
    init: function(){
        data = [];
        change_lines = [];
        return this._super.apply(this,arguments)
    },
    start: function(){
        var self = this;
        //点击收货按钮
        this.$('.js_drop_down').click(function(){ self.drop_down();});
        //交货单失去焦点
        this.$('.deliverOrder_search').blur(function(){
                self.on_deliveryOrder($(this).val());
            });
        //位置输入
        this.$('.oe_searchbox').blur(function(event){
                self.on_searchbox($(this).val());
            });

        this.$('.js_clear_search').click(function(event){
                $('.oe_searchbox').val('');
                self.load_row();
            });
    },
    load: function(){
        var self = this;
        var loading_done = new $.Deferred();
        return loading_done;
    },
    //点击收货按钮
    drop_down: function(){
        var self = this;
        //提交数据到后台收货过账
            this._rpc({
            model: 'delivery.pack.operation',
            method: 'action_done_from_ui',
            args: [dnnum,change_lines]})
            .then(function(f){
                if(f){
                    Dialog.alert(this, "收货完成");
                    data = [];
                    $(".oe_pick_app_header").html('');
                    dnnum = '';
                    return self.load_row()
                }
            });
    },
    change_qty:function(row_id,row_val){

        var op_id = parseInt(row_id);
        var value = parseFloat(row_val);
        var isExist = false;
        $.each(change_lines,function(key){
            debugger;
            if(op_id == change_lines[key]['id']){
                isExist = true;
                change_lines[key]['qty'] = value;
            }
        })
        if(!isExist){
            change_lines.push({'id':op_id,'qty':value})
        }
    },
    load_row:function(loc){
        var self = this;
        $("tbody").html("");
        change_lines = [];
        for(var i=0; i<data.length;i++){
            var row = data[i];
            if(loc && row.location_dest_name.indexOf(loc) < 0){
                continue;
            }

            $("tbody").append('<tr class="js_pack_op_line" row_id="'+row.id+'">' +
            '<td>'+row.matnr_name+'</td>' +
            '<td class="brctbl-col3 text-center">'+row.ponum+'</td>' +
            '<td class="brctbl-col3 text-center">'+row.poitem+'</td>' +
            '<td class="brctbl-col2 text-center js_row_qty">' +
            '   <div class="input-group">' +
            '       <form class="js_submit_value">' +
            '           <input type="text" class="form-control text-center js_qty" value="'+row.qty+'"/>' +
            '       </form>' +
            '   </div>' +
            '</td>' +
            '<td class="brctbl-col3 text-center">'+row.qty+ row.product_uom_name+'</td>' +
            '<td class="brctbl-col5 js_loc">' +row.location_name+'</td>' +
            '<td class="brctbl-col5 js_loc">' +row.location_dest_name+'</td>' +
            '</tr>' );
            change_lines.push({'id':row.id,'qty':row.qty});
        }
        // var row = {
        //     'id': 1,
        //     'product':'107000068',
        //     'ponum':'1000298',
        //     'poitem':'0010',
        //     'rem':10,
        //     'qty':10,
        //     'uom':'PC',
        //     'loc_name':'Supplier',
        //     'dest_name':'1000'
        // }
        //
        // $("tbody").append('<tr class="js_pack_op_line" row_id="'+row.id+'">' +
        //     '<td>'+row.product+'</td>' +
        //     '<td class="brctbl-col3 text-center">'+row.ponum+'</td>' +
        //     '<td class="brctbl-col3 text-center">'+row.poitem+'</td>' +
        //     '<td class="brctbl-col2 text-center js_row_qty">' +
        //     '   <div class="input-group">' +
        //     '       <form class="js_submit_value">' +
        //     '           <input type="text" class="form-control text-center js_qty" value="'+row.qty+'"/>' +
        //     '       </form>' +
        //     '   </div>' +
        //     '</td>' +
        //     '<td class="brctbl-col3 text-center">'+row.qty+ row.uom+'</td>' +
        //     '<td class="brctbl-col5 js_loc">' +row.loc_name+'</td>' +
        //     '<td class="brctbl-col5 js_loc">' +row.dest_name+'</td>' +
        //     '</tr>' );

        this.$('.js_qty').bind('blur',function(){
                var row_id = $(this).parent().parent().parent().parent().attr('row_id');
                var row_val = $(this).val();
                self.change_qty(row_id,row_val);
            });
    },
    on_deliveryOrder:function (query) {
        var self = this;
        if (query !== '') {
            $('.deliverOrder_search').val('');
            //查询行数据，加载行
            this._rpc({
            model: 'delivery.pack.operation',
            method: 'readDelivery',
            args: [query]})
            .then(function(d){
                if(d){
                    data = d;
                    dnnum = query;
                    $(".oe_pick_app_header").html(query)
                }else{
                    data = [];
                    $(".oe_pick_app_header").html('');
                    dnnum = ''
                }
                return self.load_row()
            });
        }
    },
    on_searchbox: function(query){
        var self = this;
        self.load_row(query)
    },
    on_attach_callback: function () {

    },
    canBeRemoved: function () {
        return $.when();
    },
    on_detach_callback: function () {}

});

core.action_registry.add('deliveryMain', deliveryMain);

return deliveryMain;

});