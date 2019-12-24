# -*- coding: utf-8 -*-
from werkzeug.exceptions import Forbidden, NotFound

from odoo import models, fields, api, http
from odoo.http import request
from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController



class WebsiteSale(ProductConfiguratorController):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                                         (not order.only_services and (
                                                     mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or def_country_id
        cities = request.env['res.city'].search([])
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            'cities': cities,
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
        }
        return request.render("website_sale.address", render_values)

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
        payment.acquirer. State at this point :

         - a draft sales order with lines; otherwise, clean context / session and
           back to the shop
         - no transaction in context / session, or only a draft one, if the customer
           did go to a payment.acquirer website but closed the tab without
           paying / canceling
        """
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False

        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')

        partner_id = render_values['order'].partner_id
        # 中国，广东省res.city(1137,)，18503, 1232423414, , +1 555-555-5555
        if not partner_id.country_id:
            country_name = ''
        else:
            country_name = partner_id.country_id.name
        if not partner_id.state_id:
            state_name = ''
        else:
            state_name = partner_id.state_id.name
        if not partner_id.city:
            city_name = ''
        else:
            city_name = partner_id.city.name
        if not partner_id.zip:
            zip = ''
        else:
            zip = partner_id.zip
        if not partner_id.street2:
            street1 = ''
        else:
            street1 = partner_id.street2
        if not partner_id.street:
            street2 = ''
        else:
            street2 = partner_id.street
        if not partner_id.phone:
            phone = ''
        else:
            phone = partner_id.phone
        render_values['address_char'] = country_name+'   '+state_name+'   '+city_name+'   '+zip+'   '+street1+'   '+street2+'   '+phone
        return request.render("website_sale.payment", render_values)

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            partner_id = order.partner_id
            if not partner_id.country_id:
                country_name = ''
            else:
                country_name = partner_id.country_id.name
            if not partner_id.state_id:
                state_name = ''
            else:
                state_name = partner_id.state_id.name
            if not partner_id.city:
                city_name = ''
            else:
                city_name = partner_id.city.name
            if not partner_id.zip:
                zip = ''
            else:
                zip = partner_id.zip
            if not partner_id.street2:
                street1 = ''
            else:
                street1 = partner_id.street2
            if not partner_id.street:
                street2 = ''
            else:
                street2 = partner_id.street
            if not partner_id.phone:
                phone = ''
            else:
                phone = partner_id.phone
            address_char = country_name + '   ' + state_name + '   ' + city_name + '   ' + zip + '   ' + street1 + '   ' + street2 + '   ' + phone
            return request.render("website_sale.confirmation", {'order': order,
                                                                'address_char': address_char})
        else:
            return request.redirect('/shop')

from odoo.addons.http_routing.models.ir_http import unslug
from odoo.addons.website.controllers.main import QueryURL
import math
PPG = 20  # Products Per Page
PPR = 4   # Products Per Row

class TableCompute(object):

    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx + x >= PPR:
                    res = False
                    break
                row = self.table.setdefault(posy + y, {})
                if row.setdefault(posx + x) is not None:
                    res = False
                    break
            for x in range(PPR):
                self.table[posy + y].setdefault(x, None)
        return res

    def process(self, products, ppg=PPG):
        # Compute products positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        x = 0
        for p in products:
            x = min(max(p.website_size_x, 1), PPR)
            y = min(max(p.website_size_y, 1), PPR)
            if index >= ppg:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % PPR, pos // PPR, x, y):
                pos += 1
            # if 21st products (index 20) and the last line is full (PPR products in it), break
            # (pos + 1.0) / PPR is the line where the product would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= ppg and ((pos + 1.0) // PPR) > maxy:
                break

            if x == 1 and y == 1:   # simple heuristic for CPU optimization
                minpos = pos // PPR

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos // PPR) + y2][(pos % PPR) + x2] = False
            self.table[pos // PPR][pos % PPR] = {
                'product': p, 'x': x, 'y': y,
                'class': " ".join(x.html_class for x in p.website_style_ids if x.html_class)
            }
            if index <= ppg:
                maxy = max(maxy, y + (pos // PPR))
            index += 1

        # Format table according to HTML needs
        rows = sorted(self.table.items())
        rows = [r[1] for r in rows]
        for col in range(len(rows)):
            cols = sorted(rows[col].items())
            x += len(cols)
            rows[col] = [r[1] for r in cols if r[1]]

        return rows

class OdooWebsiteMarketplace(http.Controller):

    # Seller Page
    @http.route(['/sellers/<seller_id>'], type='http', auth="public", website=True)
    def partners_detail(self , seller_id, page=0 ,ppg=False, **post):
        _, seller_id = unslug(seller_id)

        if seller_id:
            if ppg:
                try:
                    ppg = int(ppg)
                except ValueError:
                    ppg = PPG
                post["ppg"] = ppg
            else:
                ppg = PPG
            partner = request.env['res.partner'].sudo().browse(seller_id)
            if partner.exists():
                url = "/shop"
                keep = QueryURL('/shop')
                Product = request.env['product.template'].with_context(bin_size=True)
                product_count = Product.search_count([('seller_id','=',partner.id),('website_published','=',True)])
                pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
                products = Product.search([('seller_id','=',partner.id),('website_published','=',True)], limit=ppg, offset=pager['offset'])
                total_page = (len(partner.website_message_ids) / 10) + 1
                # partner_id = order.partner_id
                if not partner.country_id:
                    country_name = ''
                else:
                    country_name = partner.country_id.name
                if not partner.state_id:
                    state_name = ''
                else:
                    state_name = partner.state_id.name
                if not partner.city:
                    city_name = ''
                else:
                    city_name = partner.city.name
                if not partner.zip:
                    zip = ''
                else:
                    zip = partner.zip
                if not partner.street2:
                    street1 = ''
                else:
                    street1 = partner.street2
                if not partner.street:
                    street2 = ''
                else:
                    street2 = partner.street
                address_char = country_name + '   ' + state_name + '   ' + city_name + '   ' + zip + '   ' + street1 + '   ' + street2
                # partner['address_char'] = address_char
                values = {
                    'main_object': partner,
                    'partner': partner,
                    'edit_page': False,
                    'products': products,
                    'pager' : pager,
                    'keep' : keep,
                    'bins': TableCompute().process(products, ppg),
                    'rows': PPR,
                    'total_page': math.floor(total_page),
                    'address_char': address_char
                }
                return request.render("odoo_website_marketplace.seller_page", values)
        return request.not_found()