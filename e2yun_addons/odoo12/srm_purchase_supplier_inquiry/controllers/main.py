#! /usr/bin/env python3

"""Base16, Base32, Base64 (RFC 3548), Base85 and Ascii85 data encodings"""

# Modified 04-Oct-1995 by Jack Jansen to use binascii module
# Modified 30-Dec-2003 by Barry Warsaw to add full RFC 3548 support
# Modified 22-May-2007 by Guido van Rossum to use bytes everywhere

from odoo import api, fields, models, exceptions,SUPERUSER_ID, _
from odoo import http
import werkzeug
import time
import json
from odoo.http import request
import base64
class purchase_quote(http.Controller):
    _name = 'purchase.quote'

    @http.route('/test/<int:id>/',  type='json', auth="public", methods=['POST'], website=True)
    def index(self,id,sign=None,**post):
       # return http.request.render("cqnew_demo.index", {'fruits': ['apple', 'banana', 'pear']})
       #return  order_id
      # return '<h1>{} ({})</h1>'.format(id, type(id).__name__)
       jsons = [
           {
               'id': 8,
               'name': 'qiu'
           },
           {
               'id': 9,
               'name': 'chu'
           }
       ]
       print(sign)
       attachments = [('signature.png', base64.b64decode(sign))] if sign else [],
       print(attachments)
       jsons =json.dumps(jsons)
       return jsons

    @http.route([
        "/quote_purchase/<int:order_id>",
        "/quote_purchase/<int:order_id>/<token>"
    ], type='http', auth="public", website=True)
    def view(self,order_id, token=None, message=False, **post):
        order = request.env['purchase.order'].sudo().browse(order_id)
        now = time.strftime('%Y-%m-%d')
        if token:
            if token != order.access_token:
                return request.render('website.404')

            # Log only once a day
            if request.session.get('view_quote',False)!=now:
                request.session['view_quote'] = now
                body=_('Quotation viewed by customer')
                self.__message_post(body, order_id, type='comment')
        days = 0
        values = {
            'quotation': order,
            # 'message': message and int(message) or False,
            # 'option': bool(filter(lambda x: not x.line_id, order.options)),
            # 'order_valid': (not order.validity_date) or (now <= order.validity_date),
            # 'days_valid': days,

            'message': False,
            'option': False,
            'order_valid': True,
            'days_valid': days,
        }

        return request.render('srm_purchase_supplier_inquiry.so_quotation', values)



    @http.route('/quote_purchase/accept', type='json', auth="public", methods=['POST'], website=True)
    def accept(self, order_id=None, token=None, signer=None, sign=None, **post):
        order_obj = request.env['purchase.order'].sudo()
        order = order_obj.browse(order_id)
        print(sign)
        attachments = [('signature.png', base64.b64decode(sign))] if sign else [],
        order['state'] = 'supply_confirm' #供应商同意
        message = _('Order signed by %s') % (signer,)

        self.__message_post(message, order_id, type='comment', subtype='mt_comment', attachments=attachments)
        return werkzeug.utils.redirect("/quote_purchase/%s" % (order_id,))

    @http.route('/quote_purchase/decline/<int:order_id>', type='http', auth="public", methods=['POST'],website=True)
    def decline(self, order_id=None, token=None, **post):
        order_obj = request.env['purchase.order'].sudo()
        order = order_obj.browse(order_id)
        # if token != order.access_token:
        #     return request.render('website.404')
        # if order.state != 'sent':
        #     return werkzeug.utils.redirect("/quote_purchase/%s/%s?message=4" % (order_id, token))
        #request.registry.get('purchase.order').action_cancel(request.cr, SUPERUSER_ID, [order_id])
        order['state'] = 'supply_refuse'   #供应商拒绝
        message = post.get('decline_message')
        if message:
            self.__message_post(message, order_id, type='comment', subtype='mt_comment')
            return werkzeug.utils.redirect("/quote_purchase/%s" % (order_id,))

    @http.route(['/quote_purchase/<int:order_id>/<token>/post'], type='http', auth="public", website=True)
    def post(self, order_id, token, **post):
        # use SUPERUSER_ID allow to access/view order for public user
        order_obj = request.env['purchase.order'].sudo()
        order = order_obj.browse(order_id)
        message = post.get('comment')
        if token != order.access_token:
            return request.render('website.404')
        if message:
            self.__message_post(message, order_id, type='comment', subtype='mt_comment')
        return werkzeug.utils.redirect("/quote_purchase/%s/%s?message=1" % (order_id, token))

    def __message_post(self, message, order_id, type='comment', subtype=False, attachments=[]):
        request.session.body =  message
        cr, uid, context = request._cr, request._uid, request._context
        user = request.env['res.users'].browse(uid)
        if 'body' in request.session and request.session.body:
            if str(request.session.body)=='供应商审查过':
                return True
            request.env['mail.message'].create(
                {'res_id': order_id,
                 'model': 'purchase.order',
                 'subtype_id': 1,
                 'body': request.session.body
                 }
            )


    @http.route(['/quote_purchase/update_line'], type='json', auth="public", website=True)
    def update(self, line_id, remove=False, unlink=False, order_id=None, token=None, **post):
        order = request.env['purchase.order'].browse(int(order_id))
        if token != order.access_token:
            return request.render('website.404')
        if order.state not in ('draft','sent'):
            return False
        line_id=int(line_id)
        if unlink:
            request.registry.get('purchase.order.line').unlink(request.cr, SUPERUSER_ID, [line_id], context=request.context)
            return False
        number=(remove and -1 or 1)

        order_line_obj = request.registry.get('purchase.order.line')
        order_line_val = order_line_obj.read(request.cr, SUPERUSER_ID, [line_id], [], context=request.context)[0]
        quantity = order_line_val['product_qty'] + number
        order_line_obj.write(request.cr, SUPERUSER_ID, [line_id], {'product_qty': (quantity)}, context=request.context)
        return [str(quantity), str(order.amount_total)]

    @http.route(["/quote_purchase/template/<model('purchase.quote_purchase.template'):quote>"], type='http', auth="user", website=True)
    def template_view(self, quote, **post):
        values = { 'template': quote }
        return request.website.render('website_quote.so_template', values)

    @http.route(["/quote_purchase/add_line/<int:option_id>/<int:order_id>/<token>"], type='http', auth="public", website=True)
    def add(self, option_id, order_id, token, **post):
        vals = {}
        order = request.registry.get('purchase.order').browse(request.cr, SUPERUSER_ID, order_id)
        if token != order.access_token:
            return request.render('website.404')
        if order.state not in ['draft', 'sent']:
            return request.website.render('website.http_error', {'status_code': 'Forbidden', 'status_message': _('You cannot add options to a confirmed order.')})
        option_obj = request.registry.get('purchase.order.option')
        option = option_obj.browse(request.cr, SUPERUSER_ID, option_id)

        res = request.registry.get('purchase.order.line').product_id_change(request.cr, SUPERUSER_ID, order_id,
            False, option.product_id.id, option.quantity, option.uom_id.id, option.quantity, option.uom_id.id,
            option.name, order.partner_id.id, False, True, time.strftime('%Y-%m-%d'),
            False, order.fiscal_position.id, True, dict(request.context or {}, company_id=order.company_id.id))
        vals = res.get('value', {})
        if 'tax_id' in vals:
            vals['tax_id'] = [(6, 0, vals['tax_id'])]

        vals.update({
            'price_unit': option.price_unit,
            'website_description': option.website_description,
            'name': option.name,
            'order_id': order.id,
            'product_id' : option.product_id.id,
            'product_uos_qty': option.quantity,
            'product_uos': option.uom_id.id,
            'product_qty': option.quantity,
            'product_uom': option.uom_id.id,
            'discount': option.discount,
        })
        line = request.registry.get('purchase.order.line').create(request.cr, SUPERUSER_ID, vals, context=request.context)
        option_obj.write(request.cr, SUPERUSER_ID, [option.id], {'line_id': line}, context=request.context)
        return werkzeug.utils.redirect("/quote_purchase/%s/%s#pricing" % (order.id, token))


