# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
from odoo import fields, http, tools, _

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

    @http.route('/e2yun_online_shop_extends/get_token', csrf=False,type='http', auth="public")
    def get_token(self,**kwargs):
        return request.make_response(json.dumps({'csrf_token':http.request.csrf_token()}))





        #values['website_sale_order'].order_line
        # if access_token:
        #     abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
        #     if not abandoned_order:  # wrong token (or SO has been deleted)
        #         return request.render('website.404')
        #     if abandoned_order.state != 'draft':  # abandoned cart already finished
        #         values.update({'abandoned_proceed': True})
        #     elif revive == 'squash' or (revive == 'merge' and not request.session[
        #         'sale_order_id']):  # restore old cart or merge with unexistant
        #         request.session['sale_order_id'] = abandoned_order.id
        #         return request.redirect('/shop/cart')
        #     elif revive == 'merge':
        #         abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
        #         abandoned_order.action_cancel()
        #     elif abandoned_order.id != request.session[
        #         'sale_order_id']:  # abandoned cart found, user have to choose what to do
        #         values.update({'access_token': abandoned_order.access_token})

        # if order:
        #     from_currency = order.company_id.currency_id
        #     to_currency = order.pricelist_id.currency_id
        #     compute_currency = lambda price: from_currency._convert(
        #         price, to_currency, request.env.user.company_id, fields.Date.today())
        # else:
        #     compute_currency = lambda price: price
        #
        # values.update({
        #     'website_sale_order': order,
        #     'compute_currency': compute_currency,
        #     'date': fields.Date.today(),
        #     'suggested_products': [],
        # })
        # if order:
        #     _order = order
        #     if not request.env.context.get('pricelist'):
        #         _order = order.with_context(pricelist=order.pricelist_id.id)
        #     values['suggested_products'] = _order._cart_accessories()


        #return request.render("website_sale.cart", values)



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

#     @http.route('/e2yun_online_shop_extends/e2yun_online_shop_extends/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('e2yun_online_shop_extends.listing', {
#             'root': '/e2yun_online_shop_extends/e2yun_online_shop_extends',
#             'objects': http.request.env['e2yun_online_shop_extends.e2yun_online_shop_extends'].search([]),
#         })

#     @http.route('/e2yun_online_shop_extends/e2yun_online_shop_extends/objects/<model("e2yun_online_shop_extends.e2yun_online_shop_extends"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('e2yun_online_shop_extends.object', {
#             'object': obj
#         })