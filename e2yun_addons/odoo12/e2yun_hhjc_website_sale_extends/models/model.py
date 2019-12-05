# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api,exceptions
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import os
import qrcode
from PIL import Image
from odoo.modules.module import get_module_resource
from odoo.addons.wx_tools.controllers import client
import requests

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

    qrcode = fields.Char(u'二维码')
    qrcodeimg = fields.Html(compute='_get_qrcodeimg', string=u'二维码')

    def _get_qrcodeimg(self):
        entry = client.wxenv(self.env)
        if not self.qrcode:
            wx_file_path = get_module_resource('wx_tools', 'static/wx')
            file_name = 'product_category%s.png' % self.id
            url = entry.server_url + "/hhjc_shop_product_list_page/%s" % self.id
            qr = qrcode.QRCode(
                version=5,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=5,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            # 生成图片
            img = qr.make_image(fill_color="#FFFFFF", back_color="#000000")
            qrcodeimg_pic = os.path.join(wx_file_path, file_name)
            with open(qrcodeimg_pic, 'wb') as product_file:
                img.save(product_file)
            self.write({'qrcode': file_name})
            self.qrcodeimg = '<img src=wx_tools/static/wx/%s width="100px" ' \
                             'height="100px" />' % file_name

        else:
            self.qrcodeimg = '<img src=wx_tools/static/wx/%s width="100px" ' \
                             'height="100px" />' % self.qrcode



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
