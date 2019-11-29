# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
from odoo import fields, http, tools, _
from odoo.osv import expression
import jinja2
import os

BASE_DIR = os.path.dirname((os.path.dirname(__file__)))
templateLoader = jinja2.FileSystemLoader(searchpath=BASE_DIR + "/static/src")
env = jinja2.Environment(loader=templateLoader)

class cart(http.Controller):
    @http.route('/e2yun_online_shop_extends/get_cart_info', type='http', auth="public", website=True)
    def get_cart_info(self, access_token=None, revive='', **post):
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if order:
            order_line = order.order_line
            line = []
            for ol in order_line:
                line.append({
                    'product_name' : ol.product_id.name,
                    'product_num' : ol.product_uom_qty,
                    'price' : ol.price_unit,
                    'price_total' : (ol.product_uom_qty * ol.price_unit),
                    'product_template_id' : ol.product_id.product_tmpl_id.id,
                    'product_id' : ol.product_id.id,
                    'image_url' : ol.product_id.product_tmpl_id.get_primary_url()
                })
            values = {
                'total_price' : order.amount_total,
                'line' : line
            }

        return request.make_response(json.dumps(values))

    @http.route('/e2yun_online_shop_extends/get_cart_confirm_info', type='http', auth="public", website=True)
    def get_cart_confirm_info(self, access_token=None, revive='', **post):
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if order and order.order_line:
            order_line = order.order_line
            line = []

            partner = order.partner_id
            address = ''

            if partner.country_id and partner.country_id.name:
                address = address + partner.country_id.name

            if partner.state_id and partner.state_id.name:
                address = address + partner.state_id.name

            if partner.city_id and partner.city_id.name:
                address = address + partner.city_id.name

            if partner.area_id and partner.area_id.name:
                address = address + partner.area_id.name

            if partner.street:
                address = address + partner.street



            partner._get_address_format() or ''
            phone = partner.mobile or ''
            total_num = 0



            for ol in order_line:
                line.append({
                    'product_name': ol.product_id.name,
                    'product_num': ol.product_uom_qty,
                    'price': ol.price_unit,
                    'price_total': (ol.product_uom_qty * ol.price_unit),
                    'product_template_id': ol.product_id.product_tmpl_id.id,
                    'product_id': ol.product_id.id,
                    'image_url': ol.product_id.product_tmpl_id.get_primary_url()
                })
                total_num = total_num + ol.product_uom_qty
            values = {
                'total_price': order.amount_total,
                'line': line,
                'address':address,
                'phone' : phone,
                'total_num' : total_num
            }

        return request.make_response(json.dumps(values))

    @http.route('/e2yun_online_shop_extends/get_token', csrf=False,type='http', auth="public")
    def get_token(self,**kwargs):
        return request.make_response(json.dumps({'csrf_token':http.request.csrf_token()}))

    @http.route(['/e2yun_online_shop_extends/add_cart'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )
        return request.make_response(json.dumps({'success':True}))

    @http.route(['/e2yun_online_shop_extends/order_confirm_page'], type='http', auth="public", website=True)
    def order_confirm_page(self, **post):

        sale_order = request.website.sale_get_order()
        if not sale_order or not sale_order.order_line:
            return False

        template = env.get_template('order_confirm.html')
        html = template.render()
        return html

    @http.route(['/e2yun_online_shop_extends/order_confirm'], type='http', auth="public", methods=['POST'], website=True,
                csrf=False)
    def order_confirm(self, phone,address, **kw):
        sale_order = request.website.sale_get_order()
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        if sale_order:
            sale_order.telephone = phone
            sale_order.address = address
            sale_order.state = 'sent'

        return request.make_response(json.dumps({'success': True}))




    def _get_shop_payment_values(self, order, **kwargs):
        shipping_partner_id = False
        if order:
            shipping_partner_id = order.partner_shipping_id.id or order.partner_invoice_id.id

        values = dict(
            website_sale_order=order,
            errors=[],
            partner=order.partner_id.id,
            order=order,
            payment_action_id=request.env.ref('payment.action_payment_acquirer').id,
            return_url='/shop/payment/validate',
            bootstrap_formatting=True
        )

        domain = expression.AND([
            ['&', ('website_published', '=', True), ('company_id', '=', order.company_id.id)],
            ['|', ('website_id', '=', False), ('website_id', '=', request.website.id)],
            ['|', ('specific_countries', '=', False), ('country_ids', 'in', [order.partner_id.country_id.id])]
        ])
        acquirers = request.env['payment.acquirer'].search(domain)

        values['access_token'] = order.access_token
        values['acquirers'] = [acq for acq in acquirers if (acq.payment_flow == 'form' and acq.view_template_id) or
                               (acq.payment_flow == 's2s' and acq.registration_view_template_id)]
        values['tokens'] = request.env['payment.token'].search(
            [('partner_id', '=', order.partner_id.id),
             ('acquirer_id', 'in', acquirers.ids)])

        return values