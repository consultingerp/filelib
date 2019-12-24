# -*- coding: utf-8 -*-

from odoo import models, fields, api, http
from odoo.tools import date_utils
import jinja2
import os
import logging
import json
from ..controllers import user_info
from odoo.http import request
import werkzeug
import numpy as np

BASE_DIR = os.path.dirname((os.path.dirname(__file__)))
templateLoader = jinja2.FileSystemLoader(searchpath=BASE_DIR + "/static/src")
env = jinja2.Environment(loader=templateLoader)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


class OnlineShop(user_info.WebUserInfoController):

    @http.route('/hhjc_shop_index', type='http', auth="public", methods=['GET'])
    def hhjc_shop_index(self, **kwargs):
        # env = http.request.env
        template = env.get_template('index.html')
        if not request.session.usronlineinfo:
            request.session.usronlineinfo = self.get_show_userinfo()
        html = template.render()
        return html

    @http.route('/hhjc_shop_product_list', type='http', auth="public", methods=['GET'])
    def hhjc_shop_product_list(self, **kwargs):
        # env = http.request.env
        if not request.session.usronlineinfo:
            request.session.usronlineinfo = self.get_show_userinfo()
        request.session['default_product_category'] = ''
        template = env.get_template('shop-list-sidebar.html')
        html = template.render()
        return html

    @http.route('/hhjc_shop_product_list_page/<int:product_category>', type='http', auth="user")
    def hhjc_shop_product_list_page(self, product_category, **kwargs):
        if request.session.uid:
            if product_category:
                request.session['default_product_category'] = product_category
            template = env.get_template('shop-list-sidebar.html')
            html = template.render()
            return html
        query = werkzeug.urls.url_encode({
            'redirect': '/hhjc_shop_product_list_page/' + str(product_category),
            'error': '请登录然后操作'
        })
        return werkzeug.utils.redirect('/web/login?%s' % query)

    @http.route(['/online_shop/get_default_product_category'], type='http', auth="public")
    def get_default_product_category(self, **kwargs):
        default_product_category = request.session['default_product_category']
        return http.request.make_response(json.dumps({'default_product_category': default_product_category}))

    @http.route('/hhjc_shop_product_details', type='http', auth="public", methods=['GET'])
    def hhjc_shop_product_details(self, **kwargs):
        template = env.get_template('product-details.html')
        html = template.render()
        request.session['current_product_detail_id'] = ''
        return html

    # 如果想要不登录就可以访问，那么auth='public'
    @http.route('/test', type='http', auth='user', csrf=False)
    def test_test(self, **kwargs):
        # env = http.request.env
        template = env.get_template('index_test.html')
        html = template.render()
        return html

    @http.route('/test_get', type='http', auth="public", methods=['GET'])
    def test_get(self, **kwargs):
        params = http.request.params
        text = """
                <p>Ajax 的全称是 Asynchronous JavaScript and XML（异步的 JavaScript 和 XML），是一种用于创建动态网页的技术。</p>
                <p>Ajax 技术指的是脚本独立向服务器请求数据，拿到数据以后，进行处理并更新网页。</p>
                """
        return http.Response(text)

    @http.route('/online_shop/get_category', type='http', auth="public", methods=['GET'])
    def online_shop_get_category(self, **kwargs):
        text = ""
        html_head = """<li>
                            <a id='shop_category_99999' onclick='show_goods_in_category(this)'>所有类别</a>
                        </li>"""
        text = text + html_head
        category_parent_pool = http.request.env['product.public.category'].search([('parent_id', '=', False)])
        i = 0
        for category_parent in category_parent_pool:
            if i == 0:
                html_start = """<li class="menu-item-has-children active">"""
                html_start_2 = "<a id='shop_category_" + str(
                    category_parent.id) + "' onclick='show_goods_in_category(this)'>" + category_parent.name + "</a>"
                html_start_3 = """<span class="menu-expand"><i class="la la-angle-down"></i></span>"""
                html_start_4 = """<ul class="sub-menu" style="display: none;">"""
                html_body = ""
                category_child_pool = http.request.env['product.public.category'].search(
                    [('parent_id', '!=', False), ('parent_id', '=', category_parent.id)])
                for category_child in category_child_pool:
                    category_child_products = http.request.env['product.template'].search(
                        [('public_categ_ids', 'in', category_child.id)])
                    if category_child_products:
                        html_to_add = "<li><a id='shop_category_" + str(
                            category_child.id) + "' onclick='show_goods_in_category(this)'>" + category_child.name + "</a></li>"
                        html_body = html_body + html_to_add
                    else:
                        continue
                html_end = """</ul></li>"""
                category_parent_html = html_start + html_start_2 + html_start_3 + html_start_4 + html_body + html_end
                text = text + category_parent_html
                i = i + 1
            else:
                html_start = """<li class="menu-item-has-children">"""
                html_start_2 = "<a id='shop_category_" + str(
                    category_parent.id) + "' onclick='show_goods_in_category(this)'>" + category_parent.name + "</a>"
                html_start_3 = """<span class="menu-expand"><i class="la la-angle-down"></i></span>"""
                html_start_4 = """<ul class="sub-menu" style="display: none;">"""
                html_body = ""
                category_child_pool = http.request.env['product.public.category'].search(
                    [('parent_id', '!=', False), ('parent_id', '=', category_parent.id)])
                for category_child in category_child_pool:
                    category_child_products = http.request.env['product.template'].search([('public_categ_ids', 'in', category_child.id)])
                    if category_child_products:
                        html_to_add = "<li><a id='shop_category_" + str(
                            category_child.id) + "' onclick='show_goods_in_category(this)'>" + category_child.name + "</a></li>"
                        html_body = html_body + html_to_add
                    else:
                        continue
                html_end = """</ul></li>"""
                category_parent_html = html_start + html_start_2 + html_start_3 + html_start_4 + html_body + html_end
                text = text + category_parent_html
                i = i + 1

        return http.Response(text)
        # # 后面需要考虑母类别和子类别
        # # <p id="" onclick="xxxxx">xxxx</p>
        # text = " <p id='shop_category_99999' onclick='show_goods_in_category(this)'>所有类别</p>"
        # for category in category_pool:
        #     text = text + "<p id='shop_category_" + str(category.id) + "' onclick='show_goods_in_category(this)'>" + category.name + "</p>"
        # header_text = """
        # <div class="col-xl-3 col-lg-4 order-lg-1" id="left_category_chooser">
        #                     <aside class="shop-sidebar">
        #                         <div class="shop-widget mb--40">
        #                             <h3 class="widget-title mb--25">Category</h3>
        #                             <ul class="widget-list category-list">
        # """
        # footer_text = """
        #             </ul>
        #                                 </div>
        #                             </aside>
        #                             </div>"""
        # body_text = """
        # <li>
        #                                     <a id="shop_category_99999" onclick='show_goods_in_category(this)'>
        #                                         <span class="category-title">所有类别</span>
        #                                         <i class="fa fa-angle-double-right"></i>
        #                                     </a>
        #                                 </li>
        # """
        # for category in category_pool:
        #     add_text = """
        #     <li>
        #                                     <a id="shop_category_""" + str(category.id) + """"  onclick='show_goods_in_category(this)'>
        #     <span class="category-title">""" + category.name + """
        #     </span>
        #                                         <i class="fa fa-angle-double-right"></i>
        #                                     </a>
        #                                 </li>
        #     """
        #     body_text = body_text + add_text
        # text = header_text + body_text + footer_text

    @http.route(['/online_shop/get_product_list_by_category/<int:category_id>'], type='http', auth="public")
    def get_product_list_by_category(self, category_id, **kwargs):
        product_template_pool = http.request.env['product.template']
        # response_text = """<p>地区显示测试</p>"""
        response_text = """"""
        current_session = request.session
        if category_id == 99999:
            # product_pool = http.request.env['product.product'].search([('id', 'in', [45])])
            product_template_pool = http.request.env['product.template'].search([('sale_ok', '=', True)])
        else:
            product_template_pool = http.request.env['product.template'].search([('sale_ok', '=', True),
                                                                                 '|',
                                                                                 ('public_categ_ids', 'in', category_id),
                                                                                 ('category_parents', 'in', category_id)])
            for product_template in product_template_pool:
                cp = product_template.category_parents
                message = cp.ids
                logging.warning(message)
            # product_template_pool = http.request.env['product.template'].search([('sale_ok', '=', True), ('public_categ_ids', 'in', category_id)])
        for product_template in product_template_pool:
            # str_list = [str(product.id), str(product.default_code), str(product.name)]
            # str_join = ''.join(str_list)
            if product_template.id:
                # 获取产品价格（所有变体中价格最低的）
                product_template_price_float = product_template.list_price

                # product_product_pool = http.request.env['product.product'].search([('product_tmpl_id', '=', product_template.id)])
                # if product_product_pool:
                #     product_product_price_list = []
                #     for product_product in product_product_pool:
                #         if product_product.lst_price:
                #             product_product_price_list.append(product_product.lst_price)
                #     if product_product_price_list:
                #         product_template_price_float = min(product_product_price_list)

                # TODO: 产品图片获取
                def get_product_image(product_tmpl_id):
                    product_template_image_object = http.request.env['product.image.ext'].search([('product_tmpl_id', '=', product_tmpl_id), ('is_primary', '=', True)], limit=1)
                    if product_template_image_object:
                        return product_template_image_object.image_path
                    else:
                        product_template_image_object = http.request.env['product.image.ext'].search([('product_tmpl_id', '=', product_tmpl_id)], order='order_sort asc', limit=1)
                        if product_template_image_object:
                            return product_template_image_object.image_path
                        else:
                            return "/e2yun_online_shop_extends/static/src/assets/img/products/prod-04-270x300.jpg"

                product_template_image = get_product_image(product_template.id)

                # product_template_image = "/e2yun_online_shop_extends/static/src/assets/img/products/prod-04-270x300.jpg"
                # onclick='grid_image_show_product_template_detail_page(this)'
                # onclick='grid_tittle_show_product_template_detail_page(this)'
                # onclick='list_image_show_product_template_detail_page(this)'
                # onclick='list_tittle_show_product_template_detail_page(this)'
                grid_image_product_detail_id = "grid_image_shop_product_template_" + str(product_template.id)
                grid_tittle_product_detail_id = "grid_tittle_shop_product_template_" + str(product_template.id)
                list_image_product_detail_id = "list_image_shop_product_template_" + str(product_template.id)
                list_tittle_product_detail_id = "list_tittle_shop_product_template_" + str(product_template.id)
                # TODO:等待测试后删除
                product_detail_href = ''
                product_template_name = product_template.name
                product_add_to_cart_href = "cart.html"
                product_template_price_str = "¥" + str(product_template_price_float)
                # TODO:是否需要增加产品描述字段
                if product_template.description_sale:
                    product_template_description = product_template.description_sale
                else:
                    product_template_description = ''
                # TODO:是否添加一个字段，控制产品是否展示到在线商城

                text = """
                <div class="col-xl-4 col-sm-6 mb--50">
    <!--TODO：Grid模式-->
    <div class="ft-product">
        <div class="product-inner">
            <div class="product-image">
                <figure class="product-image--holder">
                    <img src='/""" + product_template_image + """' alt="Product">
                </figure>
                <a id='""" + grid_image_product_detail_id + """' onclick='grid_image_show_product_template_detail_page(this)' class="product-overlay"></a>
                <div class="product-action"></div>
            </div>
            <div class="product-info">
                <h3 class="product-title"><a id='""" + grid_tittle_product_detail_id + """' onclick='grid_tittle_show_product_template_detail_page(this)'>""" + product_template_name + """</a></h3>
                <div class="product-info-bottom">
                    <div class="product-price-wrapper">
                        <span class="money">""" + product_template_price_str + """</span><p>浏览量 """ + str(product_template.browse_num) + """</p><p>销量 """ + str(product_template.so_qty) + """</p>
                    </div>
                    <a href='/""" + product_add_to_cart_href + """' class="add-to-cart pr--15">
                        <i class="la la-plus"></i>
                        <span>添加到购物车</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
    <!--TODO：列表模式-->
    <div class="ft-product-list">
        <div class="product-inner">
            <figure class="product-image">
                <a id='""" + list_image_product_detail_id + """"' onclick='list_image_show_product_template_detail_page(this)'>
                    <img src='/""" + product_template_image + """' alt="Products">
                </a>
                <div class="product-thumbnail-action">
                </div>
            </figure>
            <div class="product-info">
                <h3 class="product-title mb--25">
                    <a id='""" + list_tittle_product_detail_id + """' onclick='list_tittle_show_product_template_detail_page(this)'>""" + product_template_name + """</a>
                </h3>
                <div class="product-price-wrapper mb--15 mb-sm--10">
                    <span class="money">""" + product_template_price_str + """</span><p>浏览量 """ + str(product_template.browse_num) + """</p><p>销量 """ + str(product_template.so_qty) + """</p>
                </div>
                <p class="product-short-description mb--20">""" + product_template_description + """</p>  
                <div class="ft-product-action-list d-flex align-items-center">
                    <input type='hidden' name='product_id' value='""" + str(product_template.product_variant_ids[0].id) + """'/>
                    <input type='hidden' name='product_template_id' value='""" + str(product_template.id) + """'/>
                    <!-- <input type='hidden' name='csrf_token' value='""" + http.request.csrf_token() + """'/>
                     <a href='/""" + product_add_to_cart_href + """' class="btn btn-size-md">添加到购物车</a> -->
                    <a href='javascript:;' class="list_btn_add_cart btn btn-size-md">添加到购物车</a>
                </div>                                            
            </div>
        </div>
    </div>
</div>"""
                response_text = response_text + text
                # product_str = "" + str(product_template.id) + ' ' + str(product_template.default_code) + ' ' + str(product_template.name)
                # text = text + "<p id='shop_product_product_" + str(product_template.id) + "' onclick='show_product_details(this)'>" + product_str + "</p>"
        return http.Response(response_text)

    @http.route(['/online_shop/search_product_list/<string:search_key>'], type='http', auth="public")
    def search_product_list(self, search_key, **kwargs):
        response_text = """"""
        product_template_pool = http.request.env['product.template'].search([('sale_ok', '=', True), ('name', 'ilike', search_key)], order='custom_order asc')
        for product_template in product_template_pool:
            # str_list = [str(product.id), str(product.default_code), str(product.name)]
            # str_join = ''.join(str_list)
            if product_template.id:
                # 获取产品价格（所有变体中价格最低的）
                product_template_price_float = product_template.list_price

                # product_product_pool = http.request.env['product.product'].search(
                #     [('product_tmpl_id', '=', product_template.id)])
                # if product_product_pool:
                #     product_product_price_list = []
                #     for product_product in product_product_pool:
                #         if product_product.lst_price:
                #             product_product_price_list.append(product_product.lst_price)
                #     if product_product_price_list:
                #         product_template_price_float = min(product_product_price_list)

                # TODO: 产品图片获取
                def get_product_image(product_tmpl_id):
                    product_template_image_object = http.request.env['product.image.ext'].search(
                        [('product_tmpl_id', '=', product_tmpl_id), ('is_primary', '=', True)], limit=1)
                    if product_template_image_object:
                        return product_template_image_object.image_path
                    else:
                        product_template_image_object = http.request.env['product.image.ext'].search(
                            [('product_tmpl_id', '=', product_tmpl_id)], order='order_sort asc', limit=1)
                        if product_template_image_object:
                            return product_template_image_object.image_path
                        else:
                            return "/e2yun_online_shop_extends/static/src/assets/img/products/prod-04-270x300.jpg"

                product_template_image = get_product_image(product_template.id)

                # product_template_image = "/e2yun_online_shop_extends/static/src/assets/img/products/prod-04-270x300.jpg"
                # onclick='grid_image_show_product_template_detail_page(this)'
                # onclick='grid_tittle_show_product_template_detail_page(this)'
                # onclick='list_image_show_product_template_detail_page(this)'
                # onclick='list_tittle_show_product_template_detail_page(this)'
                grid_image_product_detail_id = "grid_image_shop_product_template_" + str(product_template.id)
                grid_tittle_product_detail_id = "grid_tittle_shop_product_template_" + str(product_template.id)
                list_image_product_detail_id = "list_image_shop_product_template_" + str(product_template.id)
                list_tittle_product_detail_id = "list_tittle_shop_product_template_" + str(product_template.id)
                # TODO:等待测试后删除
                product_detail_href = ''
                product_template_name = product_template.name
                product_add_to_cart_href = "cart.html"
                product_template_price_str = "¥" + str(product_template_price_float)
                # TODO:是否需要增加产品描述字段
                if product_template.description_sale:
                    product_template_description = product_template.description_sale
                else:
                    product_template_description = ''
                # TODO:是否添加一个字段，控制产品是否展示到在线商城

                text = """
                               <div class="col-xl-4 col-sm-6 mb--50">
                   <!--TODO：Grid模式-->
                   <div class="ft-product">
                       <div class="product-inner">
                           <div class="product-image">
                               <figure class="product-image--holder">
                                   <img src='/""" + product_template_image + """' alt="Product">
                               </figure>
                               <a id='""" + grid_image_product_detail_id + """' onclick='grid_image_show_product_template_detail_page(this)' class="product-overlay"></a>
                               <div class="product-action"></div>
                           </div>
                           <div class="product-info">
                               <h3 class="product-title"><a id='""" + grid_tittle_product_detail_id + """' onclick='grid_tittle_show_product_template_detail_page(this)'>""" + product_template_name + """</a></h3>
                               <div class="product-info-bottom">
                                   <div class="product-price-wrapper">
                                       <span class="money">""" + product_template_price_str + """</span>
                                   </div>
                                   <a href='/""" + product_add_to_cart_href + """' class="add-to-cart pr--15">
                                       <i class="la la-plus"></i>
                                       <span>添加到购物车</span>
                                   </a>
                               </div>
                           </div>
                       </div>
                   </div>
                   <!--TODO：列表模式-->
                   <div class="ft-product-list">
                       <div class="product-inner">
                           <figure class="product-image">
                               <a id='""" + list_image_product_detail_id + """"' onclick='list_image_show_product_template_detail_page(this)'>
                                   <img src='/""" + product_template_image + """' alt="Products">
                               </a>
                               <div class="product-thumbnail-action">
                               </div>
                           </figure>
                           <div class="product-info">
                               <h3 class="product-title mb--25">
                                   <a id='""" + list_tittle_product_detail_id + """' onclick='list_tittle_show_product_template_detail_page(this)'>""" + product_template_name + """</a>
                               </h3>
                               <div class="product-price-wrapper mb--15 mb-sm--10">
                                   <span class="money">""" + product_template_price_str + """</span>
                               </div>
                               <p class="product-short-description mb--20">""" + product_template_description + """</p>  
                               <div class="ft-product-action-list d-flex align-items-center">
                                   <input type='hidden' name='product_id' value='""" + str(
                    product_template.product_variant_ids[0].id) + """'/>
                                   <input type='hidden' name='product_template_id' value='""" + str(
                    product_template.id) + """'/>
                                   <!-- <input type='hidden' name='csrf_token' value='""" + http.request.csrf_token() + """'/>
                                    <a href='/""" + product_add_to_cart_href + """' class="btn btn-size-md">添加到购物车</a> -->
                                   <a href='javascript:;' class="list_btn_add_cart btn btn-size-md">添加到购物车</a>
                               </div>                                            
                           </div>
                       </div>
                   </div>
               </div>"""
                response_text = response_text + text
                # product_str = "" + str(product_template.id) + ' ' + str(product_template.default_code) + ' ' + str(product_template.name)
                # text = text + "<p id='shop_product_product_" + str(product_template.id) + "' onclick='show_product_details(this)'>" + product_str + "</p>"
        return http.Response(response_text)

    @http.route(['/online_shop/sort_product_list/<int:current_category_id>/<int:chooser_id>'])
    def sort_product_list(self, current_category_id, chooser_id, **kwargs):
        """
        <option value="0">默认排序</option>
        <option value="1">名称升序</option>
        <option value="2">名称降序</option>
        <option value="3">价格升序</option>
        <option value="4">价格降序</option>
        <option value="5">销售数量升序</option>
        <option value="6">销售数量降序</option>
        <option value="7">浏览量升序</option>
        <option value="8">浏览量降序</option>
        <option value="9">上架时间升序</option>
        <option value="10">上架时间降序</option>

        """
        # 刷新按名称排序的次序
        replace_view_sql = """
        CREATE OR REPLACE VIEW product_template_order_view AS (
        SELECT ROW_NUMBER() OVER(ORDER BY convert_to(LOWER(name),'GB18030')),id from product_template
        );
        """
        reset_sequence_sql = """
        update product_template 
        set product_template_order_by_name = product_template_order_view.row_number 
        from product_template_order_view  
        where product_template.id = product_template_order_view.id;
        """
        http.request.env.cr.execute(replace_view_sql)
        http.request.env.cr.execute(reset_sequence_sql)

        if not request.session.usronlineinfo:  # 如果没有地区获取地区
            request.session.usronlineinfo = self.get_show_userinfo()
            request.session.usronlineinfo['chooser_id'] = chooser_id  # 设置用户排序方式放到sesion中
        else:  # 如果 有session存
            request.session.usronlineinfo['chooser_id'] = chooser_id  # 设置用户排序方式放到sesion中

        order = {
            0: 'custom_order asc',
            1: 'product_template_order_by_name asc',
            2: 'product_template_order_by_name desc',
            3: 'list_price asc',
            4: 'list_price desc',
            5: 'so_qty asc',
            6: 'so_qty desc',
            7: 'browse_num asc',
            8: 'browse_num desc',
            9: 'prefer_date asc',
            10: 'prefer_date desc',
        }
        product_template_pool = http.request.env['product.template']
        response_text = """"""
        domain = []
        area_id = None
        if request.params.get('area_id'):  # 如果查地区
            area_id = request.params['area_id']
            if area_id != '-1':
                domain = [('pc_show_id.company_id.id', '=', area_id)]
        order_text = order[chooser_id]
        if current_category_id == 99999:
            # product_pool = http.request.env['product.product'].search([('id', 'in', [45])])
            domain = domain + [('sale_ok', '=', True)]
            product_template_pool = http.request.env['product.template'].search(domain, order=order_text)
        else:
            domain = domain + [('sale_ok', '=', True),
                               '|',
                               ('public_categ_ids', 'in', current_category_id),
                               ('category_parents', 'in', current_category_id)]
            product_template_pool = http.request.env['product.template'].search(domain, order=order_text)
        for product_template in product_template_pool:
            # str_list = [str(product.id), str(product.default_code), str(product.name)]
            # str_join = ''.join(str_list)
            if product_template.id:
                # 获取产品价格（所有变体中价格最低的）
                product_template_price_float = product_template.list_price

                # product_product_pool = http.request.env['product.product'].search(
                #     [('product_tmpl_id', '=', product_template.id)])
                # if product_product_pool:
                #     product_product_price_list = []
                #     for product_product in product_product_pool:
                #         if product_product.lst_price:
                #             product_product_price_list.append(product_product.lst_price)
                #     if product_product_price_list:
                #         product_template_price_float = min(product_product_price_list)

                # TODO: 产品图片获取
                def get_product_image(product_tmpl_id):
                    product_template_image_object = http.request.env['product.image.ext'].search(
                        [('product_tmpl_id', '=', product_tmpl_id), ('is_primary', '=', True)], limit=1)
                    if product_template_image_object:
                        return product_template_image_object.image_path
                    else:
                        product_template_image_object = http.request.env['product.image.ext'].search(
                            [('product_tmpl_id', '=', product_tmpl_id)], order='order_sort asc', limit=1)
                        if product_template_image_object:
                            return product_template_image_object.image_path
                        else:
                            return "/e2yun_online_shop_extends/static/src/assets/img/products/prod-04-270x300.jpg"

                product_template_image = get_product_image(product_template.id)

                # product_template_image = "/e2yun_online_shop_extends/static/src/assets/img/products/prod-04-270x300.jpg"
                # onclick='grid_image_show_product_template_detail_page(this)'
                # onclick='grid_tittle_show_product_template_detail_page(this)'
                # onclick='list_image_show_product_template_detail_page(this)'
                # onclick='list_tittle_show_product_template_detail_page(this)'
                grid_image_product_detail_id = "grid_image_shop_product_template_" + str(product_template.id)
                grid_tittle_product_detail_id = "grid_tittle_shop_product_template_" + str(product_template.id)
                list_image_product_detail_id = "list_image_shop_product_template_" + str(product_template.id)
                list_tittle_product_detail_id = "list_tittle_shop_product_template_" + str(product_template.id)
                # TODO:等待测试后删除
                product_detail_href = ''
                product_template_name = product_template.name
                product_add_to_cart_href = "cart.html"
                product_template_price_str = "¥" + str(product_template_price_float)
                # TODO:是否需要增加产品描述字段
                if product_template.description_sale:
                    product_template_description = product_template.description_sale
                else:
                    product_template_description = ''
                # TODO:是否添加一个字段，控制产品是否展示到在线商城

                text = """
                               <div class="col-xl-4 col-sm-6 mb--50">
                   <!--TODO：Grid模式-->
                   <div class="ft-product">
                       <div class="product-inner">
                           <div class="product-image">
                               <figure class="product-image--holder">
                                   <img src='/""" + product_template_image + """' alt="Product">
                               </figure>
                               <a id='""" + grid_image_product_detail_id + """' onclick='grid_image_show_product_template_detail_page(this)' class="product-overlay"></a>
                               <div class="product-action"></div>
                           </div>
                           <div class="product-info">
                               <h3 class="product-title"><a id='""" + grid_tittle_product_detail_id + """' onclick='grid_tittle_show_product_template_detail_page(this)'>""" + product_template_name + """</a></h3>
                               <div class="product-info-bottom">
                                   <div class="product-price-wrapper">
                                       <span class="money">""" + product_template_price_str + """</span>
                                   </div>
                                   <a href='/""" + product_add_to_cart_href + """' class="add-to-cart pr--15">
                                       <i class="la la-plus"></i>
                                       <span>添加到购物车</span>
                                   </a>
                               </div>
                           </div>
                       </div>
                   </div>
                   <!--TODO：列表模式-->
                   <div class="ft-product-list">
                       <div class="product-inner">
                           <figure class="product-image">
                               <a id='""" + list_image_product_detail_id + """"' onclick='list_image_show_product_template_detail_page(this)'>
                                   <img src='/""" + product_template_image + """' alt="Products">
                               </a>
                               <div class="product-thumbnail-action">
                               </div>
                           </figure>
                           <div class="product-info">
                               <h3 class="product-title mb--25">
                                   <a id='""" + list_tittle_product_detail_id + """' onclick='list_tittle_show_product_template_detail_page(this)'>""" + product_template_name + """</a>
                               </h3>
                               <div class="product-price-wrapper mb--15 mb-sm--10">
                                   <span class="money">""" + product_template_price_str + """</span>
                               </div>
                               <p class="product-short-description mb--20">""" + product_template_description + """</p>  
                               <div class="ft-product-action-list d-flex align-items-center">
                                   <input type='hidden' name='product_id' value='""" + str(
                    product_template.product_variant_ids[0].id) + """'/>
                                   <input type='hidden' name='product_template_id' value='""" + str(
                    product_template.id) + """'/>
                                   <!-- <input type='hidden' name='csrf_token' value='""" + http.request.csrf_token() + """'/>
                                    <a href='/""" + product_add_to_cart_href + """' class="btn btn-size-md">添加到购物车</a> -->
                                   <a href='javascript:;' class="list_btn_add_cart btn btn-size-md">添加到购物车</a>
                               </div>                                            
                           </div>
                       </div>
                   </div>
               </div>"""
                response_text = response_text + text
                # product_str = "" + str(product_template.id) + ' ' + str(product_template.default_code) + ' ' + str(product_template.name)
                # text = text + "<p id='shop_product_product_" + str(product_template.id) + "' onclick='show_product_details(this)'>" + product_str + "</p>"
        return http.Response(response_text)

    @http.route(['/online_shop/get_product_image/<int:product_template_id>'], type='http', auth="public")
    def get_product_image(self, product_template_id, **kwargs):
        product_template_image_pool = http.request.env['product.image.ext'].search([('product_tmpl_id', '=', product_template_id)], order='order_sort asc')
        datas = []
        # product_template_image.image_path
        for product_template_image in product_template_image_pool:
            datas.append(product_template_image.image_path)

        return http.request.make_response(json.dumps(datas, default=date_utils.json_default))

    @http.route(['/online_shop/get_index_data'], type='http', auth="public")
    def get_index_data(self, **kwargs):
        # 推荐产品
        product_template = http.request.env['product.template'].search(
            [('recommend', '=', True)])
        recommend_datas = []
        for pt in product_template:
            recommend_datas.append({
                'product_id': pt.id,
                'product_image': pt.get_primary_url(),
                'product_name': pt.name,
                'recommend_text': pt.recommend_text or ''
            })
        # 热销产品
        product_template = http.request.env['product.template'].search(
            [('sell_well', '=', True)])
        sell_well_datas = []
        for pt in product_template:
            sell_well_datas.append({
                'product_id': pt.id,
                'product_image': pt.get_primary_url(),
                'product_name': pt.name
            })

        # #合作伙伴logo
        # logo_partner = http.request.env['online.partner'].search([])
        # logo_partner_datas = []
        # for lp in logo_partner:
        #     logo_partner_datas.append({
        #         'logo_image': lp.logo_image,
        #     })

        datas = {
            'recommend_datas': recommend_datas,
            'sell_well_datas': sell_well_datas,
            # 'logo_partner_datas':logo_partner_datas
        }
        return http.request.make_response(json.dumps(datas, cls=MyEncoder, ensure_ascii=False, indent=4))

    @http.route(['/online_shop/get_index_logo_data'], type='http', auth="public")
    def get_index_logo_data(self, **kwargs):

        # 合作伙伴logo
        logo_partner = http.request.env['online.partner'].search([])
        logo_partner_datas = []
        text = """"""
        for lp in logo_partner:
            text = text + """<div class='item'>
                      <figure>
                        <img src='data:image/png;base64,""" + lp.logo_image.decode() + """' alt='Logo' style='max-height:70px;' class='mx-auto'>
                      </figure>
                    </div>
            """

        return http.Response(text)

    # get_product_description
    @http.route(['/online_shop/get_product_description/<int:product_template_id>'], type='http', auth="public")
    def get_product_description(self, product_template_id, **kwargs):
        product_template = http.request.env['product.template'].search([('id', '=', product_template_id)], limit=1)
        if product_template:
            if product_template.description_html:
                response_text = product_template.description_html
                return http.Response(response_text)
            else:
                return http.Response(' ')
        else:
            return http.Response(' ')

    @http.route(['/online_shop/get_template_id'], type='http', auth="public")
    def get_template_id(self, **kwargs):
        template_id = request.session['current_product_detail_id']

        return http.request.make_response(json.dumps({'product_template_id': template_id}))

    @http.route(['/online_shop/get_product_detail_page/<int:product_template_id>'], type='http', auth="user")
    def get_product_detail_page(self, product_template_id, **kwargs):
        if request.session.uid:

            if product_template_id:
                request.session['current_product_detail_id'] = product_template_id
            template = env.get_template('product-details.html')
            html = template.render()
            return html
        else:

            query = werkzeug.urls.url_encode({
                'redirect': '/online_shop/get_product_detail_page/' + str(product_template_id),
                'error': '请登录然后操作'
            })
            return werkzeug.utils.redirect('/web/login?%s' % query)

            # return werkzeug.utils.redirect('/web/login?error=请登录然后操作')

    @http.route(['/online_shop/get_product_detail/<int:product_template_id>'], type='http', auth="public")
    def get_product_detail(self, product_template_id, **kwargs):
        product_template = http.request.env['product.template'].sudo().search([('id', '=', product_template_id)], limit=1)

        if product_template:
            product_template.browse_num = product_template.browse_num + 1
            product_product_pool = http.request.env['product.product'].search([('product_tmpl_id', '=', product_template_id)])
            if product_product_pool:
                product = product_product_pool[0]
                response_text = """"""
                header_text = """<div class="product-summary pl-lg--30 pl-md--0" id="product_detail_replace">
    
    <!--TODO:产品名称-->
    <h3 class="product-title mb--20">"""
                if product_template.description_sale:
                    middle_text = """</h3>
                        <!--TODO:产品简介（短）-->
                        <p class="product-short-description mb--20">""" + str(product_template.description_sale) + """</p>
                        <!--TODO:产品价格-->
                        <div class="product-price-wrapper mb--25">
                            <span class="money">"""
                else:
                    middle_text = """</h3>
                        <!--TODO:产品简介（短）-->
                        <p class="product-short-description mb--20"></p>
                        <!--TODO:产品价格-->
                        <div class="product-price-wrapper mb--25">
                            <span class="money">"""

                price_str = "¥" + str(product.lst_price)
                footer_text = """</span>"""
                browse_num_text = """<p>浏览量 """ + str(product_template.browse_num) + """</p>"""
                so_qty_text = """<p> 销量""" + str(product_template.so_qty) + """</p>"""
                footer_text2 = """</div>
    <div class="product-action d-flex flex-sm-row align-items-sm-center flex-column align-items-start mb--30">
        <input type='hidden' name='inp_product_id' value='""" + str(product.id) + """'/>
        <input type='hidden' name='inp_product_template_id' value='""" + str(product_template_id) + """'/>
        <div>
        <button margin='left' type="button" class="btn btn-size-sm btn-shape-square" onclick="detail_add_cart()">
            添加到购物车
        </button>"""
                if product_template.product_template_external_website:
                    footer_text3 = """<button type="button" margin='right' class="btn-blue btn-size-sm btn-shape-square" onclick="window.open('""" + product_template.product_template_external_website + """')" target='_blank'>
            产品效果图
        </button></div>
                    </div>  
</div>"""
                else:
                    footer_text3 = """</div></div>  
</div>"""

                response_text = header_text + product.name + middle_text + price_str + footer_text + browse_num_text + so_qty_text + footer_text2 + footer_text3
                return http.Response(response_text)


