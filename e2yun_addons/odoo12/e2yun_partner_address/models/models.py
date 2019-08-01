# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions
from datetime import timedelta

from odoo.exceptions import ValidationError, Warning

class E2yunCsutomerExtends(models.Model):
    _inherit = 'res.partner'

    @api.model
    def default_get(self, fields):
        result = super(E2yunCsutomerExtends, self).default_get(fields)
        country = self.env['res.country'].sudo().search([('name','=','中国')])
        if country and len(country) > 0:
            result['country_id'] = country[0].id
        return result


    #country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',default=_default_country)
    city_id = fields.Many2one('res.state.city',string='City',domain="[('state_id','=?',state_id)]")
    area_id = fields.Many2one('res.city.area',string='Area',domain="[('city_id','=?',city_id)]")
    address_desc = fields.Text(string='地址解析')

    def get_add(self,desc,s_idx,e_idx,t_name,postfix):
        d = desc[s_idx:e_idx]
        if d and e_idx <= len(desc):
            s = self.env[t_name].search([('name', '=', d)])
            if s:
                return s.id,e_idx
            else:
                s = self.env[t_name].search([('name', '=', d+postfix)])
                if s:
                    return s.id, e_idx
                else:
                    return self.get_add(desc,s_idx,e_idx+1,t_name,postfix)
        else:
            return 0,0


    @api.onchange('address_desc')
    def analysis_address(self):
        if self.address_desc:

            adds = self.address_desc.split(' ')

            desc = ''
            name = ''
            phone = ''

            if adds and adds[0]:
                desc = adds[0]
            if len(adds) >= 2 and adds[1]:
                name = adds[1]
            if len(adds) >= 3 and adds[2]:
                phone = adds[2]

            if name and name.isdigit() :
                d = desc
                n = name
                p = phone
                name = d
                phone = n
                desc = p

            if desc:

                desc = desc.replace('省','').replace('市','').replace('区','').replace('县','')
                state_id,state_idx = self.get_add(desc,0,2,'res.country.state','省')
                city_id, city_idx = 0,0
                area_id, area_idx = 0,0
                street = ''
                if state_id > 0:
                    self.state_id = state_id
                    city_id, city_idx = self.get_add(desc,state_idx,1+state_idx,'res.state.city','市')
                if city_id > 0:
                    area_id, area_idx = self.get_add(desc,city_idx,1+city_idx,'res.city.area','区')
                    self.city_id = city_id
                    if area_id == 0:
                        area_id, area_idx = self.get_add(desc, city_idx, 1 + city_idx, 'res.city.area', '县')
                if area_id:
                    street = desc[area_idx:len(desc)]
                    self.area_id = area_id
                    self.street = street
            if name:
                self.name = name
            if phone:
                if len(phone) == 11:
                    self.mobile = phone
                else:
                    self.phone = phone