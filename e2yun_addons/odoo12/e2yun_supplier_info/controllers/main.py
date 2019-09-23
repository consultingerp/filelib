from odoo import http
class Academy(http.Controller):


    @http.route('/supplier/register/', auth='public', website=True)
    def register(self, **kw):
        #return http.request.render('e2yun_supplier_info.supplier_register')
        return http.request.render('e2yun_supplier_info.supplier_register_index')

    #服务协议
    @http.route('/supplier/register_index/', auth='public', website=True)
    def index(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register_index')

    #失信管理规范
    @http.route('/supplier/register_index_2/', auth='public', website=True)
    def index_2(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register_index_2')

    #商业道德协议
    @http.route('/supplier/register_index_3/', auth='public', website=True)
    def index_3(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register_index_3')

    #基本信息
    @http.route('/supplier/register_base_info/', auth='public', website=True)
    def base_info(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register_base_info')

    #认证信息
    @http.route('/supplier/register_authentication_info/', auth='public', website=True)
    def authentication_info(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register_authentication_info')

    #完成
    @http.route('/supplier/register_done/', auth='public', website=True)
    def done(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register_done')

    @http.route('/supplier/register_base_info_form/', type='http',auth='public', methods=['POST'],website=True)
    def base_info_form(self, **kw):
        return True

    # @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    # def website_form(self, model_name, **kwargs):


