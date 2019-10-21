from odoo import http
class Academy(http.Controller):

    # 服务协议
    @http.route('/supplier/register/', auth='public', website=True)
    def register(self, **kw):
        #return http.request.render('e2yun_supplier_info.supplier_register')
        # 判断是否填写基本信息，填写过直接到基本信息页面，否则跳转服务协议页面
        user = http.request.env.user
        login = user.login
        supplier_info = http.request.env['e2yun.supplier.info'].sudo().search([('login_name', '=', login)])
        if supplier_info and len(supplier_info) > 0:
            return self.base_info(**kw)
        else:
            return http.request.render('e2yun_supplier_info.supplier_register_index')


    @http.route('/supplier/register_index/', auth='public', website=True)
    def index(self, **kw):
        #判断是否填写基本信息，填写过直接到基本信息页面，否面则跳转服务协议页
        # user = http.request.env.user
        # login = user.login
        # supplier_info = http.request.env['e2yun.supplier.info'].sudo().search([('login_name', '=', login)])
        # if supplier_info and len(supplier_info) > 0:
        #     return self.base_info(self, **kw)
        # else:
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
        #根据登录的用户带出潜在供应商信息
        user = http.request.env.user
        login = user.login
        supplier_info = http.request.env['e2yun.supplier.info'].sudo().search([('login_name','=',login)],limit=1)
        #国家
        countrys = http.request.env['res.country'].sudo().search([])
        # 城市
        citys = http.request.env['res.state.city'].sudo().search([])
        # 开户行国家
        bank_countrys = http.request.env['res.country'].sudo().search([])
        # 开户行省份
        bank_states = http.request.env['res.country.state'].sudo().search([])
        # 开户行城市
        bank_citys = http.request.env['res.state.city'].sudo().search([])
        # 开户行地区
        bank_regions = http.request.env['res.city.area'].sudo().search([])
        # 银行名称
        name_banks = http.request.env['res.bank'].sudo().search([])
        # 币种
        currencys_type = http.request.env['res.currency'].sudo().search([])
        #供应产品类别
        industrys = http.request.env['res.partner.industry'].sudo().search([])
        # 供应商类型
        supplier_types = http.request.env['supplier.type'].sudo().search([])
        if supplier_info and len(supplier_info) > 0:
            states = []
            if supplier_info.country_id:
                states = supplier_info.country_id.state_ids
            else:
                states = http.request.env['res.country.state'].sudo().search([])

            return http.request.render('e2yun_supplier_info.supplier_register_base_info',{'supplier': supplier_info,
                                                                                          'countrys':countrys,
                                                                                          'states':states,
                                                                                          'citys':citys,
                                                                                          'bank_countrys': bank_countrys,
                                                                                          'bank_states':bank_states,
                                                                                          'bank_citys':bank_citys,
                                                                                          'bank_regions':bank_regions,
                                                                                          'name_banks':name_banks,
                                                                                          'currencys_type':currencys_type,
                                                                                          'industrys':industrys,
                                                                                          'supplier_types': supplier_types})
        else:
            val = {
                'company_name': user.company_name,
                'login_name': login,
                'name': login,
                'password': user.password,
                'confirm_password':user.password,
                'email': user.email,
                'vat': user.vat,

            }
            supplier_info_obj = http.request.env['e2yun.supplier.info'].sudo()
            supplier_info = supplier_info_obj.create(val)
            states = http.request.env['res.country.state'].sudo().search([])
            return http.request.render('e2yun_supplier_info.supplier_register_base_info',{'supplier': supplier_info,
                                                                                          'countrys':countrys,
                                                                                          'states':states,
                                                                                          'citys': citys,
                                                                                          'bank_countrys': bank_countrys,
                                                                                          'bank_states': bank_states,
                                                                                          'bank_citys': bank_citys,
                                                                                          'bank_regions': bank_regions,
                                                                                          'name_banks': name_banks,
                                                                                          'currencys_type': currencys_type,
                                                                                          'industrys':industrys,
                                                                                          'supplier_types': supplier_types})




    #认证信息
    @http.route('/supplier/register_authentication_info/', auth='public', website=True)
    def authentication_info(self, **kw):
        return http.request.render('e2yun_supplier_info.supplier_register_authentication_info')

    #完成
    @http.route('/supplier/register_done/', auth='public', website=True)
    def done(self, **kw):
        user = http.request.env.user
        if user:
            login = user.login
            supplier_info = http.request.env['e2yun.supplier.info'].sudo().search([('login_name', '=', login)], limit=1)
            if supplier_info:
                template_id = http.request.env.ref('supplier_register.register_info_submit_mail_template')
                http.request.env['mail.thread'].sudo().message_post_with_template(
                    template_id.id,
                    model='e2yun.supplier.info',
                    res_id=supplier_info.id,
                    composition_mode='mass_mail',
                    partner_ids=supplier_info.partner_id.ids,
                )

        return http.request.render('e2yun_supplier_info.supplier_register_done')

    @http.route('/supplier/register_base_info_form/', type='http',auth='public', methods=['POST'],website=True)
    def base_info_form(self, **kw):
        return True

    # @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    # def website_form(self, model_name, **kwargs):


