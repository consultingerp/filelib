# -*- coding: utf-8 -*-
from odoo import models, fields, api, http
from odoo.http import request
import jinja2
import os
import json
import logging
from odoo.tools import date_utils

BASE_DIR = os.path.dirname((os.path.dirname(__file__)))
templateLoader = jinja2.FileSystemLoader(searchpath=BASE_DIR + "/static/src")
env = jinja2.Environment(loader=templateLoader)

class order_list(http.Controller):

    @http.route('/hhjc_shop_order_list', type='http', auth="public", methods=['GET'])
    def hhjc_shop_order_list(self, **kwargs):
        if request.params.get('show_view_id',False):
            show_view_id = request.params.get('show_view_id')
            request.session['show_view_id'] = show_view_id
        else:
            request.session['show_view_id'] = False

        template = env.get_template('order_list.html')
        html = template.render()
        return html

    @http.route('/e2yun_sale_online_shop_extends/get_order_list', type='http', auth="public", website=True)
    def get_order_list(self, access_token=None, revive='', **post):
        datas = []
        orders = []
        search_key = request.params.get('search_key', False)
        if search_key:
            orders = request.env['sale.order'].sudo().search([('partner_id','=',request.env.user.partner_id.id),'|',('order_line.product_id', 'ilike',search_key ),('name', 'ilike',search_key )])#('state','!=','draft'),
        else:
            orders = request.env['sale.order'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])  # ('state','!=','draft'),
        for order in orders:

            data = {
                'order_name':order.name,
                'order_date':order.date_order,
                'order_state':order.crmstate,
                'order_team':'',
                'order_address':order.address or '',
                'order_phone':order.telephone or '',
                'order_price' : order.amount_total,
                'order_id' : order.id
            }

            if order.team_id and order.team_id.name:
                data['order_team'] = order.team_id.name
            lines = []
            total_num = 0
            for line in order.order_line:
                lines.append({
                    'line_name' : line.name,
                    'line_qty' : line.product_uom_qty,
                    'line_delivered_qty' : line.qty_delivered,
                    'line_prict': line.price_unit,
                    'image_url': line.product_id.product_tmpl_id.get_primary_url()
                })

                total_num = total_num + line.product_uom_qty
            data['order_line'] = lines
            data['total_num'] = total_num
            datas.append(data)

        if request.session.get('show_view_id',False):
            if datas and len(datas) > 0:
                datas[0]['show_view_id'] = request.session.get('show_view_id')

        return request.make_response(json.dumps(datas, default=date_utils.json_default))

    @http.route('/order_detail_page/<int:order_id>', type='http', auth='public', website=True)
    def order_detail_page(self, order_id, **kwargs):
        request.session['detail_order_id'] = order_id
        template = env.get_template('order_detail.html')
        html = template.render()
        return html

    @http.route('/e2yun_sale_online_shop_extends/get_order_detail_data', type='http', auth="public", website=True)
    def get_order_detail_data(self, access_token=None, revive='', **post):
        datas = {}
        line = []
        if request.session.get('detail_order_id',False):
            detail_order_id = request.session.get('detail_order_id')
            orders = request.env['sale.order.crmstate.flow'].sudo().search(
                [('order_id', '=', detail_order_id)],order='create_date desc')

            if orders:
                datas['order_name'] = orders[0].order_id.name

            for order in orders:
                line.append({
                    'state': order.crmstate,
                    'date': order.create_date,
                })
        datas['line'] = line
        return request.make_response(json.dumps(datas, default=date_utils.json_default))
