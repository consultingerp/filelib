# -*- coding: utf-8 -*-

from odoo import models, fields, api
import random


class E2yunCsutomerExtends(models.Model):
    _inherit = 'res.partner'

    teams = fields.Many2many(
        'crm.team', string='Partner Team id', relation='e2yun_partner_team_rel',
        compute='_compute_crm_teams', store=True)

    @api.multi
    @api.depends('user_id', 'related_guide')
    def _compute_crm_teams(self):
        for partner in self:
            res = self.env['crm.team']
            # user_id为销售员字段，related_guide为相关导购字段
            teams = self.env['crm.team'].search(
                ['|', ('member_ids', 'in', partner.user_id.id), ('member_ids', 'in', partner.related_guide.ids)])
            for team in teams:
                res += team
            partner.teams = res


class E2yunUserExtends(models.Model):
    _inherit = 'res.users'

    teams = fields.Many2many(
        'crm.team', string='Partner Team id', relation='e2yun_user_team_rel',
        compute='_compute_crm_teams', store=True)

    update_teams_flag = fields.Char('更新团队标识')

    user_id_teams = fields.Many2many( 'crm.team', string='担任店长的门店', relation='e2yun_user_id_user_team_rel',
        compute='_compute_user_id_crm_teams', store=True)

    update_user_id_teams_flag = fields.Char('担任店长的门店更新标识')

    area_manager_teams = fields.Many2many( 'crm.team', string='担任片区长的门店', relation='e2yun_area_manager_user_team_rel',
        compute='_compute_area_manager_crm_teams', store=True)

    update_area_manager_teams_flag = fields.Char('担任片区长的门店更新标识')

    @api.multi
    @api.depends('update_teams_flag')
    def _compute_crm_teams(self):
        for user in self:
            res = self.env['crm.team']
            teams = self.env['crm.team'].search(
                ['|', ('member_ids', 'in', user.id), ('associate_member_ids', 'in', user.id)])
            for team in teams:
                res += team
            user.teams = res

    @api.multi
    @api.depends('update_user_id_teams_flag')
    def _compute_user_id_crm_teams(self):
        for user in self:
            res = self.env['crm.team']
            teams = self.env['crm.team'].search([('user_id.id', '=', user.id)])
            for team in teams:
                res += team
            user.user_id_teams = res

    @api.multi
    @api.depends('update_area_manager_teams_flag')
    def _compute_area_manager_crm_teams(self):
        for user in self:
            res = self.env['crm.team']
            teams = self.env['crm.team'].search([('area_manager.id', '=', user.id)])
            for team in teams:
                res += team
            user.area_manager_teams = res

class E2yunCrmTeamExtends(models.Model):
    _inherit = 'crm.team'

    @api.multi
    def write(self, values):
        res = super(E2yunCrmTeamExtends, self).write(values)
        if 'member_ids' in values:
            randon_int_str = str(random.randint)
            for team in self:
                team.member_ids.write({'update_teams_flag': randon_int_str})
        if 'associate_member_ids' in values:
            randon_int_str = str(random.randint)
            for team in self:
                team.associate_member_ids.write({'update_teams_flag': randon_int_str})
        if 'user_id' in values:
            randon_int_str = str(random.randint)
            for team in self:
                team.user_id.write({'update_user_id_teams_flag': randon_int_str})
        if 'area_manger' in values:
            randon_int_str = str(random.randint)
            for team in self:
                team.area_manger.write({'update_area_manger_flag': randon_int_str})
        return res
