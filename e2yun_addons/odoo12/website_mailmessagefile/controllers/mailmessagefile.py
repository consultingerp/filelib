# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
import unicodedata
from odoo.addons.portal.controllers.mail import PortalChatter
from werkzeug.exceptions import NotFound, Forbidden

from odoo import http
from odoo.http import request
from odoo.tools import consteq, plaintext2html
_logger = logging.getLogger(__name__)

def _has_token_access(res_model, res_id, token=''):
    record = request.env[res_model].browse(res_id).sudo()
    token_field = request.env[res_model]._mail_post_token_field
    return (token and record and consteq(record[token_field], token))


def _message_post_helper(res_model='', res_id=None, message='', token='', nosubscribe=True, **kw):
    """ Generic chatter function, allowing to write on *any* object that inherits mail.thread.
        If a token is specified, all logged in users will be able to write a message regardless
        of access rights; if the user is the public user, the message will be posted under the name
        of the partner_id of the object (or the public user if there is no partner_id on the object).

        :param string res_model: model name of the object
        :param int res_id: id of the object
        :param string message: content of the message

        optional keywords arguments:
        :param string token: access token if the object's model uses some kind of public access
                             using tokens (usually a uuid4) to bypass access rules
        :param bool nosubscribe: set False if you want the partner to be set as follower of the object when posting (default to True)

        The rest of the kwargs are passed on to message_post()
    """
    record = request.env[res_model].browse(res_id)
    author_id = request.env.user.partner_id.id if request.env.user.partner_id else False
    if token:
        access_as_sudo = _has_token_access(res_model, res_id, token=token)
        if access_as_sudo:
            record = record.sudo()
            if request.env.user._is_public():
                if kw.get('pid') and consteq(kw.get('hash'), record._sign_token(int(kw.get('pid')))):
                    author_id = kw.get('pid')
                else:
                    # TODO : After adding the pid and sign_token in access_url when send invoice by email, remove this line
                    # TODO : Author must be Public User (to rename to 'Anonymous')
                    author_id = record.partner_id.id if hasattr(record, 'partner_id') and record.partner_id.id else author_id
            else:
                if not author_id:
                    raise NotFound()
        else:
            raise Forbidden()
    kw.pop('csrf_token', None)

    # kw.pop('attachment_ids', None)

    email_from = None
    if author_id and 'email_from' not in kw:
        partner = request.env['res.partner'].sudo().browse(author_id)
        email_from = partner.email_formatted if partner.email else None

    message_post_args = dict(
        body=message,
        message_type=kw.pop('message_type', "comment"),
        subtype=kw.pop('subtype', "mt_comment"),
        author_id=author_id,
        **kw
    )

    # This is necessary as mail.message checks the presence
    # of the key to compute its default email from
    if email_from:
        message_post_args['email_from'] = email_from

    return record.with_context(mail_create_nosubscribe=nosubscribe).message_post(**message_post_args)


class MessageFilePortalChatter(PortalChatter):

    @http.route()
    def portal_chatter_post(self, res_model, res_id, message, **kw):
        # result = super(MessageFilePortalChatter, self).portal_chatter_post(res_model, res_id, message, **kw);
        # return result
        if kw.get('ufile'):
            attachment_ids = []
            files = request.httprequest.files.getlist('ufile')
            Model = request.env['ir.attachment']
            for ufile in files:
                filename = ufile.filename
                if request.httprequest.user_agent.browser == 'safari':
                    # Safari sends NFD UTF-8 (where é is composed by 'e' and [accent])
                    # we need to send it the same stuff, otherwise it'll fail
                    filename = unicodedata.normalize('NFD', ufile.filename)
                try:
                    attachment = Model.create({
                        'name': filename,
                        'datas': base64.b64encode(ufile.read()),
                        'datas_fname': filename,
                        'res_model': res_model,
                        'res_id': int(0)
                    })
                except Exception:
                    _logger.exception("Fail to upload attachment %s" % ufile.filename)
                attachment_ids.append(attachment.id)
            kw['attachment_ids'] = attachment_ids;
        url = request.httprequest.referrer
        if message or kw.get('ufile'):
            # message is received in plaintext and saved in html
            message = plaintext2html(message)
            _message_post_helper(res_model, int(res_id), message, **kw)
            url = url + "#discussion"
        return request.redirect(url)

    @http.route('/mail/chatter_init', type='json', auth='public', website=True)
    def portal_chatter_init(self, res_model, res_id, domain=False, limit=False, **kwargs):
        result = super(MessageFilePortalChatter, self).portal_chatter_init(res_model, res_id, domain=domain, limit=limit, **kwargs)
        return result

    @http.route('/mail/chatter_fetch', type='json', auth='public', website=True)
    def portal_message_fetch(self, res_model, res_id, domain=False, limit=10, offset=0, **kw):
        return super(MessageFilePortalChatter, self).portal_message_fetch(res_model, res_id, domain=domain, limit=limit, offset=offset, **kw)
