# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2016 e2yun - http://www.e2yun.com
#    All Rights Reserved.
#    info@e2yun.com
############################################################################
#    Coded by: joytao (joytao.zhu@e2yun.com)
############################################################################
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
# import openerp
# from openerp.osv import fields, osv, orm
# from openerp import api
from odoo import fields, models, api


class res_groups(models.Model):
    _inherit = 'res.groups'

    def getlist_model_access(self, menu_ids, context=None):
        if menu_ids:
            query_args = {'menu_ids': tuple(menu_ids)}
            query = """select id from ir_model where model in (
                          select distinct i.relation 
                          from ir_model_fields i where model in (
                            select distinct model 
                            from (
                              select a.id as id ,a.type as type ,b.res_model as model 
                              from ir_actions a  join ir_act_window b on b.id =a.id where b.res_model is not null
                              union all
                              select a.id as id ,a.type as type ,b.model as model 
                              from ir_actions a  join ir_act_report_xml b on b.id =a.id where b.model is not null
                              union all
                              select a.id as id,b.type as type,b.res_model as model 
                              from ir_actions a  join ir_act_client b on b.id =a.id where b.res_model is not null
                            ) h where concat(h.type,',',h.id) in (
                              select distinct action from ir_ui_menu where id in %(menu_ids)s)
                          ) and i.relation <>'' 
                          union all
                          select distinct model 
                          from ( 
                            select a.id as id ,a.type as type ,b.res_model as model 
                            from ir_actions a  join ir_act_window b on b.id =a.id where b.res_model is not null
                            union all
                            select a.id as id ,a.type as type ,b.model as model 
                            from ir_actions a  join ir_act_report_xml b on b.id =a.id where b.model is not null
                            union all
                            select a.id as id,b.type as type,b.res_model as model 
                            from ir_actions a  join ir_act_client b on b.id =a.id where b.res_model is not null
                          ) h1 where concat(h1.type,',',h1.id) in
                            (select distinct action from ir_ui_menu where id in %(menu_ids)s)
                       )"""

            self._cr.execute(query, query_args)

            ids = [r[0] for r in self._cr.fetchall()]

            return ids
        return False

    def getlist_rule_grups(self, menu_ids, context=None):
        if menu_ids:
            query_args = {'menu_ids': tuple(menu_ids)}
            query = """select id from ir_rule where model_id in (
                          select id from ir_model where model in (
                            select distinct i.relation 
                            from ir_model_fields i where model in (
                              select distinct model 
                              from (
                                select a.id as id ,a.type as type ,b.res_model as model 
                                from ir_actions a  join ir_act_window b on b.id =a.id where b.res_model is not null
                                union all
                                select a.id as id ,a.type as type ,b.model as model 
                                from ir_actions a  join ir_act_report_xml b on b.id =a.id where b.model is not null
                                union all
                                select a.id as id,b.type as type,b.res_model as model 
                                from ir_actions a  join ir_act_client b on b.id =a.id where b.res_model is not null
                              ) h where concat(h.type,',',h.id) in (
                                select distinct action from ir_ui_menu where id in %(menu_ids)s)
                            ) and i.relation <>'' 
                            union all
                              select distinct model 
                              from ( 
                                select a.id as id ,a.type as type ,b.res_model as model 
                                from ir_actions a  join ir_act_window b on b.id =a.id where b.res_model is not null
                                union all
                                select a.id as id ,a.type as type ,b.model as model 
                                from ir_actions a  join ir_act_report_xml b on b.id =a.id where b.model is not null
                                union all
                                select a.id as id,b.type as type,b.res_model as model 
                                from ir_actions a  join ir_act_client b on b.id =a.id where b.res_model is not null
                                ) h1 where concat(h1.type,',',h1.id) in
                                  (select distinct action from ir_ui_menu where id in %(menu_ids)s)
                          ) and  global = False and active = True
                       )"""

            self._cr.execute(query, query_args)

            ids = [r[0] for r in self._cr.fetchall()]

            return ids
        return False

    def getimplied_model_access(self, implied_ids, context=None):
        models = []
        for group in self.browse(implied_ids):
            if group.implied_ids != [] or group.implied_ids != False:
                models += group.getimplied_model_access(group.implied_ids.ids)
            for model_access in group.model_access:
                models += [model_access.model_id.id]

        models = list(set(models))
        return models

    def getimplied_rule_groups(self, implied_ids, context=None):
        rule_groups =[]
        for group in self.browse(implied_ids):
            if group.implied_ids != [] or group.implied_ids != False:
                rule_groups += group.getimplied_rule_groups(group.implied_ids.ids)

            rule_groups += group.rule_groups.ids

            rule_groups = list(set(rule_groups))
        return rule_groups

    @api.multi
    def generate_model_access(self):
        for group in self:
            ids = group.menu_access.ids
            model_ids = self.getlist_model_access(group.menu_access.ids)
            models = []
            del_models = []
            for model_id in ids:
                del_models += [(2, model_id)]
            if del_models != []:
                group.model_access = del_models
            implied_model_ids = self.getimplied_model_access(group.implied_ids.ids)
            implied_model_ids = list(set(implied_model_ids))
            if model_ids:
                model_ids = list(set(model_ids))
                model_ids = list(set(model_ids).difference(set(implied_model_ids)))
                for model_id in model_ids:
                    model_name = self.env['ir.model'].browse(model_id).name
                    models += [(0, 0, {
                            'model_id': model_id,
                            'name': model_name+' '+group.name,
                            'perm_create': False,
                            'perm_read': True,
                            'perm_unlink': False,
                            'perm_write': False
                            })]
                if models != []:
                    group.model_access = models

    @api.multi
    def generate_rule_groups(self):
        for group in self:
            ids = group.menu_access.ids
            rule_ids = self.getlist_rule_grups(group.menu_access.ids)
            implied_rule_ids = self.getimplied_rule_groups(group.implied_ids.ids)
            if rule_ids:
                rule_ids = list(set(rule_ids))
                implied_rule_ids = list(set(implied_rule_ids))
                rule_ids = list(set(rule_ids).difference(set(implied_rule_ids)))
                rules = []
                del_rules = []
                for rule_id in ids:
                    del_rules += [(3, rule_id)]
                if del_rules != []:
                    group.rule_groups = del_rules
                for rule_id in rule_ids:
                    rules += [(4, rule_id)]
                group.rule_groups = rules