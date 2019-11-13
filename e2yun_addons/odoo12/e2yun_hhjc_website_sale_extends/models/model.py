# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api,exceptions
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class ProductPublicCategory(models.Model):
    _name = 'product.public.category'
    _inherit = 'product.public.category'


    def _compute_sz_show(self):
        for s in self:
            sz_show = False
            if s.parent_id:
                company_id = self.env['res.company'].search([('company_code','=','2000')]).id
                product = self.env['product.template']

                products = product.search([('public_categ_ids','in',s.id)])
                if products:
                    for p in products:
                        for pc in p.pc_show_id:
                            if pc.company_id.id == company_id and pc.show_ok:
                                sz_show = True
                                break
                        if sz_show:
                            break
            else:
                categs = self.search([('parent_id','=',s.id)])
                for c in categs:
                    if c.sz_show == True:
                        sz_show = True
                        break
            s.sz_show = sz_show

    def _compute_bj_show(self):

        for s in self:
            bj_show = False
            if s.parent_id:
                company_id = self.env['res.company'].search([('company_code','=','1000')]).id
                product = self.env['product.template']

                products = product.search([('public_categ_ids','in',s.id)])
                if products:
                    for p in products:
                        for pc in p.pc_show_id:
                            if pc.company_id.id == company_id and pc.show_ok:
                                bj_show = True
                                break
                        if bj_show:
                            break
            else:
                categs = self.search([('parent_id','=',s.id)])
                for c in categs:
                    if c.bj_show == True:
                        bj_show = True
                        break
            s.bj_show = bj_show

    code = fields.Char('代码')
    sz_show = fields.Boolean('深圳公司显示',compute=_compute_sz_show)
    bj_show = fields.Boolean('北京公司显示',compute=_compute_bj_show)


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        if vals.get('pos_public_categ_ids', False):
            public_categ_ids = [(6, 0, [vals.get('pos_public_categ_ids')])]
            vals['public_categ_ids'] = public_categ_ids
            del vals['pos_public_categ_ids']
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('pos_public_categ_ids', False):
            public_categ_ids = [(6, 0, [vals.get('pos_public_categ_ids')])]
            vals['public_categ_ids'] = public_categ_ids
            del vals['pos_public_categ_ids']
        return super(ProductTemplate, self).write(vals)
