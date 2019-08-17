from odoo import models, fields, api
import datetime
import pytz
import logging
from odoo.exceptions import UserError
from odoo.tools.translate import _

class e2yun_supplier_authentication_info(models.Model):
    _name = 'e2yun.supplier.authentication.info'
    _description = '供应商认证信息'

    name = fields.Char('名称')
    code = fields.Char('认证编号')
    image = fields.Binary('证书图片',attachment=True)
    start_date = fields.Date('生效日期')
    end_date = fields.Date('失效日期')
    remark = fields.Text('备注')
    supplier_info_id = fields.Many2one('e2yun.supplier.info','Supplier Info')
    authentication_type = fields.Selection([('ISO9000','ISO9000认证'),('ISO14000','ISO14000认证'),('UL','UL认证'),('CCC','CCC认证'),('FCC','FCC认证')],'认证类型')