# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import random
from odoo.exceptions import Warning



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

    # 等待二次更新后注释
    user_id_teams = fields.Many2many( 'crm.team', string='担任店长的门店', relation='e2yun_user_id_user_team_rel',
        compute='_compute_user_id_crm_teams', store=True)
    #
    # update_user_id_teams_flag = fields.Char('担任店长的门店更新标识')
    # 等待二次更新后注释ß
    area_manager_teams = fields.Many2many( 'crm.team', string='担任片区长的门店', relation='e2yun_area_manager_user_team_rel',
        compute='_compute_area_manager_crm_teams', store=True)
    #
    # update_area_manager_teams_flag = fields.Char('担任片区长的门店更新标识')

    # 每一个Flag对应的是门店模型中相应字段的更新
    # 如果是附属成员、团队成员的更新，那么有可能更新到
    @api.multi
    @api.depends('update_teams_flag')
    def _compute_crm_teams(self):
        for user in self:
            res = self.env['crm.team']
            teams = self.env['crm.team'].search(
                ['|', '|', '|', ('member_ids', 'in', user.id), ('associate_member_ids', 'in', user.id),
                 ('user_id', '=', user.id), ('area_manager', '=', user.id)])
            for team in teams:
                res += team
            user.teams = res

    def button_add_related_teams(self):
        ctx = self.env.context.copy()
        current_id = self.id
        ctx.update({'current_res_user_id': current_id})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'add.related.teams',
            'context': ctx,
        }


class E2yuAddRelatedTeamModel(models.TransientModel):
    _name = 'add.related.teams'

    teams = fields.Many2many('crm.team', required=True)
    """
    area_manager 片区长
    user_id 店长
    member_ids 团队成员
    associate_member_ids 附属成员
    """
    member_type = fields.Selection([('area_manager', '片区长'), ('user_id', '店长'),
                                    ('member_ids', '团队成员'), ('associate_member_ids', '附属成员')], required=True)

    def add_related_teams(self):
        ctx = self.env.context.copy()
        teams = self.teams
        member_type = self.member_type
        current_user_id = ctx.get('current_res_user_id')
        current_user = self.env['res.users'].browse(current_user_id)
        if member_type == 'area_manager':
            for team in teams:
                team.area_manager = current_user
        elif member_type == 'user_id':
            for team in teams:
                team.user_id = current_user
        elif member_type == 'member_ids':
            if len(teams) > 1:
                raise Warning(_('选择团队成员字段时，请勿选择多个门店'))
            for team in teams:
                member_ids = team.member_ids.ids
                member_ids.append(current_user_id)
                member_ids = list(set(member_ids))
                team.member_ids = member_ids
        elif member_type == 'associate_member_ids':
            for team in teams:
                associate_member_ids = team.associate_member_ids.ids
                associate_member_ids.append(current_user_id)
                associate_member_ids = list(set(associate_member_ids))
                team.associate_member_ids = [(6, 0, associate_member_ids)]
        return 0
    # @api.multi
    # @api.depends('update_user_id_teams_flag')
    # def _compute_user_id_crm_teams(self):
    #     for user in self:
    #         res = self.env['crm.team']
    #         teams = self.env['crm.team'].search([('user_id.id', '=', user.id)])
    #         for team in teams:
    #             res += team
    #         user.user_id_teams = res
    #
    # @api.multi
    # @api.depends('update_area_manager_teams_flag')
    # def _compute_area_manager_crm_teams(self):
    #     for user in self:
    #         res = self.env['crm.team']
    #         teams = self.env['crm.team'].search([('area_manager.id', '=', user.id)])
    #         for team in teams:
    #             res += team
    #         user.area_manager_teams = res


class E2yunCrmTeamExtends(models.Model):
    _inherit = 'crm.team'

    # @api.multi
    # def write(self, values):
    #     res = super(E2yunCrmTeamExtends, self).write(values)
    #     if 'member_ids' in values:
    #         randon_int_str = str(random.randint)
    #         for team in self:
    #             team.member_ids.write({'update_teams_flag': randon_int_str})
    #     if 'associate_member_ids' in values:
    #         randon_int_str = str(random.randint)
    #         for team in self:
    #             team.associate_member_ids.write({'update_teams_flag': randon_int_str})
    #     if 'user_id' in values:
    #         randon_int_str = str(random.randint)
    #         for team in self:
    #             team.user_id.write({'update_teams_flag': randon_int_str})
    #     if 'area_manager' in values:
    #         randon_int_str = str(random.randint)
    #         for team in self:
    #             team.area_manager.write({'update_teams_flag': randon_int_str})
    #     return res

    @api.one
    def write(self, vals):
        # member_ids_before_modify = self.env['res.users']
        # associate_member_ids_before_modify = self.env['res.users']
        # user_id_before_modify = self.env['res.users']
        # area_manager_before_modify = self.env['res.users']
        if 'member_ids' in vals:
            member_ids_before_modify = self.member_ids
        if 'associate_member_ids' in vals:
            associate_member_ids_before_modify = self.associate_member_ids
        if 'user_id' in vals:
            user_id_before_modify = self.user_id
        if 'area_manager' in vals:
            area_manager_before_modify = self.area_manager

        res = super(E2yunCrmTeamExtends, self).write(vals)

        if 'member_ids' in vals:
            randon_int_str = str(random.randint)
            self.member_ids.write({'update_teams_flag': randon_int_str})
            if member_ids_before_modify:
                member_ids_before_modify.write({'update_teams_flag': randon_int_str})
        if 'associate_member_ids' in vals:
            randon_int_str = str(random.randint)
            self.associate_member_ids.write({'update_teams_flag': randon_int_str})
            if associate_member_ids_before_modify:
                associate_member_ids_before_modify.write({'update_teams_flag': randon_int_str})
        if 'user_id' in vals:
            randon_int_str = str(random.randint)
            self.user_id.write({'update_teams_flag': randon_int_str})
            if user_id_before_modify:
                user_id_before_modify.write({'update_teams_flag': randon_int_str})
        if 'area_manager' in vals:
            randon_int_str = str(random.randint)
            self.area_manager.write({'update_teams_flag': randon_int_str})
            if area_manager_before_modify:
                area_manager_before_modify.write({'update_teams_flag': randon_int_str})
        return res

