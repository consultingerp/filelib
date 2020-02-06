# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today OpenERP SA (<http://www.openerp.com>).
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

from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request
import werkzeug
import datetime
import time

from odoo.tools.translate import _

class srm_account_quiry(http.Controller):
    _name = 'srm.account.quiry'

    @http.route([
        "/srm_inquiry_account/<int:account_id>",
        "/srm_inquiry_account/<int:account_id>/<token>"
    ], type='http', auth="public", website=True)
    def view(self, account_id, token=None, message=False, **post):
        order = request.env['srm.account.order'].browse(account_id)
        now = time.strftime('%Y-%m-%d')
        # if request.uid:
        #     if request.uid != order.access_token:
        #         return request.render('website.404')

        values = {
            'quotation': order,
            'message': False,
            'option': False,
            'order_valid': True,
            'days_valid': 30,
        }
        return request.render('srm_account_order.srm_account_inquiry_template', values)

    @http.route(['/srm_inquiry_account/accept'], type='json', auth="public", website=True)
    def accept(self, account_id, token=None, signer=None, sign=None, **post):
        order_obj = request.env['srm.account.order']
        order = order_obj.browse(account_id)
        attachments=sign and [('signature.png', sign.decode('base64'))] or []
        order.state = 'supplier_confirm'  # 供应商同意
        message = _('Order signed by %s') % (signer,)
        self.__message_post(message, account_id, type='comment', subtype='mt_comment', attachments=attachments)
        return True

    @http.route(['/srm_inquiry_account/accept1/<int:account_id>'])
    def accept1(self, account_id, token=None, signer=None, sign=None, **post):
        order_obj = request.env['srm.account.order']
        order = order_obj.browse(account_id)
        order.state = 'supplier_confirm' #供应商同意
        message = _('Order signed by %s') % (signer,)
        attachments = sign and [('signature.png', sign.decode('base64'))] or []
        self.__message_post(message, account_id, type='comment', subtype='mt_comment', attachments=attachments)
        return werkzeug.utils.redirect("/srm_inquiry_account/%s?message=1" % (account_id))

    @http.route(['/srm_inquiry_account/<int:account_id>/decline'])
    def decline(self, account_id, token=None,decline_message=None, **post):
        order_obj = request.env['srm.account.order']
        order = order_obj.browse(account_id)
        order['state'] = 'supply_refuse'   #供应商拒绝
        if decline_message:
            decline_message = '供应商拒绝 拒绝原因:' + decline_message
            self.__message_post(decline_message, account_id, type='comment', subtype='mt_comment')
        return werkzeug.utils.redirect("/srm_inquiry_account/%s?message=2" % (account_id))

    @http.route(['/srm_inquiry_account/<int:account_id>/post'], type='http', auth="public", website=True)
    def post(self, account_id, token=None,**post):
        # use SUPERUSER_ID allow to access/view order for public user
        order_obj = request.env['srm.account.order']
        order = order_obj.browse(account_id)
        message = post.get('comment')
        if message:
            self.__message_post(message, account_id, type='comment', subtype='mt_comment')
        return werkzeug.utils.redirect("/srm_inquiry_account/%s?message=1" % (account_id))

    def __message_post(self, message, account_id, type='comment', subtype=False, attachments=[]):
        request.session.body =  message
        user = request.env['res.users'].browse(request._uid)
        if 'body' in request.session and request.session.body:
            if str(request.session.body)=='供应商审查过':
                return True
            request.env['mail.message'].create(
                {'res_id': account_id,
                 'model': 'srm.account.order',
                 'subtype_id': 1,
                 'body': request.session.body
                 }
            )
            request.session.body = False
        return True




