# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class CrmTeamADDinformation(models.Model):
    _inherit = ['crm.team']

    shop_type = fields.Char('门店类别')
    shop_code = fields.Char('门店编码')
    sales_organization = fields.Char('销售组织')
    sales_organization_name = fields.Char('销售组织名称')
    sales_channel = fields.Char('分销渠道名称')
    sales_office = fields.Char('销售办公室')
    sales_office_description = fields.Char('销售办公室描述')
    address = fields.Char('详细地址')
    tel = fields.Char('联系电话')

    street = fields.Char('地址')
    street2 = fields.Char('地址2')
    zip = fields.Char('邮编', change_default=True)
    city = fields.Char('市')
    state_id = fields.Many2one("res.country.state", string='省', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='国家', ondelete='restrict')

    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as avatar for this contact, limited to 1024x1024px", )
    image_medium = fields.Binary("Medium-sized image", attachment=True,
                                 help="Medium-sized image of this contact. It is automatically " \
                                      "resized as a 128x128px image, with aspect ratio preserved. " \
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
                                help="Small-sized image of this contact. It is automatically " \
                                     "resized as a 64x64px image, with aspect ratio preserved. " \
                                     "Use this field anywhere a small image is required.")

    area_manager = fields.Many2one('res.users', string='片区长')
    associate_member_ids = fields.Many2many('res.users', string='附属成员')

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals, sizes={'image': (1024, None)})
        return super(CrmTeamADDinformation, self).write(vals)



class ResUsers(models.Model):
    _inherit = 'res.users'

    associate_team_ids = fields.Many2many('crm.team', string='附属门店')