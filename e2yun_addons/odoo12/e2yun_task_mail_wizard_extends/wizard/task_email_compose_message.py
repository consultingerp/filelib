# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
import uuid

from werkzeug import urls

from odoo import api, fields, models, _,exceptions
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
                                ('email_private', 'Send private invitation to your audience (only one response per recipient and per invitation.)'),
                               ('send_internal_process_messages', 'Send internal process messages.')],
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

    @api.onchange('public')
    def onchange_partner_ids(self):
        if self.public == 'send_internal_process_messages':
            domain = [('user_ids.share', '=', False)]
            return {
                'domain': {'partner_ids': domain}
            }
        elif self.public == 'email_private':
            domain = [('user_ids.share', '=', True)]
            return {
                'domain': {'partner_ids': domain}
            }

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

        def create_response_and_send_mail(wizard, partner_id, email):
            """ Create one mail by recipients and replace __URL__ by link with identification token """
            body_a = ""
            for u in wizard.survey_ids:
                token = create_token(wizard, partner_id, email, u.id)
                url = u.public_url
                name = u.title
                if token:
                    url = url + '/'+ token
                body_a = body_a + """<a href='""" + url + """' style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">"""+ name + """</a>"""

            body = """
                <div style="margin: 0px; padding: 0px; font-size: 13px;">
                    <p style="margin: 0px; padding: 0px; font-size: 13px;">
                        您好<br /><br />
                        我们正在进行调查，您的回复将不胜感激。
                        <div style="margin: 16px 0px 16px 0px;">
                            """+body_a+"""
                        </div>
                        谢您的参与！
                    </p>
                </div> 
           """
            values = {
                'model': None,
                'res_id': None,
                'subject': wizard.subject,
                'body': body,
                'body_html': body,
                'parent_id': None,
                'attachment_ids': wizard.attachment_ids and [(6, 0, wizard.attachment_ids.ids)] or None,
                'email_from': wizard.email_from or None,
                'auto_delete': True,
            }
            if partner_id:
                values['recipient_ids'] = [(4, partner_id)]
            else:
                values['email_to'] = email

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

        def create_token(wizard, partner_id, email,survey_id):
            if context.get("survey_resent_user_input"):
                survey_user_input = SurveyUserInput.browse(context.get("survey_resent_user_input"))
                if survey_user_input.state in ('new', 'skip'):
                    return survey_user_input.token
            if context.get("survey_resent_token"):
                survey_user_input = []
                survey_user_input.append(SurveyUserInput.search([('survey_id', '=', survey_id),
                                                                 ('state', 'in', ['new', 'skip']), '|',
                                                                 ('partner_id', '=', partner_id),
                                                                 ('email', '=', email)], limit=1))
                if survey_user_input:
                    input_token = []
                    for input in survey_user_input:
                        input_token.append(input.token)
                    return input_token
            # if wizard.public != 'email_private':
            if wizard.public == 'public_link':
                return None
            elif wizard.public == 'email_private':
                token = pycompat.text_type(uuid.uuid4())
                # create response with token
                survey_user_input = SurveyUserInput.create({
                    'survey_id': survey_id,
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
                # token = create_token(wizard, partner.id, email)
                create_response_and_send_mail(wizard, partner.id, email)

            for partner in partner_list:
                # token = create_token(wizard, partner['id'], partner['email'])
                create_response_and_send_mail(wizard, partner['id'], partner['email'])

        if not self.partner_ids and not self.multi_email:
            raise exceptions.Warning(_('Please select the existing contact person'))
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_send_mail(self):
        self.mail_send()
        if not self.partner_ids and not self.multi_email:
            raise exceptions.Warning(_('Please enter an existing contact or email list'))
        return {'type': 'ir.actions.act_window_close', 'infos': 'mail_sent'}

    @api.multi
    def mail_send(self, auto_commit=False):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        notif_layout = self._context.get('custom_layout')
        # Several custom layouts make use of the model description at rendering, e.g. in the
        # 'View <document>' button. Some models are used for different business concepts, such as
        # 'purchase.order' which is used for a RFQ and and PO. To avoid confusion, we must use a
        # different wording depending on the state of the object.
        # Therefore, we can set the description in the context from the beginning to avoid falling
        # back on the regular display_name retrieved in '_notify_prepare_template_context'.
        model_description = self._context.get('model_description')
        for wizard in self:
            # Duplicate attachments linked to the email.template.
            # Indeed, basic mail.compose.message wizard duplicates attachments in mass
            # mailing mode. But in 'single post' mode, attachments of an email template
            # also have to be duplicated to avoid changing their ownership.
            if wizard.attachment_ids and wizard.composition_mode != 'mass_mail' and wizard.template_id:
                new_attachment_ids = []
                for attachment in wizard.attachment_ids:
                    if attachment in wizard.template_id.attachment_ids:
                        new_attachment_ids.append(
                            attachment.copy({'res_model': 'mail.compose.message', 'res_id': wizard.id}).id)
                    else:
                        new_attachment_ids.append(attachment.id)
                wizard.write({'attachment_ids': [(6, 0, new_attachment_ids)]})

            # Mass Mailing
            mass_mode = wizard.composition_mode in ('mass_mail', 'mass_post')

            Mail = self.env['mail.mail']
            ActiveModel = self.env[wizard.model] if wizard.model and hasattr(self.env[wizard.model],
                                                                             'message_post') else self.env[
                'mail.thread']
            if wizard.composition_mode == 'mass_post':
                # do not send emails directly but use the queue instead
                # add context key to avoid subscribing the author
                ActiveModel = ActiveModel.with_context(mail_notify_force_send=False, mail_create_nosubscribe=True)
            # wizard works in batch mode: [res_id] or active_ids or active_domain
            if mass_mode and wizard.use_active_domain and wizard.model:
                res_ids = self.env[wizard.model].search(safe_eval(wizard.active_domain)).ids
            elif mass_mode and wizard.model and self._context.get('active_ids'):
                res_ids = self._context['active_ids']
            else:
                res_ids = [wizard.res_id]

            batch_size = int(self.env['ir.config_parameter'].sudo().get_param('mail.batch_size')) or self._batch_size
            sliced_res_ids = [res_ids[i:i + batch_size] for i in range(0, len(res_ids), batch_size)]

            if wizard.composition_mode == 'mass_mail' or wizard.is_log or (
                    wizard.composition_mode == 'mass_post' and not wizard.notify):  # log a note: subtype is False
                subtype_id = False
            elif wizard.subtype_id:
                subtype_id = wizard.subtype_id.id
            else:
                subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')

            SurveyUserInput = self.env['survey.user_input']
            Partner = self.env['res.partner']
            def create_token(wizard, partner_id, email, survey_id):
                token = pycompat.text_type(uuid.uuid4())
                # create response with token
                survey_user_input = SurveyUserInput.create({
                    'survey_id': survey_id,
                    'deadline': wizard.date_deadline,
                    'date_create': fields.Datetime.now(),
                    'type': 'link',
                    'state': 'new',
                    'token': token,
                    'partner_id': partner_id,
                    'email': email})
                return survey_user_input.token

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

            survey_ids = wizard._context['default_survey_ids']
            survey = self.env['survey.survey']
            body_a = """"""
            for email in emails_list:
                partner = Partner.search([('email', '=', email)], limit=1)
                #消息内容
                for u in survey.browse(survey_ids):
                    url = u.public_url
                    name = u.title
                    token = create_token(wizard, partner.id, email, u.id)
                    if token:
                        url = url + '/' + token
                    body_a = body_a + """<a href='""" + url + """' style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">""" + name + """</a>"""

                body = """
                     <div style="margin: 0px; padding: 0px; font-size: 13px;">
                         <p style="margin: 0px; padding: 0px; font-size: 13px;">
                             您好<br /><br />
                             我们正在进行调查，您的回复将不胜感激。
                             <div style="margin: 16px 0px 16px 0px;">
                                 """ + body_a + """
                             </div>
                             谢您的参与！
                         </p>
                     </div> 
                """
                for res_ids in sliced_res_ids:
                    batch_mails = Mail
                    all_mail_values = wizard.get_mail_values(res_ids)
                    for res_id, mail_values in all_mail_values.items():
                        if wizard.composition_mode == 'mass_mail':
                            batch_mails |= Mail.create(mail_values)
                        else:
                            mail_values['body'] = body
                            post_params = dict(
                                message_type=wizard.message_type,
                                subtype_id=subtype_id,
                                notif_layout=notif_layout,
                                add_sign=not bool(wizard.template_id),
                                mail_auto_delete=wizard.template_id.auto_delete if wizard.template_id else False,
                                model_description=model_description,
                                **mail_values)
                            if ActiveModel._name == 'mail.thread' and wizard.model:
                                post_params['model'] = wizard.model
                            ActiveModel.browse(res_id).message_post(**post_params)

                    if wizard.composition_mode == 'mass_mail':
                        batch_mails.send(auto_commit=auto_commit)

            for partner in partner_list:
                # 消息内容
                for u in survey.browse(survey_ids):
                    url = u.public_url
                    name = u.title
                    token = create_token(wizard, partner['id'], partner['email'], u.id)
                    if token:
                        url = url + '/' + token
                    body_a = body_a + """<a href='""" + url + """' style="background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">""" + name + """</a>"""

                body = """
                                     <div style="margin: 0px; padding: 0px; font-size: 13px;">
                                         <p style="margin: 0px; padding: 0px; font-size: 13px;">
                                             您好<br /><br />
                                             我们正在进行调查，您的回复将不胜感激。
                                             <div style="margin: 16px 0px 16px 0px;">
                                                 """ + body_a + """
                                             </div>
                                             谢您的参与！
                                         </p>
                                     </div> 
                                """
                for res_ids in sliced_res_ids:
                    batch_mails = Mail
                    all_mail_values = wizard.get_mail_values(res_ids)
                    for res_id, mail_values in all_mail_values.items():
                        if wizard.composition_mode == 'mass_mail':
                            batch_mails |= Mail.create(mail_values)
                        else:
                            mail_values['body'] = body
                            post_params = dict(
                                message_type=wizard.message_type,
                                subtype_id=subtype_id,
                                notif_layout=notif_layout,
                                add_sign=not bool(wizard.template_id),
                                mail_auto_delete=wizard.template_id.auto_delete if wizard.template_id else False,
                                model_description=model_description,
                                **mail_values)
                            if ActiveModel._name == 'mail.thread' and wizard.model:
                                post_params['model'] = wizard.model
                            ActiveModel.browse(res_id).message_post(**post_params)

                    if wizard.composition_mode == 'mass_mail':
                        batch_mails.send(auto_commit=auto_commit)

