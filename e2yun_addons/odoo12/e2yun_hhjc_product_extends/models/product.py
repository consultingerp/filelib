# -*- coding: utf-8 -*-
import suds

from odoo import models, fields, api
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)


class ProductShowCompany(models.Model):
    _name = 'product.company.show'
    _description = '产品展示公司'

    product_id = fields.Many2one('product.template','产品')
    company_id = fields.Many2one('res.company','公司')
    show_ok = fields.Boolean('展示')

# class Company(models.Model):
#     _inherit = 'res.company'
#     pc_show_id = fields.One2many('product.company.show', 'company_id', '产品展示公司')



class Product(models.Model):
    _inherit = 'product.template'

    layer = fields.Char('产品层次')
    layer_name = fields.Char('产品层次描述')#
    customized = fields.Boolean('定制')
    product_group = fields.Char('产品组')
    mat_group = fields.Char('物料组')
    batch_manager = fields.Char('批次管理')
    so_qty = fields.Float('销售数量')##
    prefer_date = fields.Date('上架时间')
    add_unit = fields.Char('附加单位')##
    groes = fields.Char('大小量纲')
    browse_num = fields.Integer('浏览量')
    pc_show_id = fields.One2many('product.company.show','product_id','产品展示公司')

    @api.model
    def sync_pos_matnr_to_crm(self,matnr,current_date):

        if not current_date:
            current_date = date.today().strftime("%Y-%m-%d")

        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncMatnr?wsdl'  # webservice调用地址
        client = suds.client.Client(url)
        client.service.getMatnr(matnr,current_date)
        return True
