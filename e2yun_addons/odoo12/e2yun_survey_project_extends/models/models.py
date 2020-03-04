# -*- coding: utf-8 -*-
from collections import defaultdict

# special columns automatically created by the ORM
LOG_ACCESS_COLUMNS = ['create_uid', 'create_date', 'write_uid', 'write_date']
MAGIC_COLUMNS = ['id'] + LOG_ACCESS_COLUMNS

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class E2yunProjectTaskAddQuestionnaire(models.TransientModel):
    _name = 'project.task.add.questionnaire'
    _description = '任务页面添加问卷按钮'

    # 问卷分类
    questionnaire_classification = fields.Selection([('Internally', '对内'), ('Foreign', '对外')], string='问卷分类')
    # 是否多问卷
    multiple_questionnaires = fields.Selection([('yes', '是'), ('no', '否')], string='是否多问卷')
    questionnaire_scenario = fields.Selection(
        [('评分问卷', '评分问卷'), ('资质调查', '资质调查'), ('满意度调查', '满意度调查'),
         ('报名登记表', '报名登记表'), ('其他', '其他')], string='问卷场景')
    # 权重
    weight = fields.Char(string='权重')
    # 问卷模板
    survey_temp_id = fields.Many2one('survey.survey', string='问卷模版')
    questionnaire_name = fields.Char('问卷名称')

    @api.onchange('questionnaire_scenario')
    def _onchange_questionnaire_scenario(self):
        survey_temp_id_domain = [('questionnaire_classification', '=', self.questionnaire_classification),
                                 ('questionnaire_scenario', '=', self.questionnaire_scenario)]
        context = self._context.copy()
        if context.get('add_new_questionnaire'):
            return {
                'domain': {'survey_temp_id': [('id', '=', -1)]}
            }
        else:
            return {
                'domain': {'survey_temp_id': survey_temp_id_domain}
            }

    def add_questionnaire_to_task(self):
        current_project_task_id = self._context.get('current_project_task_id')
        current_project_task = self.env['project.task'].browse(current_project_task_id)

        if self._context.get('add_new_questionnaire'):
            survey_after_copy = self.survey_temp_id
        else:
            survey_after_copy = self.survey_temp_id.copy({'new_title': self.questionnaire_name})
            # survey_after_copy.write({'title': self.questionnaire_name})
        weight = self.weight
        questionnaire_scenario = self.questionnaire_scenario

        new_project_task_questionnaire_ids_values = {
            'questionnaire_scenario': questionnaire_scenario,
            'weight': weight,
            'survey_temp_id': survey_after_copy.id
        }

        new_project_task_questionnaire_ids_item = self.env['project.questionnaire'].create(
            new_project_task_questionnaire_ids_values)
        if new_project_task_questionnaire_ids_item:
            current_questionnaire_ids = current_project_task.questionnaire_ids.ids
            current_questionnaire_ids.append(new_project_task_questionnaire_ids_item.id)
            current_project_task.update({
                'questionnaire_ids': current_questionnaire_ids
            })
            return 1
        else:
            raise Warning(_("无法正确新建行项目!"))

    @api.model
    def default_get(self, fields_list):
        res = super(E2yunProjectTaskAddQuestionnaire, self).default_get(fields_list)
        res.update({'questionnaire_classification': self._context.get('current_questionnaire_classification'),
                    'multiple_questionnaires': self._context.get('multiple_questionnaires')})
        return res


