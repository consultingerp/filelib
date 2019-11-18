odoo.define('sales_report_bar', function (require) {
    "use strict";
    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var Widget = require('web.Widget');
    var _t = core._t;

var customer_loss_funnel = AbstractAction.extend({
    template: 'sales_report_bar_template',
    init: function(parent, action){
        this._super(parent, action);
        this.url = action.params.url;
    },
    get_funnel_div_dom:function(){
        var els = this.$el;
        var funnel_div_dom = '';
        for(var i = 0;i<els.length;i++){
            if(els[i]['id'] == 'funnel_div'){
                funnel_div_dom = els[i];
                break;
            }
        }
        return funnel_div_dom;
    },
    start: function(){
        var self = this;
        // var chartdiv = document.createElement('div');
        // chartdiv.style= "width: 600px;height:500px;";
        // chartdiv.id= 'echarts_funnel_div';
        //
        // $('.o_content')[0].appendChild(chartdiv);
        //debugger;


        //查询行数据，加载行
        this._rpc({
        model: 'res.partner',
        method: 'get_customer_loss_data',
        //args: [query]
        })
        .then(function(datas){
            if(datas){
                var funnel_div_dom = self.get_funnel_div_dom();
                var myChart = echarts.init(funnel_div_dom);
                option = {
                    title: {
                        text: '世界人口总量',
                        subtext: '数据来自网络'
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'shadow'
                        }
                    },
                    legend: {
                        data: ['2011年', '2012年']
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    xAxis: {
                        type: 'value',
                        boundaryGap: [0, 0.01]
                    },
                    yAxis: {
                        type: 'category',
                        data: ['巴西','印尼','美国','印度','中国','世界人口(万)']
                    },
                    series: [
                        {
                            name: '2011年',
                            type: 'bar',
                            data: [18203, 23489, 29034, 104970, 131744, 630230]
                        },
                        {
                            name: '2012年',
                            type: 'bar',
                            data: [19325, 23438, 31000, 121594, 134141, 681807]
                        }
                    ]
                };
                myChart.setOption(option);
            }

        });





    },
    destroy: function () {
        // var funnel_div = document.getElementById("echarts_funnel_div");
        // if(funnel_div){
        //     funnel_div.remove();
        // }
    }
});

core.action_registry.add('sales_report_bar', customer_loss_funnel);

// return {
//     customer_loss_funnel: customer_loss_funnel,
// };

});