class online_partner(models.Model):
    _name = 'online.partner'
    _description = '电商合作伙伴'
    _order = 'sort'

    name = fields.Char('名称')
    logo_image = fields.Binary('Logo 图片')
    sort = fields.Integer('排序')


class ProductTemplateCategoryExtend(models.Model):
    _inherit = 'product.template'

    category_parents = fields.Many2many('product.public.category', 'parent_id', string='所属父类别', compute='get_category_parents', store=True)
    product_template_external_website = fields.Char(string='产品外部页面链接')
    custom_order = fields.Integer(string='产品展示自定义排序')
    description_html = fields.Html(string='产品详细介绍')
    product_template_order_by_name = fields.Integer('产品按名称排序的次序')
    so_qty = fields.Float('销售数量', compute='_compute_so_qty', store=False)
    recommend = fields.Boolean('推荐产品', default=False)
    recommend_text = fields.Char('推荐描述')
    sell_well = fields.Boolean('热销产品', default=False)

    @api.one
    def _compute_so_qty(self):
        template_id = self.id
        product_product_pool = self.env['product.product'].search([('product_tmpl_id', '=', template_id)])
        if product_product_pool:
            product_ids = product_product_pool.ids
            sale_order_line_pool = self.env['sale.order.line'].search([('product_id', 'in', product_ids)])
            if sale_order_line_pool:
                qty = 0.0
                for record in sale_order_line_pool:
                    qty = qty + record.product_uom_qty
                self.so_qty = qty
            else:
                self.so_qty = 0.0
        else:
            self.so_qty = 0.0

    @api.multi
    def _compute_so_qty(self):
        for product_template in self:
            template_id = product_template.id
            product_product_pool = self.env['product.product'].search([('product_tmpl_id', '=', template_id)])
            if product_product_pool:
                product_ids = product_product_pool.ids
                sale_order_line_pool = self.env['sale.order.line'].search([('product_id', 'in', product_ids)])
                if sale_order_line_pool:
                    qty = 0.0
                    for record in sale_order_line_pool:
                        qty = qty + record.product_uom_qty
                    product_template.so_qty = qty
                else:
                    product_template.so_qty = 0.0
            else:
                product_template.so_qty = 0.0

    @api.one
    @api.depends('public_categ_ids')
    def get_category_parents(self):
        parent_ids = []
        for category in self.public_categ_ids:
            if category.parent_id:
                parent_ids.append(category.parent_id.id)
        if parent_ids:
            parent_ids_write = [(6, 0, parent_ids)]
            self.category_parents = parent_ids_write
            # self.write({'category_parents': parent_ids_write})

    # # public_categ_ids

# class ProductProductGetInfoExtends(models.Model):
#     _inherit = 'product.product'

# class e2yun_online_shop_extends(models.Model):
#     _name = 'e2yun_online_shop_extends.e2yun_online_shop_extends'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
