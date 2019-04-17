odoo.define('supplier_recruitment.supplier_recruitment', function(require) {
"use strict";

var KanbanRecord = require('web_kanban.Record');

KanbanRecord.include({
    on_card_clicked: function() {
        if (this.model === 'supplier.job') {
            this.$('.oe_applications a').first().click();
        } else {
            this._super.apply(this, arguments);
        }
    },
});

});
