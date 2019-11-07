# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing tailsde.
from odoo import models,fields,api,exceptions
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
import suds.client

class model(models.Model):
    _name = 'credit.query.report'
    _description = '信用查询'

    team = fields.Many2one('crm.team','门店',required=True)

    def search_credit(self):

        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncReport?wsdl'  # webservice调用地址
        client = suds.client.Client(url)
        #company_code = self.env['res.company']._company_default_get('credit.query.report').company_code
        result = client.service.queryXY(self.team.company_id.company_code, self.team.shop_code)
        if result[0] == 'E':
            raise exceptions.Warning('查询信用数据异常:' + result)
        else:
            credit_result = self.env['credit.result.report'].sudo()
            credit = credit_result.create({'credit':str(result)})

            return {
                'name': '信用查询',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'credit.result.report',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': credit.id,
            }




class model_result(models.Model):
    _name = 'credit.result.report'
    _description = '信用查询'

    credit = fields.Char('信用')

    def search_credit(self):
        return {
            'name': '信用查询',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'credit.query.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }







