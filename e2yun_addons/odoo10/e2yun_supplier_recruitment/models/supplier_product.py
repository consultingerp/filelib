# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SupplierProduct(models.Model):
    _inherit = 'product.template'

    new_applicant_count = fields.Integer(
        compute='_compute_new_applicant_count', string='New Applicant')
    new_certified_supplier = fields.Integer(
        compute='_compute_recruitment_stats', string='New Certified Supplier')
    expected_supplier = fields.Integer(
        compute='_compute_recruitment_stats', string='Expected Supplier')
    manager_id = fields.Many2one('hr.employee', string='Manager', track_visibility='onchange')
    @api.multi
    def _compute_new_applicant_count(self):
        applicant_data = self.env['supplier.applicant'].read_group(
            [('product_id', 'in', self.ids), ('stage_id.sequence', '<=', '1')],
            ['product_id'], ['product_id'])
        result = dict((data['product_id'][0], data['product_id_count']) for data in applicant_data)
        for product in self:
            product.new_applicant_count = result.get(product.id, 0)

    @api.multi
    def _compute_recruitment_stats(self):
        job_data = self.env['supplier.job'].read_group(
            [('product_id', 'in', self.ids)],
            ['no_of_certified_supplier', 'no_of_recruitment', 'product_id'], ['product_id'])
        new_supplier = dict((data['product_id'][0], data['no_of_certified_supplier']) for data in job_data)
        expected_supplier = dict((data['product_id'][0], data['no_of_recruitment']) for data in job_data)
        for product in self:
            product.new_certified_supplier = new_supplier.get(product.id, 0)
            product.certified_supplier = expected_supplier.get(product.id, 0)
