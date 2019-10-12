odoo.define('e2yun_hhjc_crm_report.bicon_list_view_button', function (require) {
    "use strict";
    //这些是调⽤需要的模块
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var ListController = require('web.ListController');
    //这块代码是继承ListController在原来的基础上进⾏扩展
    var BiConListController = ListController.extend({
        renderButtons: function () {
            console.log('进⼊按钮渲染⽅法！');
            this._super.apply(this, arguments);
            if (this.$buttons) {
                //这⾥找到刚才定义的class名为create_by_dept的按钮
                var btn = this.$buttons.find('.create_by_dept');
                //给按钮绑定click事件和⽅法create_data_by_dept
                btn.on('click', this.proxy('create_data_by_dept'));
            }

        },
        create_data_by_dept: function () {
            var self = this;
            console.log('进⼊了按钮绑定的⽅法⾥⾯！');

            return this.do_action({
                name: '',
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                target: 'new',
                views: [[false, 'form']],
                res_model: 'stock.query.condition.report'
            });
        },
    });
    //这块代码是继承ListView在原来的基础上进⾏扩展
    //这块⼀般只需要在config中添加上⾃⼰的Model,Renderer,Controller
    //这⾥我就对原来的Controller进⾏了扩展编写，所以就配置了⼀下BiConListController
    var BiConListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: BiConListController,
        }),
    });
    //这⾥⽤来注册编写的视图BiConListView，第⼀个字符串是注册名到时候需要根据注册名调⽤视图
    viewRegistry.add('bicon_list_view_button', BiConListView);
    return BiConListView;
});