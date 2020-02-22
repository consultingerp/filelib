# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_partner(models.Model):
    _inherit = 'res.partner'

    supplier_code = fields.Char('供应商代码')
    secondary_industry_ids = fields.Many2many(
        comodel_name='res.partner.industry', string="供应产品类别",
        domain="[('id', '!=', industry_id)]")

    organ_code = fields.Char('组织代码')
    business_license = fields.Binary('营业执照', attachment=True)
    annual_turnover = fields.Selection(
        [('1', '1000万以下'), ('2', '1000万-5000万'), ('3', '5000万-1亿'), ('4', '1亿-10亿'), ('5', '10亿-100亿')], '年营业额')
    employees = fields.Selection([('1', '500人以下'), ('2', '500-1000人'), ('3', '1000-5000人'), ('4', '5000-10000人')],
                                 '企业员工')
    authenitcation_id = fields.One2many('e2yun.supplier.authentication.info', 'partner_info_id', '认证信息')

    listed_company = fields.Boolean('是否上市')

    # 新增添字段
    comment = fields.Text(string='Notes')
    # 供应商类型
    suppliertype_ids = fields.Many2many('supplier.type', string='供应商类型')

    nature_enterprise = fields.Selection(
        [('State Administrative Enterprises', '国家行政企业'), ('Public-Private Cooperative Enterprises', '公私合作企业'),
         ('Sino-foreign joint ventures', '中外合资企业'), ('Social Organizations', '社会组织机构'),
         ('International Organization Institutions', '国际组织机构'), ('Foreign enterprise', '外资企业'),
         ('private enterprise', '私营企业'), ('Collective enterprise', '集体企业'), ('Defense Military Enterprises', '国防军事企业')],
        '企业性质')
    registered_address = fields.Char('注册地址')
    company_profile = fields.Text('公司简介')
    # 新增公司信息
    validity_license = fields.Date('营业执照有效期')
    CreditCode = fields.Char('统一社会信用代码', help="Unified Social Credit Code.")
    registered_capital = fields.Char('注册资金')
    image_company = fields.Binary('公司正门照片')
    organization_chart = fields.Binary('组织架构图')
    image_product = fields.Binary('工厂区生产照片')
    # 新增银行信息
    country_bank = fields.Many2one('res.country', '开户行国家', required=True, ondelete='restrict')
    province_bank = fields.Many2one('res.country.state', '开户行省份', required=True, ondelete='restrict')
    city_bank = fields.Many2one('res.city', '开户行城市', required=True, ondelete='restrict')
    # region_bank = fields.Many2one('res.city.area', '开户行地区', ondelete='restrict')
    name_bank = fields.Many2one('res.bank', '银行名称', required=True)
    name_bank_branch = fields.Char('分行名称')
    name_banks = fields.Char('支行名称')
    # account_bank = fields.Many2one('res.partner.bank', '银行账号', required=True)
    account_bank = fields.Char('银行账号')
    name_account = fields.Char('账号名称')
    currency_type = fields.Many2one('res.currency', '币种', required=True)
    code_bank = fields.Char('银行代码')
    enclosure_bank = fields.Binary('开户行资料附件')
    # 联系人/账号信息
    name = fields.Char(index=True)
    login_name = fields.Char('登录名')
    phone = fields.Char()
    mobile = fields.Char()
    email = fields.Char()
    function = fields.Char(string='Job Position')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    city = fields.Many2one('res.city', 'City', ondelete='restrict')
    street = fields.Char('详细地址')
    website = fields.Char()

    # 修改供应商默认属性

    @api.model
    def create(self, values):
        # overridden to automatically invite user to sign up
        if 'name' not in values and not values('name'):
            if 'email' in values and values['email']:
                values['name'] = values['email']
            else:
                values['name'] = 'nonameandnoemail'
        user = super(res_partner, self).create(values)
        return user

    # 国家省份联动：
    @api.onchange('country_id')
    def _onchange_country_id(self):
        self.state_id = False
        self.city = False
        if self.country_id:
            return {'domain': {'state_id': [('country_id', '=', self.country_id.id)]}}
        else:
            return {'domain': {'state_id': []}}

    # 省份城市联动
    @api.onchange('state_id')
    def _onchange_state_id(self):
        self.city = False
        if self.state_id:
            return {'domain': {'city': [('state_id', '=', self.state_id.id)]}}
        else:
            return {'domain': {'city': []}}

    # 开户行国家省份联动：
    @api.onchange('country_bank')
    def _onchange_country_bank(self):
        self.province_bank = False
        self.city = False
        if self.country_bank:
            return {'domain': {'province_bank': [('country_id', '=', self.country_bank.id)]}}
        else:
            return {'domain': {'province_bank': []}}

    # 开户行省份城市联动
    @api.onchange('province_bank')
    def _onchange_province_bank(self):
        self.city_bank = False
        if self.province_bank:
            return {'domain': {'city_bank': [('state_id', '=', self.province_bank.id)]}}
        else:
            return {'domain': {'city_bank': []}}
