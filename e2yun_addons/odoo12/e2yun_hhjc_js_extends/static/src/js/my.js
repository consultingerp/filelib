odoo.define('e2yun_hhjc_js_extends.initial_page', function (require) {
    "use strict";

    // console.log("===========================1111111111111111111111111==================================");

    var FormView = require('web.FormView');

    /**
     * 功能提供了如果是input控件，在初始化form的时候，绑定一个focus事件，能够当获取焦点的时候，就进行全部选中，
     * 不需要在一个字符一个字符的删除
     */

    FormView.include({
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);

            // console.log("===========================22222222222222222222222222=========================");
            setInterval(function () {
                $("input").unbind('focus').bind('focus', function () {
                    $(this).select()
                })
            }, 1000);

        },
    });
});
