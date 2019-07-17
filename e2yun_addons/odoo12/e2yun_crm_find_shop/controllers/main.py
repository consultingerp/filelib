from odoo import http


class Map(http.Controller):

    # @http.route('/library/books', auth='user')  # 要求为登录用户才能访问URL地址,如果需要公开,修改auth参数为public
    # def list(self, *args, **kwargs):
    #     Book = http.request.env['library.book']
    #     # 使用http.request.env来获取环境,可以从目录中获取有效图书记录集
    #     books = Book.search([])
    #     return http.request.render(
    #         'hhtest.book_list_template', {'books': books})
    #     # 使用http.request.render来返回模板并输出HTML,可通过字典给模板传值,模板是视图类型


    # @http.route('/map', auth='public')
    # def gaode_map(self, *args, **kwargs):
    #
    #     return http.request.render(
    #         'e2yun_crm_find_shop.gaode_map_template', {}
    #     )

    @http.route('/map', auth='public')
    def gaode_map(self, *args, **kwargs):
        WX = http.request.env['wx.config.settings']
        wx = WX.search([])
        return http.request.render(
            'e2yun_crm_find_shop.map_template', {'wx': wx}
        )