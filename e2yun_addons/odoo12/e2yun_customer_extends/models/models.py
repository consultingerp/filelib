# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions, http
#import suds
import suds.client
import re
import datetime
from datetime import timedelta
# import werkzeug
from odoo.exceptions import ValidationError, Warning

class E2yunUserAddPartnerRelated(models.Model):
    _inherit = 'res.users'

    related_partner = fields.Many2many('res.partner')


class E2yunCsutomerExtends(models.Model):
    _inherit = 'res.partner'

    def default_shop_code(self):
        user_pool = self.env['res.users']
        user_id = self.env.context.get('uid')
        user = user_pool.search([('id', '=', user_id)])
        shop = user.partner_id.shop_code
        return shop

    # 将现有字段设为必输
    mobile = fields.Char(required=True)
    state_id = fields.Many2one("res.country.state", required=True)
    country_id = fields.Many2one('res.country', required=True)
    street = fields.Char(required=True)
    city_id = fields.Many2one('res.state.city', required=True)
    area_id = fields.Many2one('res.city.area', required=True)

    app_code = fields.Char(string='', copy=False, readonly=True, default=lambda self: _('New'))
    shop_code = fields.Many2one('crm.team', string='', default=default_shop_code)
    shop_name = fields.Char(string='', readonly=True, compute='_compute_shop_name', store=True)
    referrer = fields.Many2one('res.users', string='')
    occupation = fields.Char(string='')
    car_brand = fields.Char(string='')
    user_nick_name = fields.Char(string='')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ], string='')
    customer_source = fields.Selection([
        ('qrscene_USERS', 'User Barcode'),
        ('qrscene_TEAM', 'Team Barcode'),
        ('subscribe', 'Subscribe'),
        ('qrscene_COMPANY', 'QR Scan Company'),
        ('manual', 'Manual'),
        ('qrscene_COMPANYEXTERNAL', 'QR Scan Company External'),
        ('pos_sync', 'POS Sync')
    ], string='', default='manual')
    pos_state = fields.Boolean(String='Sync Pos State',default=False)
    state = fields.Selection([
        ('potential_customer', 'Potential Customer'),
        ('intention_customer', 'Intention Customer'),
        ('intention_customer_loss', 'Intention Customer Loss'),
        ('target_customer', 'Target Customer'),
        ('target_customer_loss', 'Target Customer Loss'),
        ('contract_customers', 'Contract Customers')
    ], string='Status', default='potential_customer', group_expand='_group_expand_stage_id')
    related_guide = fields.Many2many('res.users',  domain="[('function', '!=', False)]", readonly=True)
    user_id = fields.Many2one('res.users', readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super(E2yunCsutomerExtends, self).default_get(fields_list)
        res['user_id'] = self.env.user.id
        return res

    @api.onchange('shop_code')
    def on_change_shop_name(self):
        # new_context = self.env.context.copy()
        # new_context['show_custom_name'] = 2
        # self.with_context(new_context).shop_code.name_get()
        self.shop_name = self.shop_code.name

    @api.multi
    @api.depends('shop_code')
    def _compute_shop_name(self):
        for record in self:
            record.shop_name = record.shop_code.name

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return ['potential_customer', 'intention_customer', 'intention_customer_loss', 'target_customer', 'target_customer_loss', 'contract_customers']

    @api.model
    def create(self, vals):
        if vals.get('app_code', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['app_code'] = self.env['ir.sequence'].with_context(force_company=vals['company_id'])\
                                   .next_by_code('app.code') or _('New')
            else:
                vals['app_code'] = self.env['ir.sequence'].next_by_code('app.code') or _('New')

        pos_flag = False
        if vals.get('pos_flag', False):
            pos_flag = True
            del vals['pos_flag']

        result = super(E2yunCsutomerExtends, self).create(vals)
        if pos_flag and vals.get('shop_code',False):
            result.teams = [(6,0,[vals.get('shop_code'),])]

        if not vals.get('pos_flag', False) and result.state != 'potential_customer':
            result.sync_customer_to_pos()
            result.pos_state = True

        return result

    # @api.multi
    # def set_intention(self):
    #     for record in self:
    #         if not record.mobile or not record.street or not record.city or not record.state_id:
    #             raise Warning(_("Please fill in partner's mobile and address!"))
    #         record.state = 'intention_customer'
    #
    # @api.multi
    # def set_intention_loss(self):
    #     for record in self:
    #         record.state = 'intention_customer_loss'
    #
    # @api.multi
    # def set_target(self):
    #     for record in self:
    #         record.state = 'target_customer'
    #
    # @api.multi
    # def set_target_loss(self):
    #     for record in self:
    #         record.state = 'target_customer_loss'
    #
    # @api.multi
    # def set_contract(self):
    #     for record in self:
    #         record.state = 'contract_customers'

    @api.multi
    def write(self, values):
        if 'state' in values:
            previous_state = self.state
            new_state = values.get('state')
            # intention_customer_loss  target_customer_loss  contract_customers
            if previous_state in ['potential_customer']:
                if not self.mobile or not self.state_id or not self.city_id or not self.area_id or not self.street:
                    raise Warning(_("Please fill in partner's mobile and address!"))
            if previous_state not in ['potential_customer'] and new_state in ['potential_customer']:
                raise Warning(_("Can not back to potential_customer from other state"))
            # if previous_state in ['intention_customer_loss', 'target_customer_loss']:
            #     raise Warning(_("不能从流失客户转换到其他状态！"))
            # elif previous_state in ['contract_customers']:
            #     raise Warning(_("不能从成交客户转换到其他状态！"))
        # 对修改后的手机号进行验证
        if 'mobile' in values and values.get('mobile',False):
            mobile = values.get('mobile')
            ret = re.match(r"^(((13[0-9]{1})|(15[0-9]{1})|(17[0-9]{1})|(18[0-9]{1}))+\d{8})$", mobile)
            if not ret:
                raise Warning(_("请输入合法手机号码！"))

        if values.get('pos_flag',False) and values.get('shop_code',False):
            values['teams'] = [(6,0,[values.get('shop_code'),])]
            del values['pos_flag']
        result = super(E2yunCsutomerExtends, self).write(values)

        if self.state != 'potential_customer' and not values.get('pos_flag',False) and not values.get('pos_state',False):
            self.sync_customer_to_pos()
            self.pos_state = True
        return result


    def run_send_wx_msg(self):
        intention_customer_msg_day = self.env['res.config.settings']._get_intention_customer_msg_day()
        target_customer_msg_day = self.env['res.config.settings']._get_target_customer_msg_day()

        self.send_wx_msg(state='intention_customer',day_num=intention_customer_msg_day)
        self.send_wx_msg(state='target_customer',day_num=target_customer_msg_day)

    def send_wx_msg(self,state,day_num):
        sql = """
            select rel.res_users_id as user_id,t.* from (select sum(type_code),p_id from (
              select distinct id as p_id,1 as type_code from res_partner p 
                 where (CURRENT_TIMESTAMP - write_date) > interval '""" + day_num + """ day' 
                 and p.customer = 't' 
                 and p.active = 't' 
                 and p.state = '""" + state + """' 

             union

                select p.id as p_id,2 as type_code from crm_lead  l 
                 right join res_partner p on l.partner_id = p.id 
                 where p.customer = 't' 
                 and p.active = 't' 
                 and p.state = '""" + state + """' 
                 group by p.id
                 having (((CURRENT_TIMESTAMP - max(l.write_date)) > interval '""" + day_num + """ day' ) or max(l.write_date) is null)

             union

                select p.id as p_id,3 as type_code from mail_activity a 
                 right join res_partner p on p.id = a.res_id
                 where a.res_model = 'res.partner' 
                 and p.customer = 't' 
                 and p.active = 't' 
                 and p.state = '""" + state + """' 
                 group by p.id
                 having (((CURRENT_TIMESTAMP - max(a.write_date)) > interval '""" + day_num + """ day' ) or max(a.write_date) is null)
                 ) t group by p_id having sum(type_code) >= 6) t 
                 inner join res_partner_res_users_rel rel on rel.res_partner_id = t.p_id

        """
        self._cr.execute(sql)
        users = self.env.cr.dictfetchall()
        template_id = ''
        configer_para = self.env["wx.paraconfig"].sudo().search([('paraconfig_name', '=', '计划事件提醒')])
        if configer_para:
            template_id = configer_para[0].paraconfig_value
        if users and len(users) > 0:
            partner_obj = self.env['res.partner']
            wx_user_obj = self.env['wx.user']
            res_user_obj = self.env['res.users']

            for u in users:
                partner = partner_obj.browse(u['p_id'])
                msg = ''
                if state == 'intention_customer':
                    msg = '意向客户:' + partner.name + ' 超过' + day_num + '天没有新的服务状态更新'
                elif state == 'target_customer':
                    msg = '准客户:' + partner.name + ' 超过' + day_num + '天未邀约客户进行方案洽谈'

                data = {
                    "first":{
                        "value":"客户跟踪提醒"
                    },
                    "keyword2":{
                        "value":partner.name
                    },
                    "keyword3": {
                        "value": (datetime.datetime.now()+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                    },
                    "remark":{
                        "value":msg
                    }

                }
                #wx_user_obj.send_template_message(data, template_id, user=res_user_obj.browse(u['user_id']))
                try:
                    wx_user_obj.send_template_message(data,template_id,user=res_user_obj.browse(u['user_id']),url_type='out')
                except:
                    pass

    def sync_customer_to_pos(self):
        for r in self:

            if r.state == 'potential_customer':
                raise exceptions.Warning('状态为潜在客户，不能同步到POS系统')

            # if r.pos_state:
            #     raise exceptions.Warning("POS状态已传输，不能再同步哟！")
            ICPSudo = self.env['ir.config_parameter'].sudo()

            url = ICPSudo.get_param('e2yun.pos_url') +'/esb/webservice/SyncMember?wsdl'  # webservice调用地址
            client = suds.client.Client(url)
            shop_code = ''
            shop_name = ''
            if r.shop_code:
                shop_code = r.shop_code.shop_code
                shop_name = r.shop_code.name
            openid = ''
            if r.wx_user_id:
                openid = r.wx_user_id.openid
            result = client.service.createMember(r.state_id.name or '',  # 省
                                                 r.city_id.name or '',  # 城市
                                                 r.area_id.name or '',  # 县区
                                                 r.street or '',  # 地址
                                                 r.name or '',  # 名称
                                                 r.user_nick_name or '',  # 昵称
                                                 shop_code or '',  # 门店编码
                                                 r.mobile or '',  # 手机号码
                                                 r.phone or '',  # 电话号码
                                                 r.email or '',  # 邮箱
                                                 shop_name or '',  # 门店名称
                                                 r.occupation or '',  # 职业
                                                 r.app_code or '',  # app编码
                                                 self.env.user.name,# 创建人
                                                 openid
                                                 )

            if result != 'S':
                raise exceptions.Warning('客户同步到POS系统出现错误，请检查输入的数据'+result)

        return True


    @api.model
    def updata_customer_state(self):
        customers = self.search([('state','in',['potential_customer','intention_customer','target_customer']),('customer','=',True)])
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncMember?wsdl'  # webservice调用地址
        for customer in customers:
            client = suds.client.Client(url)
            result = client.service.updateState(customer.id or '', customer.app_code or '', customer.state or '')


#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class resPartnerBatch(models.TransientModel):
    _name = 'res.partner.extends.batch'

    def sync_customer_to_pos(self):
        ctx = self._context.copy()

        # active_model = ctx.get('active_model')
        active_ids = ctx.get('active_ids', [])

        rep = self.env['res.partner'].browse(active_ids)
        for r in rep:
            # if r.pos_state:
            #     raise exceptions.Warning("POS状态已传输，不能再同步哟！")

            if r.state == 'potential_customer':
                raise exceptions.Warning('状态为潜在客户，不能同步到POS系统')
            ICPSudo = self.env['ir.config_parameter'].sudo()

            url = ICPSudo.get_param('e2yun.pos_url') + '/esb/webservice/SyncMember?wsdl'  # webservice调用地址
            client = suds.client.Client(url)

            shop_code = ''
            shop_name = ''
            if r.shop_code:
                shop_code = r.shop_code.shop_code
                shop_name = r.shop_code.name
            openid = ''
            if r.wx_user_id:
                openid = r.wx_user_id.openid

            result = client.service.createMember(r.state_id.name or '',  # 省
                                                 r.city_id.name or '',  # 城市
                                                 r.area_id.name or '',  # 县区
                                                 r.street or '',  # 地址
                                                 r.name or '',  # 名称
                                                 r.user_nick_name or '',  # 昵称
                                                 shop_code or '',  # 门店编码
                                                 r.mobile or '',  # 手机号码
                                                 r.phone or '',  # 电话号码
                                                 r.email or '',  # 邮箱
                                                 shop_name or '',  # 门店名称
                                                 r.occupation or '',  # 职业
                                                 r.app_code or '',  # app编码
                                                 self.env.user.name,openid)  # 创建人

            if result != 'S':
                raise exceptions.Warning('客户同步到POS系统出现错误，请检查输入的数据'+result)
            else:
                r.pos_state = True

        return True


class E2yunCrmTeamNameExtends(models.Model):
    _inherit = 'crm.team'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        flag = self.env.context.get('search_owned_shop', False)
        if flag:
            user_related_teams = self.env.user.teams
            args.append(('id', 'in', user_related_teams.ids))
            # teams = self.search(['&', '|', ('shop_code', operator, name), ('name', operator, name), ('id', 'in', user_related_teams)])
            return super(E2yunCrmTeamNameExtends, self).name_search(name, args, operator, limit)
        if name:
            teams = self.search(['|', ('shop_code', operator, name), ('name', operator, name)])
            return teams.name_get()
        # res = self.search([('shop_code', operator, name)])
        # res = super(E2yunCrmTeamNameExtends, self).name_search(name, args, operator, limit)
        else:
            return super(E2yunCrmTeamNameExtends, self).name_search(name, args, operator, limit)

    @api.multi
    def name_get(self):
        flag = self.env.context.get('show_custom_name', False)
        if flag == 1:
            res = []
            for crm_team in self:
                name = str(crm_team.shop_code) + ' ' + str(crm_team.name)
                res.append((crm_team.id, name))
            return res
        elif flag == 2:
            res = []
            for crm_team in self:
                name = str(crm_team.shop_code)
                res.append((crm_team.id, name))
            return res
        else:
            return super(E2yunCrmTeamNameExtends, self).name_get()

    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     flag = self.env.context.get('search_owned_shop', False)
    #     if flag:
    #         # user_related_teams = self.env.user.teams
    #         user_related_teams = self.env['res.users'].browse(2)
    #         # condition = ['id', 'in', user_related_teams]
    #         # condition_tuple = tuple(condition)
    #         # args.append(condition_tuple)
    #         res = super(E2yunCrmTeamNameExtends, self).search(args, offset, limit, order, count)
    #         return res
    #     else:
    #         return super(E2yunCrmTeamNameExtends, self).search(args, offset, limit, order, count)





        # return [(e.shop_code, e.name) for e in self]
        # res = self.get_formview_id()
        # for crm_team in self:
        #     # name = str(crm_team.shop_code) + ' ' + str(crm_team.name)
        #     name = str(crm_team.shop_code)
        #     res.append((crm_team.id, name))
        # return res

