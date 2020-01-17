odoo.define('outbound_report.target_completion_tree_view_button', function (require) {
    "use strict";
    //这些是调⽤需要的模块
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var ListController = require('web.ListController');
    //这块代码是继承ListController在原来的基础上进⾏扩展
    var TargetCompletionListController = ListController.extend({
        renderButtons: function () {
            console.log('进⼊按钮渲染⽅法！');
            this._super.apply(this, arguments);
            if (this.$buttons) {
                //这⾥找到刚才定义的class名为create_by_dept的按钮
                var btn = this.$buttons.find('.create_by_target');
                //给按钮绑定click事件和⽅法create_data_by_dept
                btn.on('click', this.proxy('create_data_by_target'));
            }

        },
        create_data_by_target: function () {
            var self = this;
            console.log('进⼊了按钮绑定的⽅法⾥⾯！');
            // 获取指定视图id,返回指定视图
            this._rpc({
                    model: 'outbound_sync_from_pos.final',
                    method: 'get_view_id',
                    })
            .then(function(query_view_id){
                var view_id = query_view_id;
                return self.do_action({
                                name: '目标完成占比报表查询',
                                type: 'ir.actions.act_window',
                                view_type: 'form',
                                view_mode: 'form',
                                target: 'new',
                //                views: [[2865, 'tree'],[2864, 'graph'],[false, 'form']],
                                views: [[view_id, 'form']],
                                res_model: 'outbound_sync_from_pos.final',
                                context : self.initialState.context
                            });
            });
        },

    });
    //这块代码是继承ListView在原来的基础上进⾏扩展
    //这块⼀般只需要在config中添加上⾃⼰的Model,Renderer,Controller
    //这⾥我就对原来的Controller进⾏了扩展编写，所以就配置了⼀下OutboundListController
    var TargetCompletionListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: TargetCompletionListController,
        }),
    });
    //这⾥⽤来注册编写的视图，第⼀个字符串是注册名到时候需要根据注册名调⽤视图
    viewRegistry.add('target_completion_tree_view_button', TargetCompletionListView);
    return TargetCompletionListView;
});