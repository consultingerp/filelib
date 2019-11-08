from odoo import fields, models, api


class GroupDepartments (models.Model):
    _name = 'group.departments'
    _description = '事业部'

    name = fields.Char('事业部')
    factory = fields.Char('工厂', default=1000)


class GroupChannels (models.Model):
    _name = 'group.channels'
    _description = '渠道'

    name = fields.Char('渠道')
