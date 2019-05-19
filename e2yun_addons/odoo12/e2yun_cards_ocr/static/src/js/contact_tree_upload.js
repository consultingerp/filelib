odoo.define('e2yun_business_card.contact.tree', function (require) {
"use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    var qweb = core.qweb;

    var ContactListController = ListController.extend({
        buttons_template: 'ContactListView.buttons',
        /**
         * Extends the renderButtons function of ListView by adding an event listener
         * on the bill upload button.
         *
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments); // Possibly sets this.$buttons
            if (this.$buttons) {
                var self = this;
                this.$buttons.on('click', '.o_button_upload_contact', function () {
                    var state = self.model.get(self.handle, {raw: true});
                    self.do_action({
                        type: 'ir.actions.act_window',
                        res_model: 'contact.import.wizard',
                        target: 'new',
                        views: [[false, 'form']],
                    });
                });
            }
        }
    });

    var ContactListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ContactListController,
        }),
    });

    viewRegistry.add('e2yun_business_card_contact_tree', ContactListView);
});