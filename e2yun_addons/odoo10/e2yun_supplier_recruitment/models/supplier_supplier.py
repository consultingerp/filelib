# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Supplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    newly_certified_supplier = fields.Boolean('Newly certified supplier', compute='_compute_newly_certified_supplier',
                                          search='_search_newly_certified_supplier')
    job_id = fields.Many2one('supplier.job', "Supplier Job ID")
    active = fields.Boolean("Active", default=True,
                            help="If the active field is set to false, it will allow you to hide the case without removing it.")

    @api.multi
    def _compute_newly_certified_supplier(self):
        read_group_result = self.env['supplier.applicant'].read_group(
            [('supplier_id', 'in', self.ids), ('job_id.state', '=', 'recruit')],
            ['supplier_id'], ['supplier_id'])
        result = dict((data['supplier_id'], data['supplier_id_count'] > 0) for data in read_group_result)
        for record in self:
            record.newly_certified_supplier = result.get(record.id, False)

    def _search_newly_certified_supplier(self, operator, value):
        applicants = self.env['supplier.applicant'].search([('job_id.state', '=', 'recruit')])
        return [('id', 'in', applicants.ids)]

    @api.multi
    def _broadcast_welcome(self):
        """ Broadcast the welcome message to all users in the supplier company. """
        self.ensure_one()
        IrModelData = self.env['ir.model.data']
        channel_all_suppliers = IrModelData.xmlid_to_object('channel_all_suppliers')
        template_new_supplier = IrModelData.xmlid_to_object('email_template_data_applicant_supplier')
        if template_new_supplier:
            MailTemplate = self.env['mail.template']
            body_html = MailTemplate.render_template(template_new_supplier.body_html, 'product.supplierinfo', self.id)
            subject = MailTemplate.render_template(template_new_supplier.subject, 'product.supplierinfo', self.id)
            channel_all_suppliers.message_post(
                body=body_html, subject=subject,
                subtype='mail.mt_comment')
        return True
