odoo.define('e2yun_business_card.contact.kanban', function (require) {
"use strict";
    var core = require('web.core');
    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var viewRegistry = require('web.view_registry');

    var qweb = core.qweb;

    var ContactKanbanController = KanbanController.extend({
        buttons_template: 'ContactKanbanView.buttons',
        /**
         * Extends the renderButtons function of KanbanView by adding an event listener
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
                        title: _t("Business Card OCR"),
                        name: 'Business Card OCR',
                        type: 'ir.actions.act_window',
                        res_model: 'contact.import.wizard',
                        target: 'new',
                        views: [[false, 'form']],
                    });
                });
            }
        }
    });

    var ContactKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: ContactKanbanController,
        }),
    });

    viewRegistry.add('e2yun_business_card_contact_kanban', ContactKanbanView);
});