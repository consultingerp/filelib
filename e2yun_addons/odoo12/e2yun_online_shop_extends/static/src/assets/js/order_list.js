function load_order_list(){
    $('.tab-panel-item').innerHTML = '';

    var access_token = $("input[name='csrf_token']").val();
    $.post('/e2yun_online_shop_extends/get_order_list',{
        'access_token' : access_token,
        'csrf_token' : access_token
    },function(datas) {
        var d = JSON.parse(datas);

        for(var i = 0;i < d.length; i++){
            var order = d[i];
            var order_state = order.order_state;

            var order_state_text = order_state;
            if(order_state == 'sent'){
                order_state_text = '待确认';
            }else if (order_state == 'sale'){
                order_state_text = '已确认';
            }else if (order_state == 'done'){
                order_state_text = '已完成';
            }else if (order_state == 'cancel'){
                order_state_text = '已取消';
            }

            var html =
                "           <div class='tab-item'>" +
                "               <a href='javascript:void(0);' class='aui-well-item aui-well-item-clear'>" +
                "                   <div class='aui-well-item-bd'> " +
                "                       <h3>门店:"+order.order_team+"</h3>" +
                "                       <h3>订单编号:"+order.order_name+"</h3>" +
                "                   </div>" +
                "                   <span>"+order_state_text+"</span>" +
                "               </a>" +
                "               <div class='aui-mail-product'>";

            var lines = order['order_line'];
            for(var k = 0;k<lines.length;k++){
                var line = lines[k];
                html = html + "<a href='javascript:;' class='aui-mail-product-item'>" +
                    "       <div class='aui-mail-product-item-hd'>" +
                    "           <img src='"+line.image_url+"' alt=''>" +
                    "       </div>" +
                    "       <div class='aui-mail-product-item-bd'>" +
                    "           <p>"+line.line_name+"</p>" +
                    "           <p>销售数量:"+line.line_qty+"</span><span style='float: right;'>交货数量:"+line.line_delivered_qty+"</span></p>" +
                    "       </div>" +
                    "   </a>";
            }
            html = html + "</div><a href='javascript:;' class='aui-mail-payment'>" +
                "       <p>" +
                "           共<em>"+order.total_num+"</em>" +
                "           件商品 实付款: ￥<i>"+order.order_price+"</i>" +
                "       </p>" +
                "   </a>" +
                "   <div style='padding-left: 20px;'>" +
                "       地址:"+order.order_address+"<br/>"+
                "       联系电话:"+order.order_phone+"<br/>"+
                //"       <a href='javascript:;'>再次购买</a>" +
                //"       <a href='javascript:;' class='aui-df-color'>评价晒单</a>" +
                //"       <a href='javascript:;' class='aui-df-color'>查看发票</a>" +
                "    </div>";


            html = html + "</div>";
            html = html + "<div class='divHeight'></div>";


            $('.all_item').append(html);// = html;//(html);

            if(order_state == 'sent'){
                $('.sent_item').append(html);
            }else if(order_state == 'sale'){
                $('.confirm_item').append(html);
            }
            else if(order_state == 'done'){
                $('.done_item').append(html);
            }else if(order_state == 'cancel'){
                $('.cancel_item').append(html);
            }
        }

    });
}

$(document).ready(function() {

    $.post('/e2yun_online_shop_extends/get_token',{},function(datas) {
        var d = JSON.parse(datas);
        $('body').append("<input name='csrf_token' value="+d['csrf_token']+" type='hidden' />");
        load_order_list();
    });

    $("a[name='btn_back']").click(function(){
        window.location.href = '/hhjc_shop_index';
    });
});

!function(window) {
    "use strict";

    var doc = window.document
      , ydui = {};

    $(window).on('load', function() {
        //load_order_list();

    });

    var util = ydui.util = {

        parseOptions: function(string) {},

        pageScroll: function() {}(),

        localStorage: function() {}(),

        sessionStorage: function() {}(),

        serialize: function(value) {},

        deserialize: function(value) {}
    };

    function storage(ls) {}

    $.fn.emulateTransitionEnd = function(duration) {}
    ;

    if (typeof define === 'function') {
        define(ydui);
    } else {
        window.YDUI = ydui;
    }

}(window);

!function(window) {
    "use strict";

    function Tab(element, options) {
        this.$element = $(element);
        this.options = $.extend({}, Tab.DEFAULTS, options || {});
        this.init();
        this.bindEvent();
        this.transitioning = false;
    }

    Tab.TRANSITION_DURATION = 150;

    Tab.DEFAULTS = {
        nav: '.tab-nav-item',
        panel: '.tab-panel-item',
        activeClass: 'tab-active'
    };

    Tab.prototype.init = function() {
        var _this = this
          , $element = _this.$element;

        _this.$nav = $element.find(_this.options.nav);
        _this.$panel = $element.find(_this.options.panel);
    }
    ;

    Tab.prototype.bindEvent = function() {
        var _this = this;
        _this.$nav.each(function(e) {
            $(this).on('click.ydui.tab', function() {
                _this.open(e);
            });
        });
    }
    ;

    Tab.prototype.open = function(index) {
        var _this = this;

        index = typeof index == 'number' ? index : _this.$nav.filter(index).index();

        var $curNav = _this.$nav.eq(index);

        _this.active($curNav, _this.$nav);

        _this.active(_this.$panel.eq(index), _this.$panel, function() {
            $curNav.trigger({
                type: 'opened.ydui.tab',
                index: index
            });
            _this.transitioning = false;
        });
    }
    ;

    Tab.prototype.active = function($element, $container, callback) {
        var _this = this
          , activeClass = _this.options.activeClass;

        var $avtive = $container.filter('.' + activeClass);

        function next() {
            typeof callback == 'function' && callback();
        }

        $element.one('webkitTransitionEnd', next).emulateTransitionEnd(Tab.TRANSITION_DURATION);

        $avtive.removeClass(activeClass);
        $element.addClass(activeClass);
    }
    ;

    function Plugin(option) {
        var args = Array.prototype.slice.call(arguments, 1);

        return this.each(function() {
            var target = this
              , $this = $(target)
              , tab = $this.data('ydui.tab');

            if (!tab) {
                $this.data('ydui.tab', (tab = new Tab(target,option)));
            }

            if (typeof option == 'string') {
                tab[option] && tab[option].apply(tab, args);
            }
        });
    }

    $(window).on('load.ydui.tab', function() {
        $('[data-ydui-tab]').each(function() {
            var $this = $(this);
            $this.tab(window.YDUI.util.parseOptions($this.data('ydui-tab')));
        });
    });

    $.fn.tab = Plugin;

}(window);

