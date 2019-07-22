odoo.define('wx_tools.team.tree', function (require) {
    "use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    var qweb = core.qweb;

    var ContactListController = ListController.extend({
        buttons_template: 'CrmTeamListView.buttons',
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
                this.$buttons.on('click', '.o_list_tender_button_location', function () {
                    var state = self.model.get(self.handle, {raw: true});
                    self._rpc({
                        model: 'crm.team',
                        method: 'convertteamaddres',
                        args: [self.res_id]
                    }).then(function (result) {

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

    viewRegistry.add('wx_tools_team_tree', ContactListView);
});