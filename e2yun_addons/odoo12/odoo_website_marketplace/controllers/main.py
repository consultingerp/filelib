# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import json
import math
import logging
from werkzeug.exceptions import Forbidden

from odoo import http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
#from odoo.addons.website.models.website import slug,unslug
from odoo.addons.http_routing.models.ir_http import slugify, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.auth_signup.models.res_partner import SignupError
from odoo.addons.auth_signup.models.res_users import ResUsers      # Registration type return

from odoo.addons.website_sale.controllers.main import WebsiteSale
import werkzeug.urls
import werkzeug.wrappers
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home  # add library for Registration page

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
                values = {
                    'main_object': partner,
                    'partner': partner,
                    'edit_page': False,
                    'products': products,
                    'pager' : pager,
                    'keep' : keep,
                    'bins': TableCompute().process(products, ppg),
                    'rows': PPR,
                    'total_page' : math.floor(total_page)
                }

                return request.render("odoo_website_marketplace.seller_page", values)
        return request.not_found()



    # Seller Page
    @http.route(['/marketplace'], type='http', auth='user', website=True)
    def marketplace(self, redirect=None, **post):
        user_brw = request.env['res.users'].sudo().browse(request.session.uid).groups_id
        group_id = [a.id for a in user_brw]
        
        seller_pending_user = user_brw.env.ref('odoo_website_marketplace.group_market_place_pending_seller')
        seller_account_user = user_brw.env.ref('odoo_website_marketplace.group_market_place_seller')
        seller_manager_user = user_brw.env.ref('odoo_website_marketplace.group_market_place_manager')
        menu_brw = False
        if (seller_manager_user.id in group_id) or (seller_account_user.id in group_id) or (seller_pending_user.id in group_id):
            menu_id = request.env['ir.ui.menu'].search([('name', '=','Seller Dashboard')],limit=1)
            menu_brw = request.env['ir.ui.menu'].browse(menu_id.id)

        market = '/web#menu_id=' + str(menu_brw.id)

        return werkzeug.utils.redirect(market, 303)


    # Seller Menu
    @http.route(['/seller'], type='http', auth="public", website=True)
    def seller(self, page=0, category=None, search='', **post):
        return request.render("odoo_website_marketplace.seller")


    # Reviews & Rating
    """ This method is overloaded for to add messaege_rate and short_description
    in product.template"""
    @http.route(['/sellers/comment/<int:seller_id>'], type='http', auth="public", methods=['POST'], website=True)
    def seller_rating( self, seller_id, **post ):
        if post.get('comment'):
            user_id =request.env['res.users'].search([('partner_id','=',seller_id)],limit=1)
            partner_id = request.env['res.partner'].browse(seller_id)
            message_id1 = partner_id.sudo().message_post(
                body=post.get('comment'),
                message_type='comment',
                subtype='mail.mt_comment')  # mail_create_nosubcribe=True
            
            message_id1.body = post.get( 'comment' )
            message_id1.type = 'comment'
            message_id1.subtype = 'mt_comment'
            message_id1.model = 'res.partner'
            message_id1.res_id = seller_id
            
            review = post.get( 'review', 0 )
            short_description = post.get( 'short_description' )
            
            val = {'message_rate':review, 'short_description':short_description, 'website_message':True, }
            message_id1.sudo().write(val)
            
            # seller review 
            seller_review = request.env['seller.review']
            res_partner_obj = request.env['res.partner'].sudo().browse(seller_id)
            #res_user_obj = request.env['res.users'].search([('id', '=',res_partner_obj.user_id.id)])
            # if res_partner_obj:
            
            res_user_obj = request.env['res.users'].sudo().search([('id', '=',res_partner_obj.user_id.id)])
            
            if res_user_obj:
                res_user_obj = res_user_obj.id
            else:
                res_user_obj = request.session.uid
            
            vals = {
                'name' : post['comment'],
                'seller_id' : res_user_obj,
                'rating_msg' : short_description,
                'rating_num' : review,
            }
            seller_review_create = seller_review.sudo().create(vals)
            
            return werkzeug.utils.redirect( request.httprequest.referrer + "#comments" )

    
    @http.route(['/seller/signup'], type='http', auth="public", website=True)
    def seller_signup(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.env
        return request.render("odoo_website_marketplace.seller_signup")


    @http.route(['/seller/signup/thanks'], type='http', auth="public", website=True)
    def seller_thank_you(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.env

        if post:
            name = post['name']
            shop_name = post['shopname']
            # url = post['url']
            password = post['password2']
            confirm_password = post['password3']
            email = post['email']
            tag_line = post['tagline']

            user_ids = request.env['res.users'].sudo().search([])
            email_list = []
            for user in user_ids:
                email_list.append(user.login)

            for mail in email_list:
                if email in email_list:
                    return request.redirect('/seller/signup?email_msg=%s' % _('Email is Already Used.'))

            partner_obj = request.env['res.partner']
            user_obj = request.env['res.users']
            
            part_vals = {
                'name' : str(name),
                'shop_name' : str(shop_name),
                'email' : str(email),
                'seller' : True,
                'tag_line' : str(tag_line),
                'password' : str(confirm_password),
            }
            
            partner = partner_obj.sudo().create(part_vals)
            
            pending_seller_id = request.env['ir.model.data'].sudo().get_object_reference('odoo_website_marketplace','group_market_place_pending_seller')[1]

            group_list = []
            group_list.append(pending_seller_id)

            user_vals = {
                'email': str(email),
                'login': str(email),
                'password' : str(confirm_password),
                'partner_id': partner.id,
                'groups_id': [(6, 0, group_list)],
            }

            users = user_obj.sudo().create(user_vals)

            
            partner.write({'seller_id':users.id, 'user_id':users.id, 'website_true' : True})

            template_id = request.env['ir.model.data'].get_object_reference('odoo_website_marketplace','email_template_marketplace')[1]

            mananger_seller_id = request.env['ir.model.data'].sudo().get_object_reference('odoo_website_marketplace','group_market_place_manager')[1]

            group_manager = request.env['res.groups'].sudo().browse(mananger_seller_id)

            manager = None
            if group_manager.users:
                manager = group_manager.users[0]

                template_id = request.env['ir.model.data'].sudo().get_object_reference('odoo_website_marketplace', 'email_template_signup_seller_email')[1]
                email_template_obj = request.env['mail.template'].sudo().browse(template_id)
                values = email_template_obj.sudo().generate_email(partner.id)
                values['email_from'] = manager.sudo().partner_id.email
                values['email_to'] = str(email)
                values['res_id'] = partner.id
                values['body_html'] = """
                        <p>Dear %s</p>
                        <p> We Receive your request as a Seller</p>
                        <p> Thank You for being part of us.</p>
                        <br/>
                        <p>Here is your login details </p>
                        <table style="border 1px solid black">
                            <tr>
                                <td>Login</td>
                                <td>%s</td>
                            </tr>
                            <tr>
                                <td>Password</td>
                                <td>%s</td>
                            </tr>
                        </table>
                    """ % (str(name),str(email),str(confirm_password))

                mail_mail_obj = request.env['mail.mail']
                msg_id = mail_mail_obj.sudo().create(values)
                if msg_id:
                    mail_mail_obj.sudo().send([msg_id])

            return request.render("odoo_website_marketplace.seller_thank_you")
        else:
            return request.render("odoo_website_marketplace.seller_signup")
