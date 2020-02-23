odoo.define('e2yun_agreement_tier_validation.upload_attachment', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var session = require('web.session');
    var field_registry = require('web.field_registry');
    var Widget = require('web.Widget');
    var data = require('web.data');

    var _t = core._t;
    var QWeb = core.qweb;

    var TierUploadAttachmentField = AbstractField.extend({
        template: 'tier.upload.attachment',
        events: {
        'change input.o_input_file': '_onAttachmentChange',
        'click .o_attachment_delete': '_onAttachmentDelete',
        'click .o_attachment_download': '_onAttachmentDownload',
        'click .o_attachment_view': '_onAttachmentView',
        'click .o_composer_button_add_attachment': '_onClickAddAttachment',
        },
        start: function () {
            var self = this;
           //self._renderDropdown();
         this._attachmentDataSet = new data.DataSetSearch(this, 'ir.attachment', this.context);
         this.fileuploadID = _.uniqueId('o_chat_fileupload');
         this.set('attachment_ids', []);
         this._$attachmentButton = this.$('.o_composer_button_add_attachment');
         this._$attachmentsList = this.$('.o_composer_attachments_list');
         this._renderAttachments();
         $(window).on(this.fileuploadID, this._onAttachmentLoaded.bind(this));
         this.on('change:attachment_ids', this, this._renderAttachments);

        },
          /**
     * @private
     * @param {jQuery.Event} ev
     */
    _onAttachmentChange: function (ev) {
        var self = this;
        var files = ev.target.files;
        var attachments = this.get('attachment_ids');

        _.each(files, function (file){
            var attachment = _.findWhere(attachments, {name: file.name});
            // if the files already exits, delete the file before upload
            if (attachment){
                self._attachmentDataSet.unlink([attachment.id]);
                attachments = _.without(attachments, attachment);
            }
        });
        this.$('form.o_form_binary_form').submit();
        this._$attachmentButton.prop('disabled', true);
        var uploadAttachments = _.map(files, function (file){
            return {
                id: 0,
                name: file.name,
                filename: file.name,
                url: '',
                upload: true,
                mimetype: '',
            };
        });
        attachments = attachments.concat(uploadAttachments);
        this.set('attachment_ids', attachments);
        ev.target.value = "";
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onAttachmentDelete: function (ev){
        ev.stopPropagation();
        var self = this;
        var attachmentID = $(ev.currentTarget).data('id');
        if (attachmentID) {
            var attachments = [];
            _.each(this.get('attachment_ids'), function (attachment){
                if (attachmentID !== attachment.id) {
                    attachments.push(attachment);
                } else {
                    self._attachmentDataSet.unlink([attachmentID]);
                }
            });
            this.set('attachment_ids', attachments);
            this.$('input.o_input_file').val('');
        }
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onAttachmentDownload: function (ev) {
        ev.stopPropagation();
     },
    _onAttachmentLoaded: function () {
        var attachments = this.get('attachment_ids');
        alert(attachments)
        var files = Array.prototype.slice.call(arguments, 1);
        _.each(files, function (file) {
            if (file.error || !file.id){
                this.do_warn(file.error);
                attachments = _.filter(attachments, function (attachment) {
                    return !attachment.upload;
                });
            } else {
                var attachment = _.findWhere(attachments, { filename: file.filename, upload: true });
                if (attachment) {
                    attachments = _.without(attachments, attachment);
                    attachments.push({
                        id: file.id,
                        name: file.name || file.filename,
                        filename: file.filename,
                        mimetype: file.mimetype,
                        url: session.url('/web/content', { id: file.id, download: true }),
                    });
                }
            }
        }.bind(this));
        this.set('attachment_ids', attachments);
        this._$attachmentButton.prop('disabled', false);
      },
     _onClickAddAttachment: function () {
             this.$('input.o_input_file').click();
             //this.$('input.o_input_file').focus();
        },
     _renderAttachments: function () {
        this._$attachmentsList.html(QWeb.render('mail.composer.Attachments', {
            attachments: this.get('attachment_ids'),
        }));
     },
    });

    field_registry.add('tier_upload_attachment', TierUploadAttachmentField);

    return TierUploadAttachmentField;

    });
