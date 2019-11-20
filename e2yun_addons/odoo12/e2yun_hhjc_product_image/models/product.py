#!/usr/bin/python3
from odoo import api, fields, models
import os
import sys
import jinja2
import hashlib

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'html'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.e2yun_hhjc_product_image', "html")

jinja2Env = jinja2.Environment('<%', '%>', '${', '}', '%', loader=loader, autoescape=True)


class ProductImage(models.Model):
    _name = "product.image.ext"
    _order = "order_sort"

    image_path = fields.Char(u'产品图片地址')
    file_name = fields.Char(u'名称')
    file_md5 = fields.Char(u'md5')
    file_size = fields.Char(u'大小')
    is_primary = fields.Boolean(u'是主图')
    order_sort = fields.Integer(u'图片顺序')
    product_tmpl_id = fields.Many2one('product.template', string=u'产品', index=True)

    @api.model
    def create(self, vals):

        if not vals.get('file_md5',False) and vals.get('file_name',False):
            file_md5 = hashlib.md5(vals.get('file_name').encode(encoding='UTF-8')).hexdigest()
            vals['file_md5'] = file_md5
        return super(ProductImage, self).create(vals)
    
    @api.multi
    def write(self,vals):
        if vals.get('file_name',False):
            file_md5 = hashlib.md5(vals.get('file_name').encode(encoding='UTF-8')).hexdigest()
            vals['file_md5'] = file_md5
        return super(ProductImage, self).write(vals)

    # _sql_constraints = [
    #     ('product_template_sort_uniq', 'unique(product_tmpl_id, order_sort)', "图片顺序 已经存在请核对后再进行添加 !"),
    # ]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    images_html = fields.Text(string=u'图片列表', compute='_get_all_images_html')
    product_image_ext_ids = fields.One2many('product.image.ext', 'product_tmpl_id', u'产品图片')

    @api.multi
    def _get_all_images_html(self):
        # product = self[0]
        # template = jinja2Env.get_template('images.html')
        # self.images_html = template.render({'editor_id': product.id})
        for product in self[0]:
            template = jinja2Env.get_template('images.html')
            product.images_html = template.render({'editor_id': product.id})

    @api.model
    def get_primary_url(self):
        url = ''
        for image in self.product_image_ext_ids:
            if image.order_sort == 0 or image.is_primary == True:
                url = image.image_path
        return url
