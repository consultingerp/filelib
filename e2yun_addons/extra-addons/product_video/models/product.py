# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Product_Video(models.Model):
  """ Model for uploading an Video''"""

  _name='product.video'

  product_id= fields.Many2one(comodel_name='product.product',
                                 string='Product')
  name = fields.Char(string='Attachment Name', required=True)
  attachment_type = fields.Selection([('file','File'),('url','URL')], required=True , string='Attachment Type')
  data_file = fields.Binary(string='Video')
  url = fields.Char(string='URl')
  mine_type = fields.Char(string='Mime Type')
  description = fields.Text(string='Description')


class Product_Template(models.Model):

	_inherit = 'product.template'

	video_ids = fields.One2many(related='product_variant_ids.video_ids',string='Product Videos')


class Product_Product(models.Model):
	_inherit = 'product.product'

	video_ids = fields.One2many(comodel_name='product.video',
                                inverse_name='product_id',
                                string='Product Video')		 