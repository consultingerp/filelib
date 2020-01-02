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


    @api.multi
    def _compute_pos_price(self):
        for s in self:
            pricelist = self.env['product.pricelist'].search([('company_id','=',self.env['res.company']._company_default_get().id),('name','ilike','零售标价表')])
            if pricelist:
                pricelist_item = self.env['product.pricelist.item'].search([('pricelist_id','=',pricelist.id),('product_tmpl_id','=',s.id)])
                if pricelist_item:
                    s.pos_price = pricelist_item.fixed_price


    pos_price = fields.Float('价格',compute=_compute_pos_price)

    @api.multi
    @api.depends('pc_show_id')
    def _compute_company_show(self):
        for s in self:
            for c in s.pc_show_id:
                if c.show_ok and c.company_id.company_code == '1000':
                    s.bj_show = True
                if c.show_ok and c.company_id.company_code == '2000':
                    s.sz_show = True

    sz_show = fields.Boolean(compute=_compute_company_show,store=True)
    bj_show = fields.Boolean(compute=_compute_company_show,store=True)

    @api.model
    def sync_pos_matnr_to_crm(self,matnr,current_date):

        if not current_date:
            current_date = date.today().strftime("%Y-%m-%d")

        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncMatnr?wsdl'  # webservice调用地址
        client = suds.client.Client(url)
        client.service.getMatnr(matnr,current_date)
        return True

    @api.model
    def sync_pos_setmeal_to_crm(self,matnr,current_date):

        if not matnr and not current_date:
            current_date = date.today().strftime("%Y-%m-%d")


        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncMatnr?wsdl'  # webservice调用地址
        client = suds.client.Client(url)
        client.service.getSetmeal(matnr,current_date)
        return True

    @api.model
    def sync_pos_mateproduct_to_crm(self,matnr,current_date):

        if not matnr and not current_date:
            current_date = date.today().strftime("%Y-%m-%d")


        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncMatnr?wsdl'  # webservice调用地址
        client = suds.client.Client(url)
        client.service.getMateproduct(matnr,current_date)
        return True

    @api.model
    def sync_pos_matnrprice_to_crm(self,matnr,current_date):

        if not matnr and not current_date:
            current_date = date.today().strftime("%Y-%m-%d")


        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncMatnr?wsdl'  # webservice调用地址
        client = suds.client.Client(url)
        client.service.getMatnrPrice(matnr,current_date)
        return True
