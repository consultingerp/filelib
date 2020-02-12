# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2001-2014 Zhuhai sunlight software development co.,ltd. All Rights Reserved.
#    Author: Kenny
#    Website: http://zhsunlight.cn
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api

import time

class confirm_msg(models.TransientModel):
    _name = 'confirm.msg'

    confirm_title = fields.Char(string="Confirm Message Title")
    confirm_msg = fields.Char(string="Confirm Message")
    previous_id =fields.Char(string="previous_id")
    previous_type = fields.Char(string="previous_type")
    previous_method = fields.Char(string="previous_method")

    @api.multi
    def do_confirm_action(self):
        view = self.env.ref('srm_confirm_msg.view_confirm_msg')

        return {
            'name': self.confirm_title,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'confirm.msg',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }


    @api.multi
    def do_confirm(self):
        previous = self.env[self.previous_type].search([('id', "=", self.previous_id)])
        method = getattr(previous,self.previous_method)
        res = method()
        return res
