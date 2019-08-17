from odoo import models, fields, api

class e2yun_supplier_user(models.Model):
    _name = 'e2yun.supplier.user'
    _description = '供应商用户'

    name = fields.Char('名称')
    password = fields.Char('密码')
    confirm_password = fields.Char('确认密码')
