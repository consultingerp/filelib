# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
from odoo import fields, http, tools, _
from ..controllers import user_info
from odoo.osv import expression
import jinja2
import os
import  logging

BASE_DIR = os.path.dirname((os.path.dirname(__file__)))
templateLoader = jinja2.FileSystemLoader(searchpath=BASE_DIR + "/static/src")
env = jinja2.Environment(loader=templateLoader)

_logger = logging.getLogger(__name__)

class cart(user_info.WebUserInfoController):
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

    @http.route(['/e2yun_online_shop_extends/ger_cart_qty'], type='http', auth="public", methods=['POST'], website=True,csrf=False)
    def ger_cart_qty(self,**kw):
        sale_order = request.website.sale_get_order(force_create=False)
        cart_qty = 0
        if sale_order.state == 'draft':
            cart_qty = len(sale_order.order_line)

        return request.make_response(json.dumps({'cart_qty': cart_qty}))

    @http.route(['/e2yun_online_shop_extends/add_cart'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """This route is called when adding a product to cart (no options)."""

        if not request.session.usronlineinfo:
            request.session.usronlineinfo = self.get_show_userinfo()
        usronlineinfo = request.session.usronlineinfo

        pricelist_name = ''
        region = usronlineinfo.get('region', False)
        if region and region == '北京':
            pricelist_name = '北京订单价格表'
        if region and region == '深圳':
            pricelist_name = '深圳订单价格表'
        pricelist = request.env['product.pricelist'].sudo().search([('name', '=', pricelist_name)])

        sale_order = request.website.sale_get_order(force_create=False)

        if not sale_order or sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True,force_pricelist=pricelist.id)
            # 设置公司为当前位置对应公司
            if sale_order.company_id.id != usronlineinfo['company_id']:
                sale_order.company_id = usronlineinfo['company_id']

        if sale_order.user_id and not sale_order.team_id:
            team_user = request.env['res.users'].sudo().search([('id','=',sale_order.user_id.id)])
            sale_order.team_id = team_user.sale_team_id.id

            # request.env['crm.team'].sudo().search([('')])

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

    @http.route('/e2yun_online_shop_extends/get_order_done_info', type='http', auth="public", website=True)
    def get_order_done_info(self, access_token=None, revive='', **post):
        confirm_sale_order_id = request.session['confirm_sale_order_id']
        values = {}
        if confirm_sale_order_id:
            order = request.env['sale.order'].sudo().browse(confirm_sale_order_id)
            values = {
                'total_price': order.amount_total,
                'order_code': order.name,
                'order_id' : order.id
            }

        return request.make_response(json.dumps(values))

    @http.route(['/e2yun_online_shop_extends/order_done_page'], type='http', auth="public", website=True)
    def order_done_page(self, **post):

        template = env.get_template('order_done.html')
        html = template.render()
        return html

    @http.route(['/e2yun_online_shop_extends/order_confirm'], type='http', auth="public", methods=['POST'], website=True,
                csrf=False)
    def order_confirm(self, phone,address,coupon, **kw):
        sale_order = request.website.sale_get_order()

        if sale_order:
            if not request.session.usronlineinfo:
                request.session.usronlineinfo = self.get_show_userinfo(refresh=True)
            company_id = request.session.usronlineinfo['company_id']
            website = request.env['website'].sudo().search([('company_id', '=', company_id)], limit=1)
            if website:
                sale_order.website_id = website.id
                sale_order.company_id = company_id
            _logger.info("订单公司代码%s" % sale_order.company_id)
            _logger.info("订单网站到%s" % website.id)


            if coupon:
                coupon_status = request.env['sale.coupon.apply.code'].sudo().apply_coupon(sale_order, coupon)
                if coupon_status.get('error'):
                    return request.make_response(json.dumps({'success': False}))

            sale_order.telephone = phone
            sale_order.address = address
            sale_order.state = 'sent'


            request.session['confirm_sale_order_id'] = sale_order.id

        return request.make_response(json.dumps({'success': True}))


    @http.route('/e2yun_online_shop_extends/get_coupon', type='http', auth="public", website=True)
    def get_coupon(self, access_token=None, revive='', **post):
        datas = []
        coupos = request.env['sale.coupon'].search(
            [('state', '=', 'new'), ('partner_id', '=', request.env.user.partner_id.id)])
        for coupo in coupos:

            data = {
                'coupo_name': coupo.program_id.name,
                'coupo_code': coupo.code
            }

            datas.append(data)

        return request.make_response(json.dumps(datas))
