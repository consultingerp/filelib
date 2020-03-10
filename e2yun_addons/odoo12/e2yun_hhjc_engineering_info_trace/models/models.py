# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import re
from odoo.exceptions import ValidationError, Warning


class E2yunHHJCEngineeringInfoTraceChangeProjectTracer(models.TransientModel):
    _name = 'engineering.info.trace.change.project.tracer'
    _description = '工程信息跟踪表改派业务员临时模型'

    project_tracer = fields.Many2one('res.users', string='新业务员', required=True)

    def action_change_project_tracer(self):
        current_lead_id = self._context.get('current_lead_id')
        current_lead = self.env['crm.lead'].browse(current_lead_id)
        if self.project_tracer and current_lead:
            current_lead.project_follower = self.project_tracer
        else:
            raise Warning(_('请选择新的业务员！'))

    def action_change_project_tracer_multi(self):
        new_project_tracer = self.project_tracer.id

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')
        will_change = self.env[active_model].browse(active_ids)

        try:
            for need_change_id in will_change:
                need_change_id.update({'business_tracer': new_project_tracer})
        except Exception as e:
            raise e


class E2yunHHJCEngineeringInfoTrace(models.Model):
    _inherit = 'crm.lead'

    apply_date = fields.Date(string='申请日期', default=lambda self: fields.Date.today(), required=True)
    product_type = fields.Selection([('arrow_sanitary', '箭牌洁具'), ('annwa_sanitary', '安华洁具'),
                                     ('arrow_tile', '箭牌瓷砖'), ('arrow_cabinet', '箭牌橱柜'), ], string='产品类型',
                                    default='arrow_sanitary', required=True)
    integral_plant_report_num = fields.Char('总厂报备号', required=True)
    engineering_project_name = fields.Char('工程项目名称', required=True)
    business_tracer = fields.Many2one('res.users', string='业务跟踪员', required=True, track_visibilty='always')
    project_related_team = fields.Many2one('crm.team', string='门店', required=True)

    first_party_name = fields.Char('甲方名称', required=True)
    first_party_contacter = fields.Char('甲方联系人', required=True)
    first_party_phone = fields.Char('甲方联系电话', required=True)
    second_party_name = fields.Char('乙方名称', required=True)
    second_party_contacter = fields.Char('乙方联系人', required=True)
    second_party_phone = fields.Char('乙方联系电话', required=True)

    date_project_duration_start = fields.Date('建设周期开始日期', required=True)
    date_project_duration_end = fields.Date('建设周期结束日期', required=True)

    project_team = fields.Many2one('crm.team', string='门店', required=True)
    project_follower = fields.Many2one('res.users', string='业务跟踪员', required=True)
    remark = fields.Text('备注')

    project_state = fields.Selection([('new', '新建'), ('allocated', '已分配'), ('processing', '进行中'),
                                      ('finished', '已完成'), ('lost', '已流失')], string='状态', default='new', required=True)

    # @api.onchange('first_party_phone')
    # def validate_phone_numbers(self):
    #     if self.first_party_phone:
    #         ret = re.match(r"^(((13[0-9]{1})|(15[0-9]{1})|(17[0-9]{1})|(18[0-9]{1}))+\d{8})$", self.first_party_phone)
    #         if not ret:
    #             raise Warning(_("请输入合法手机号码！"))
    #
    # @api.onchange('second_party_phone')
    # def validate_phone_numbers(self):
    #     if self.second_party_phone:
    #         ret = re.match(r"^(((13[0-9]{1})|(15[0-9]{1})|(17[0-9]{1})|(18[0-9]{1}))+\d{8})$", self.second_party_phone)
    #         if not ret:
    #             raise Warning(_("请输入合法手机号码！"))

    def change_business_tracer(self):
        current_context = self._context.copy()
        current_context['current_lead_id'] = self.id

        view = self.env['ir.ui.view'].search([('model', 'like', 'engineering.info.trace.change.project.tracer'),
                                              ('name', 'like', '业务员改派')], order='write_date desc', limit=1)
        return {
            'name': '业务员改派',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'engineering.info.trace.change.project.tracer',
            'views': [(view.id, 'form')],
            'context': current_context
        }

    @api.onchange('project_state')
    def onchange_project_state(self):
        pass

    @api.model
    def create(self, vals):
        first_party_phone_invalid = False
        second_party_phone_invalid = False
        start_and_end_date_invalid = False
        error_message = ""
        if 'first_party_phone' in vals and vals.get('first_party_phone', False):
            first_party_phone = vals.get('first_party_phone')
            ret = re.match(r"^(((13[0-9]{1})|(15[0-9]{1})|(17[0-9]{1})|(18[0-9]{1}))+\d{8})$", first_party_phone)
            if not ret:
                first_party_phone_invalid = True
        if 'second_party_phone' in vals and vals.get('second_party_phone', False):
            second_party_phone = vals.get('second_party_phone')
            ret = re.match(r"^(((13[0-9]{1})|(15[0-9]{1})|(17[0-9]{1})|(18[0-9]{1}))+\d{8})$", second_party_phone)
            if not ret:
                second_party_phone_invalid = True
        if 'date_project_duration_start' in vals and 'date_project_duration_end' in vals:
            date_project_duration_start = vals.get('date_project_duration_start', False)
            date_project_duration_end = vals.get('date_project_duration_end', False)
            if str(date_project_duration_start) > str(date_project_duration_end):
                start_and_end_date_invalid = True
        if first_party_phone_invalid:
            error_message = error_message + '\n请输入合法的甲方联系电话!'
        if second_party_phone_invalid:
            error_message = error_message + '\n请输入合法的乙方联系电话!'
        if start_and_end_date_invalid:
            error_message = error_message + '\n建设周期开始日期必须小于建设周期结束日期!'
        if error_message:
            raise Warning(_(error_message))
        res = super(E2yunHHJCEngineeringInfoTrace, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        self.ensure_one()
        first_party_phone_invalid = False
        second_party_phone_invalid = False
        start_and_end_date_invalid = False
        error_message = ""
        if 'first_party_phone' in vals and vals.get('first_party_phone', False):
            first_party_phone = vals.get('first_party_phone')
            ret = re.match(r"^(((13[0-9]{1})|(15[0-9]{1})|(17[0-9]{1})|(18[0-9]{1}))+\d{8})$", first_party_phone)
            if not ret:
                first_party_phone_invalid = True
        if 'second_party_phone' in vals and vals.get('second_party_phone', False):
            second_party_phone = vals.get('second_party_phone')
            ret = re.match(r"^(((13[0-9]{1})|(15[0-9]{1})|(17[0-9]{1})|(18[0-9]{1}))+\d{8})$", second_party_phone)
            if not ret:
                second_party_phone_invalid = True
        if self.date_project_duration_start and self.date_project_duration_end:
            if 'date_project_duration_start' in vals and 'date_project_duration_end' in vals:
                date_project_duration_start = vals.get('date_project_duration_start', False)
                date_project_duration_end = vals.get('date_project_duration_end', False)
                if str(date_project_duration_start) > str(date_project_duration_end):
                    start_and_end_date_invalid = True
            elif 'date_project_duration_start' in vals:
                date_project_duration_start = vals.get('date_project_duration_start', False)
                date_project_duration_end = self.date_project_duration_end
                if str(date_project_duration_start) > str(date_project_duration_end):
                    start_and_end_date_invalid = True
            elif 'date_project_duration_end' in vals:
                date_project_duration_start = self.date_project_duration_start
                date_project_duration_end = vals.get('date_project_duration_end', False)
                if str(date_project_duration_start) > str(date_project_duration_end):
                    start_and_end_date_invalid = True
        if first_party_phone_invalid:
            error_message = error_message + '\n请输入合法的甲方联系电话!'
        if second_party_phone_invalid:
            error_message = error_message + '\n请输入合法的乙方联系电话!'
        if start_and_end_date_invalid:
            error_message = error_message + '\n建设周期开始日期必须小于建设周期结束日期!'
        if error_message:
            raise Warning(_(error_message))
        res = super(E2yunHHJCEngineeringInfoTrace, self).write(vals)
        return res


