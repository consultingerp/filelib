# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
import uuid

from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import pycompat

_logger = logging.getLogger(__name__)

emails_split = re.compile(r"[;,\n\r]+")
email_validator = re.compile(r"[^@]+@[^@]+\.[^@]+")


class SurveyMailComposeMessage(models.TransientModel):
    _name = 'task.mail.compose.message'
    _inherit = 'mail.compose.message'
    _description = 'Email composition wizard for Task'

    # def default_survey_id(self):
    #     context = self.env.context
    #     if context.get('model') == 'project.task':
    #         id = context.get('res_id')
    #         record = self.env['project.task'].search([{'id', '=', id }])
    #         if record.questionnaire_ids:
    #             all_template = []
    #             for questionnaire in record.questionnaire_ids:
    #                 questionnaire.survey_temp_id
    #             return context.get('res_id')

    def default_survey_ids(self):
        context = self.env.context
        if context.get('model') == 'project.task':
            id = context.get('res_id')
            record = self.env['project.task'].search([{'id', '=', id }])
            if record.questionnaire_ids:
                all_template = []
                for questionnaire in record.questionnaire_ids:
                    all_template.append(questionnaire.survey_temp_id.id)
                return all_template

    # survey_id = fields.Many2many('survey.survey', string='Survey', default=default_survey_id, required=True)
    survey_ids = fields.Many2many('survey.survey', string='Survey', default=default_survey_ids, required=True)
    public = fields.Selection([('public_link', 'Share the public web link to your audience.'),
                                ('email_public_link', 'Send by email the public web link to your audience.'),
                                ('email_private', 'Send private invitation to your audience (only one response per recipient and per invitation).')],
                                string='Share options', default='public_link', required=True)
    public_url = fields.Char(compute="_compute_survey_url", string="Public url")
    public_url_html = fields.Char(compute="_compute_survey_url", string="Public HTML web link")
    # partner_ids = fields.Many2many('res.partner', 'survey_mail_compose_message_res_partner_rel', 'wizard_id', 'partner_id', string='Existing contacts')
    partner_ids = fields.Many2many('res.partner', 'wizard_id', string='Existing contacts')
    attachment_ids = fields.Many2many('ir.attachment', 'survey_mail_compose_message_ir_attachments_rel', 'wizard_id', 'attachment_id', string='Attachments')
    multi_email = fields.Text(string='List of emails', help="This list of emails of recipients will not be converted in contacts.\
        Emails must be separated by commas, semicolons or newline.")
    date_deadline = fields.Date(string="Deadline to which the invitation to respond is valid",
        help="Deadline to which the invitation to respond for this survey is valid. If the field is empty,\
        the invitation is still valid.")

    @api.depends('survey_ids')
    def _compute_survey_url(self):
        for wizard in self:
            public_urls,public_url_htmls = [],[]
            for sur in wizard.survey_ids:
                public_urls.append(sur.public_url)
                public_url_htmls.append(sur.public_url_html)
            wizard.public_url = public_urls
            wizard.public_url_html = public_url_htmls

    @api.model
    def default_get(self, fields):
        res = super(SurveyMailComposeMessage, self).default_get(fields)
        context = self.env.context
        if context.get('active_model') == 'res.partner' and context.get('active_ids'):
            res.update({'partner_ids': context['active_ids']})
        return res

    @api.onchange('multi_email')
    def onchange_multi_email(self):
        emails = list(set(emails_split.split(self.multi_email or "")))
        emails_checked = []
        error_message = ""
        for email in emails:
            email = email.strip()
            if email:
                if not email_validator.match(email):
                    error_message += "\n'%s'" % email
                else:
                    emails_checked.append(email)
        if error_message:
            raise UserError(_("Incorrect Email Address: %s") % error_message)

        emails_checked.sort()
        self.multi_email = '\n'.join(emails_checked)

    #------------------------------------------------------
    # Wizard validation and send
    #------------------------------------------------------

    @api.multi
    def send_mail_action(self):
        return self.send_mail()

    @api.multi
    def send_mail(self, auto_commit=False):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed """

        SurveyUserInput = self.env['survey.user_input']
        Partner = self.env['res.partner']
        Mail = self.env['mail.mail']
        notif_layout = self.env.context.get('notif_layout', self.env.context.get('custom_layout'))

        def create_response_and_send_mail(wizard, token, partner_id, email):
            """ Create one mail by recipients and replace __URL__ by link with identification token """
            #set url
            urls = []
            for u in wizard.survey_ids:
                 urls.append(u.public_url)
            if token:
                if len(wizard.survey_ids) == 1:
                    urls = urls.replace(0,urls[0]+token[0])
                elif len(wizard.survey_ids) == 2:
                    urls = urls.replace(0,urls[0]+token[0])
                    urls = urls.replace(1,urls[1]+token[1])
                elif len(wizard.survey_ids) == 3:
                    urls = urls.replace(0,urls[0]+token[0])
                    urls = urls.replace(1,urls[1]+token[1])
                    urls = urls.replace(2, urls[2] + token[2])
            # urls = wizard.survey_id.public_url

            # if token:
            #     urls = []
            #     for ul in urls:
            #         ul = ul + '/' + token
            #         urls.append(ul)
            # post the message:判断问卷的个数，在进行url的替换
            if len(wizard.survey_ids) == 1:
                url = urls[0]
                values = {
                    'model': None,
                    'res_id': None,
                    'subject': wizard.subject,
                    'body': wizard.body.replace("__URL__", url),
                    'body_html': wizard.body.replace("__URL__", url),
                    'parent_id': None,
                    'attachment_ids': wizard.attachment_ids and [(6, 0, wizard.attachment_ids.ids)] or None,
                    'email_from': wizard.email_from or None,
                    'auto_delete': True,
                }
                if partner_id:
                    values['recipient_ids'] = [(4, partner_id)]
                else:
                    values['email_to'] = email

            elif len(wizard.survey_ids) == 2:
                url1 = urls[0]
                url2 = urls[1]
                values = {
                    'model': None,
                    'res_id': None,
                    'subject': wizard.subject,
                    'body': wizard.body.replace("zhangsan", url1).replace("lisi", url2),
                    'body_html': wizard.body.replace("zhangsan", url1).replace("lisi", url2),
                    'parent_id': None,
                    'attachment_ids': wizard.attachment_ids and [(6, 0, wizard.attachment_ids.ids)] or None,
                    'email_from': wizard.email_from or None,
                    'auto_delete': True,
                }
                if partner_id:
                    values['recipient_ids'] = [(4, partner_id)]
                else:
                    values['email_to'] = email
            elif len(wizard.survey_ids) == 3:
                url1 = urls[0]
                url2 = urls[1]
                url3 = urls[2]
                values = {
                    'model': None,
                    'res_id': None,
                    'subject': wizard.subject,
                    'body': wizard.body.replace("zhangsan", url1).replace("lisi", url2).replace("wangwu", url3),
                    'body_html': wizard.body.replace("zhangsan", url1).replace("lisi", url2).replace("wangwu", url3),
                    'parent_id': None,
                    'attachment_ids': wizard.attachment_ids and [(6, 0, wizard.attachment_ids.ids)] or None,
                    'email_from': wizard.email_from or None,
                    'auto_delete': True,
                }
                if partner_id:
                    values['recipient_ids'] = [(4, partner_id)]
                else:
                    values['email_to'] = email

            # optional support of notif_layout in context
            if notif_layout:
                try:
                    template = self.env.ref(notif_layout, raise_if_not_found=True)
                except ValueError:
                    _logger.warning('QWeb template %s not found when sending survey mails. Sending without layouting.' % (notif_layout))
                else:
                    template_ctx = {
                        'message': self.env['mail.message'].sudo().new(dict(body=values['body_html'])),
                        'model_description': self.env['ir.model']._get('survey.survey').display_name,
                        'company': self.env.user.company_id,
                    }
                    body = template.render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
                    values['body_html'] = self.env['mail.thread']._replace_local_links(body)

            Mail.create(values).send()

        def create_token(wizard, partner_id, email):
            if context.get("survey_resent_user_input"):
                survey_user_input = SurveyUserInput.browse(context.get("survey_resent_user_input"))
                if survey_user_input.state in ('new', 'skip'):
                    return survey_user_input.token
            if context.get("survey_resent_token"):
                all_surveys = []
                for survey in wizard.survey_ids:
                    all_surveys.append(survey.id)
                survey_user_input = []
                if len(all_surveys) == 1:
                    survey_user_input.append(SurveyUserInput.search([('survey_id', '=', all_surveys[0]),
                        ('state', 'in', ['new', 'skip']), '|', ('partner_id', '=', partner_id),
                        ('email', '=', email)], limit=1))
                    # if survey_user_input:
                    #     return survey_user_input.token
                elif len(all_surveys) == 2:
                    survey_user_input.append(SurveyUserInput.search([('survey_id', '=', all_surveys[0]),
                        ('state', 'in', ['new', 'skip']), '|', ('partner_id', '=', partner_id),
                        ('email', '=', email)], limit=1))
                    survey_user_input.append(SurveyUserInput.search([('survey_id', '=', all_surveys[1]),
                                                ('state', 'in', ['new', 'skip']), '|', ('partner_id', '=', partner_id),
                                                ('email', '=', email)], limit=1))
                    # if survey_user_input:
                    #     return survey_user_input.token
                elif len(all_surveys) == 3:
                    survey_user_input.append(SurveyUserInput.search([('survey_id', '=', all_surveys[0]),
                        ('state', 'in', ['new', 'skip']), '|', ('partner_id', '=', partner_id),
                        ('email', '=', email)], limit=1))
                    survey_user_input.append(SurveyUserInput.search([('survey_id', '=', all_surveys[1]),
                                                ('state', 'in', ['new', 'skip']), '|', ('partner_id', '=', partner_id),
                                                ('email', '=', email)], limit=1))
                    survey_user_input.append(SurveyUserInput.search([('survey_id', '=', all_surveys[2]),
                                                                     ('state', 'in', ['new', 'skip']), '|',
                                                                     ('partner_id', '=', partner_id),
                                                                     ('email', '=', email)], limit=1))
                if survey_user_input:
                    input_token = []
                    for input in survey_user_input:
                        input_token.append(input.token)
                    return input_token
            if wizard.public != 'email_private':
                return None
            else:
                token = pycompat.text_type(uuid.uuid4())
                # create response with token
                survey_user_input = SurveyUserInput.create({
                    'survey_id': wizard.survey_id.id,
                    'deadline': wizard.date_deadline,
                    'date_create': fields.Datetime.now(),
                    'type': 'link',
                    'state': 'new',
                    'token': token,
                    'partner_id': partner_id,
                    'email': email})
                return survey_user_input.token

        for wizard in self:
            # check if __URL__ is in the text
            # if wizard.body.find("__URL__") < 0:
            #     raise UserError(_("The content of the text don't contain '__URL__'. \
            #         __URL__ is automaticaly converted into the special url of the survey."))

            context = self.env.context
            if not wizard.multi_email and not wizard.partner_ids and (context.get('default_partner_ids') or context.get('default_multi_email')):
                wizard.multi_email = context.get('default_multi_email')
                wizard.partner_ids = context.get('default_partner_ids')

            # quick check of email list
            emails_list = []
            if wizard.multi_email:
                emails = set(emails_split.split(wizard.multi_email)) - set(wizard.partner_ids.mapped('email'))
                for email in emails:
                    email = email.strip()
                    if email_validator.match(email):
                        emails_list.append(email)

            # remove public anonymous access
            partner_list = []
            for partner in wizard.partner_ids:
                partner_list.append({'id': partner.id, 'email': partner.email})

            if not len(emails_list) and not len(partner_list):
                if wizard.model == 'res.partner' and wizard.res_id:
                    return False
                raise UserError(_("Please enter at least one valid recipient."))

            for email in emails_list:
                partner = Partner.search([('email', '=', email)], limit=1)
                token = create_token(wizard, partner.id, email)
                create_response_and_send_mail(wizard, token, partner.id, email)

            for partner in partner_list:
                token = create_token(wizard, partner['id'], partner['email'])
                create_response_and_send_mail(wizard, token, partner['id'], partner['email'])

        return {'type': 'ir.actions.act_window_close'}


