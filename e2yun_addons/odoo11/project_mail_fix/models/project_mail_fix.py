# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def create(self, vals):
        #_logger.error('type_id:%s,project_id:%s' % (vals.get('type_id', False),vals.get('project_id', False)))
        if vals.get('type_id', False) == False and  vals.get('project_id', False) :
            project = self.env['project.project'].browse(vals.get('project_id', False))
            #_logger.error('project id values:%s' % project.type_id.id)
            vals['type_id'] = self.env['project.task.type2'].search(
                [('project_type_ids' ,'=',project.type_id.id)],limit=1).id
        if vals.get('priority_id', False) ==False:
            vals['priority_id']= self.env['project.task.priority'].search(
                [('type_ids' ,'=',vals['type_id'])],limit=1).id
        #_logger.error('new  values:%s' % vals)
        return super(ProjectTask, self).create(vals)

    @api.model
    def message_new(self, msg, custom_values=None):
        if custom_values is None:
            custom_values = {'description':msg.get('body')}
        else:
            custom_values.update({'description':msg.get('body')})
        msg['body']= msg.get('subject') or _("No Subject")
        return super(ProjectTask, self). message_new(msg, custom_values=custom_values)