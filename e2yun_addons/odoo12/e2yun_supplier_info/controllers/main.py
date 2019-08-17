from odoo import http
class Academy(http.Controller):


    @http.route('/supplier/register/', auth='public', website=True)
    def register(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register')

    @http.route('/supplier/register_index/', auth='public', website=True)
    def index(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register_index')

    @http.route('/supplier/register_base_info/', auth='public', website=True)
    def base_info(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register_base_info')

    @http.route('/supplier/register_authentication_info/', auth='public', website=True)
    def authentication_info(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register_authentication_info')

    @http.route('/supplier/register_done/', auth='public', website=True)
    def done(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register_done')

    @http.route('/supplier/register_base_info_form/', type='http',auth='public', methods=['POST'],website=True)
    def base_info_form(self, **kw):
        return True

    # @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    # def website_form(self, model_name, **kwargs):