class E2yunSurveyProjectExtends(models.Model):
    _inherit = 'project.task'

    questionnaire_ids_len = fields.Integer('问卷数量', compute='_compute_questionnaire_ids_length', store=True)

    # , compute='_compute_questionnaire_ids_length', store=True
    @api.multi
    @api.depends('questionnaire_ids')
    def _compute_questionnaire_ids_length(self):
        for rec in self:
            rec.questionnaire_ids_len = len(rec.questionnaire_ids)

    # @api.onchange('questionnaire_ids')
    # def onchange_questionnaire_ids_len(self):
    #     self.questionnaire_ids_len = len(self.questionnaire_ids)

    def project_task_survey_add_questionnaire(self):
        current_context = self._context.copy()
        current_context['current_questionnaire_classification'] = self.questionnaire_classification
        current_context['multiple_questionnaires'] = self.multiple_questionnaires
        current_context['current_project_task_id'] = self.id
        current_context['copy_for_survey_project'] = True
        view = self.env['ir.ui.view'].search([('model', 'like', 'project.task.add.questionnaire'),
                                              ('name', 'like', '添加历史问卷')], order='write_date desc', limit=1)
        if view:
            return {
                'name': '添加问卷',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view.id, 'form')],
                'target': 'new',
                'res_model': 'project.task.add.questionnaire',
                'context': current_context
            }
        else:
            return {
                'name': '添加问卷',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'project.task.add.questionnaire',
                'context': current_context
            }

    def project_task_survey_add_new_questionnaire(self):
        current_context = self._context.copy()
        current_context['current_questionnaire_classification'] = self.questionnaire_classification
        current_context['multiple_questionnaires'] = self.multiple_questionnaires
        current_context['current_project_task_id'] = self.id
        current_context['add_new_questionnaire'] = True
        view = self.env['ir.ui.view'].search([('model', 'like', 'project.task.add.questionnaire'),
                                              ('name', 'like', '添加新问卷')], order='write_date desc', limit=1)
        if view:
            return {
                'name': '添加问卷',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view.id, 'form')],
                'target': 'new',
                'res_model': 'project.task.add.questionnaire',
                'context': current_context
            }
        else:
            return {
                'name': '添加问卷',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'project.task.add.questionnaire',
                'context': current_context
            }


class E2yunSurveyProjectSurveyExtends(models.Model):
    _inherit = 'survey.survey'

    @api.multi
    def copy(self, default=None):
        res = super(E2yunSurveyProjectSurveyExtends, self).copy(default)
        return res

    @api.model
    def default_get(self, fields_list):
        res = super(E2yunSurveyProjectSurveyExtends, self).default_get(fields_list)
        return res

    @api.multi
    @api.returns(None, lambda value: value[0])
    def base_copy_data(self, default=None):
        """
        Copy given record's data with all its fields values

        :param default: field values to override in the original values of the copied record
        :return: list with a dictionary containing all the field values
        """
        # In the old API, this method took a single id and return a dict. When
        # invoked with the new API, it returned a list of dicts.
        self.ensure_one()

        # avoid recursion through already copied records in case of circular relationship
        if '__copy_data_seen' not in self._context:
            self = self.with_context(__copy_data_seen=defaultdict(set))
        seen_map = self._context['__copy_data_seen']
        if self.id in seen_map[self._name]:
            return
        seen_map[self._name].add(self.id)

        default = dict(default or [])
        if 'state' not in default and 'state' in self._fields:
            field = self._fields['state']
            if field.default:
                value = field.default(self)
                value = field.convert_to_cache(value, self)
                value = field.convert_to_record(value, self)
                value = field.convert_to_write(value, self)
                default['state'] = value

        # build a black list of fields that should not be copied
        blacklist = set(MAGIC_COLUMNS + ['parent_path'])
        whitelist = set(name for name, field in self._fields.items() if not field.inherited)

        def blacklist_given_fields(model):
            # blacklist the fields that are given by inheritance
            for parent_model, parent_field in model._inherits.items():
                blacklist.add(parent_field)
                if parent_field in default:
                    # all the fields of 'parent_model' are given by the record:
                    # default[parent_field], except the ones redefined in self
                    blacklist.update(set(self.env[parent_model]._fields) - whitelist)
                else:
                    blacklist_given_fields(self.env[parent_model])
            # blacklist deprecated fields
            for name, field in model._fields.items():
                if field.deprecated:
                    blacklist.add(name)

        blacklist_given_fields(self)

        fields_to_copy = {name: field
                          for name, field in self._fields.items()
                          if field.copy and name not in default and name not in blacklist}

        for name, field in fields_to_copy.items():
            if field.type == 'one2many':
                # duplicate following the order of the ids because we'll rely on
                # it later for copying translations in copy_translation()!
                lines = [rec.copy_data()[0] for rec in self[name].sorted(key='id')]
                # the lines are duplicated using the wrong (old) parent, but then
                # are reassigned to the correct one thanks to the (0, 0, ...)
                default[name] = [(0, 0, line) for line in lines if line]
            elif field.type == 'many2many':
                default[name] = [(6, 0, self[name].ids)]
            else:
                default[name] = field.convert_to_write(self[name], self)

        return [default]

    def copy_data(self, default=None):
        context = self._context.copy()
        if context.get('copy_for_survey_project') and default.get('new_title'):
            title = default.get('new_title')
            default = dict(default or {}, title=title)
            res = self.base_copy_data(default)
            return res
        else:
            res = super(E2yunSurveyProjectSurveyExtends, self).copy_data(default)
            return res
