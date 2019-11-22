# -*- coding: utf-8 -*-

from odoo import models, fields, api, http
import jinja2
import os
import logging

BASE_DIR = os.path.dirname((os.path.dirname(__file__)))
templateLoader = jinja2.FileSystemLoader(searchpath=BASE_DIR + "/static/src")
env = jinja2.Environment(loader=templateLoader)


class OnlineShop(http.Controller):

    @http.route('/hhjc_shop_index', type='http', auth="public", methods=['GET'])
    def hhjc_shop_index(self, **kwargs):
        # env = http.request.env
        template = env.get_template('index.html')
        html = template.render()
        return html

    @http.route('/hhjc_shop_product_list', type='http', auth="public", methods=['GET'])
    def hhjc_shop_product_list(self, **kwargs):
        # env = http.request.env
        template = env.get_template('shop-list-sidebar.html')
        html = template.render()
        return html

    @http.route('/hhjc_shop_product_details', type='http', auth="public", methods=['GET'])
    def hhjc_shop_product_details(self, **kwargs):
        template = env.get_template('product-details.html')
        html = template.render()
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
                    html_to_add = "<li><a id='shop_category_" + str(
                        category_child.id) + "' onclick='show_goods_in_category(this)'>" + category_child.name + "</a></li>"
                    html_body = html_body + html_to_add
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
                    html_to_add = "<li><a id='shop_category_" + str(
                        category_child.id) + "' onclick='show_goods_in_category(this)'>" + category_child.name + "</a></li>"
                    html_body = html_body + html_to_add
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
        response_text = """"""
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
                product_template_price_float = 0.0
                product_product_pool = http.request.env['product.product'].search([('product_tmpl_id', '=', product_template.id)])
                if product_product_pool:
                    product_product_price_list = []
                    for product_product in product_product_pool:
                        if product_product.lst_price:
                            product_product_price_list.append(product_product.lst_price)
                    if product_product_price_list:
                        product_template_price_float = min(product_product_price_list)

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
                    <img src='""" + product_template_image + """' alt="Product">
                </figure>
                <a id='""" + grid_image_product_detail_id + """' onclick='grid_image_show_product_template_detail_page(this)' class="product-overlay"></a>
                <div class="product-action"></div>
            </div>
            <div class="product-info">
                <h3 class="product-title"><a id='""" + grid_tittle_product_detail_id +"""' onclick='grid_tittle_show_product_template_detail_page(this)'>""" + product_template_name + """</a></h3>
                <div class="product-info-bottom">
                    <div class="product-price-wrapper">
                        <span class="money">""" + product_template_price_str + """</span>
                    </div>
                    <a href='""" + product_add_to_cart_href + """' class="add-to-cart pr--15">
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
                    <img src='""" + product_template_image + """' alt="Products">
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
                    <input type='hidden' name='product_id' value='"""+str(product_template.product_variant_ids[0].id)+"""'/>
                    <input type='hidden' name='product_template_id' value='"""+str(product_template.id)+"""'/>
                    <!-- <input type='hidden' name='csrf_token' value='"""+http.request.csrf_token()+"""'/>
                     <a href='""" + product_add_to_cart_href + """' class="btn btn-size-md">添加到购物车</a> -->
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
        large_image_header = """<div class="product-gallery__large-image mb--30">
                                                <div class="product-gallery__wrapper">
                                                    <div class="element-carousel main-slider image-popup"
                                                    data-slick-options='{
                                                        "slidesToShow": 1,
                                                        "slidesToScroll": 1,
                                                        "infinite": true,
                                                        "arrows": false, 
                                                        "asNavFor": ".nav-slider"
                                                    }'>"""
        large_image_footer = """</div>
                                                </div>
                                            </div>"""
        small_image_header = """<div class="product-gallery__nav-image">
                                                <div class="element-carousel nav-slider product-slide-nav slick-vertical-center" 
                                                data-slick-options='{
                                                    "spaceBetween": 30,
                                                    "slidesToShow": 3,
                                                    "slidesToScroll": 1,
                                                    "swipe": true,
                                                    "infinite": true,
                                                    "focusOnSelect": true,
                                                    "asNavFor": ".main-slider",
                                                    "arrows": true, 
                                                    "prevArrow": {"buttonClass": "slick-btn slick-prev", "iconClass": "la la-angle-left" },
                                                    "nextArrow": {"buttonClass": "slick-btn slick-next", "iconClass": "la la-angle-right" }
                                                }'
                                                data-slick-responsive='[
                                                    {
                                                        "breakpoint":767, 
                                                        "settings": {
                                                            "slidesToShow": 4
                                                        } 
                                                    },
                                                    {
                                                        "breakpoint":575, 
                                                        "settings": {
                                                            "slidesToShow": 3
                                                        } 
                                                    },
                                                    {
                                                        "breakpoint":480, 
                                                        "settings": {
                                                            "slidesToShow": 2
                                                        } 
                                                    }
                                                ]'>"""
        small_image_footer = """</div></div>"""
        product_template_image_pool = http.request.env['product.image.ext'].search([('product_tmpl_id', '=', product_template_id)], order='order_sort asc')
        large_image_body = """"""
        small_image_body = """"""
        for product_template_image in product_template_image_pool:
            large_text = """<figure class="product-gallery__image zoom">
                                                    <img src='""" + product_template_image.image_path + """' alt="Product"><div class="product-gallery__actions"><button class="action-btn btn-zoom-popup"><i class="la la-eye"></i></button>
                                                    </div>
                                                </figure>"""
            small_text = """<figure class="product-gallery__nav-image--single">
                                                <img src='""" + product_template_image.image_path +"""' alt="Products">
                                            </figure>"""
            small_image_body = small_image_body + small_text
            large_image_body = large_image_body + large_text

        response_text = large_image_header + large_image_body + large_image_footer + small_image_header + small_image_body + small_image_footer
        return http.Response(response_text)

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


    @http.route(['/online_shop/get_product_detail/<int:product_template_id>'], type='http', auth="public")
    def get_product_detail(self, product_template_id, **kwargs):
        product_template = http.request.env['product.template'].search([('id', '=', product_template_id)], limit=1)
        if product_template_id:
            product_product_pool = http.request.env['product.product'].search([('product_tmpl_id', '=', product_template_id)])
            if product_product_pool:
                product = product_product_pool[0]
                response_text = """"""
                header_text = """<div class="product-summary pl-lg--30 pl-md--0" id="product_detail_replace">
    <div class="product-navigation text-right mb--20">
        <!--TODO:产品详情中用于切换产品的左右箭头-->
        <a href="#" class="prev"><i class="la la-angle-double-left"></i></a>
        <a href="#" class="next"><i class="la la-angle-double-right"></i></a>
    </div>
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
                footer_text = """</span>
    </div>
    <div class="product-action d-flex flex-sm-row align-items-sm-center flex-column align-items-start mb--30">
        <div class="quantity-wrapper d-flex align-items-center mr--30 mr-xs--0 mb-xs--30">
            <label class="quantity-label" for="qty">数量:</label>
            <div class="quantity">
                <input type="number" class="quantity-input" name="qty" id="qty" value="1" min="1">
            </div>
        </div>
        <!--TODO：这里有匿名函数使用js的示例-->
        <input type='hidden' name='inp_product_id' value='"""+str(product.id)+"""'/>
        <input type='hidden' name='inp_product_template_id' value='"""+str(product_template_id)+"""'/>
        <button type="button" class="btn btn-size-sm btn-shape-square" onclick="detail_add_cart()">
            添加到购物车
        </button>"""
                if product_template.product_template_external_website:
                    footer_text2 = """<button type="button" class="btn btn-size-sm btn-shape-square" onclick="window.open('""" + product_template.product_template_external_website + """')" target='_blank'>
            产品效果图
        </button>
                    </div>  
</div>"""
                else:
                    footer_text2 = """</div>  
</div>"""

                response_text = header_text + product.name + middle_text + price_str + footer_text +footer_text2
                return http.Response(response_text)

class ProductTemplateCategoryExtend(models.Model):
    _inherit = 'product.template'

    category_parents = fields.Many2many('product.public.category', 'parent_id', string='所属父类别', compute='get_category_parents', store=True)
    product_template_external_website = fields.Char(string='产品外部页面链接')
    custom_order = fields.Integer(string='产品展示自定义排序')
    description_html = fields.Html(string='产品详细介绍')

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