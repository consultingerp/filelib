odoo.define('website_mailmessagefile.thread', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    //var data = require('web.data');

    var qweb = core.qweb;
    var _t = core._t;

    var PortalChatter = require('portal.chatter').PortalChatter;

    /**
     * Extends Frontend Chatter to handle rating
     */
    PortalChatter.include({
        events: _.extend({}, PortalChatter.prototype.events, {
            'change input.o_input_file': '_onAttachmentChange',
            'click .o_composer_button_add_attachment': '_onClickAddAttachment',
        }),

        init: function (parent, options) {
            this._super.apply(this, arguments);
        },
        willStart: function () {
            var self = this;
            return $.when(this._super.apply(this, arguments));
        },
        start: function () {
            var self = this;
            this._$attachmentButton = this.$('.o_composer_button_add_attachment');
            return this._super.apply(this, arguments);
        },


        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        _loadTemplates: function () {
            return $.when(this._super(), ajax.loadXML('/website_mailmessagefile/static/src/xml/portal_chatter_messagefiles.xml', qweb));
        },

        _onClickAddAttachment: function () {
            this.$('input.o_input_file').click();
            this.$input.focus();
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {jQuery.Event} ev
         */
        _onAttachmentChange: function (ev) {
            var self = this;
            var files = ev.target.files;
            var attachments = this.get('attachment_ids');
        },


    });
});
