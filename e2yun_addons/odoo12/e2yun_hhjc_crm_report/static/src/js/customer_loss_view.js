odoo.define('customer_loss_funnel', function (require) {
    "use strict";
    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var Widget = require('web.Widget');
    var _t = core._t;

var customer_loss_funnel = AbstractAction.extend({
    template: 'customer_loss_funnel_template',
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
                var option = {
                    title: {
                        text: '客户流失表',
                        subtext: '漏斗视图'
                    },
                    tooltip: {
                        trigger: 'item',
                        formatter: "{a} <br/>{b} : {c}"
                    },
                    toolbox: {
                        feature: {
                            //dataView: {readOnly: false},
                            //restore: {},
                            saveAsImage: {}
                        }
                    },
                    legend: {
                        data: ['潜在客户','意向客户','准客户','成交客户']
                    },
                    calculable: true,
                    series: [
                        {
                            name:'',
                            type:'funnel',
                            left: '10%',
                            top: 60,
                            //x2: 80,
                            bottom: 60,
                            width: '80%',
                            // height: {totalHeight} - y - y2,
                            min: 0,
                            max: 100,
                            minSize: '10%',
                            maxSize: '90%',
                            sort: 'descending',
                            gap: 10,
                            color:['#e28282','#dadc5e','#61d26f','#5094b5'],
                            // label: {
                            //     show: true,
                            //     position: 'inside'
                            // },
                            labelLine: {
                                length: 80,
                                lineStyle: {
                                    width: 1,
                                    type: 'solid'
                                }
                            },
                            itemStyle: {
                                normal: {
                                    borderColor: '#fff',        //每一块的边框颜色
                                    borderWidth: 0,             //每一块边框的宽度
                                    shadowBlur: 30,             //整个外面的阴影厚度
                                    shadowOffsetX: 0,
                                    shadowOffsetY: 30,          //每一块的x轴的阴影
                                    shadowColor: 'rgba(0, 0, 0, 0.5)'    //阴影颜色
                                }

                                // borderColor: '#fff',
                                // borderWidth: 1
                            },
                            emphasis: {
                                label: {
                                    fontSize: 20
                                }
                            },
                            data: datas
                            //     [
                            //     {value: 60, name: '访问'},
                            //     {value: 40, name: '咨询'},
                            //     {value: 20, name: '订单'},
                            //     {value: 80, name: '点击'},
                            //     {value: 100, name: '展现'}
                            // ]
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

core.action_registry.add('customer_loss_funnel', customer_loss_funnel);

// return {
//     customer_loss_funnel: customer_loss_funnel,
// };

});