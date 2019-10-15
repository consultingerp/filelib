odoo.define('e2yun_hhjc_js_extends.initial_page', function (require) {
    "use strict";

    // console.log("===========================1111111111111111111111111==================================");


    var FormView = require('web.FormView');

    /**
     * This file is used to add "message_attachment_count" to fieldsInfo so we can fetch its value for the
     * chatter's attachment button without having it explicitly declared in the form view template.
     *
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
