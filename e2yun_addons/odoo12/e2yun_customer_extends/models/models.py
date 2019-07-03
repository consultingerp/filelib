# -*- coding: utf-8 -*-

from odoo import models, fields, api, _,exceptions
#import suds
import suds.client

from odoo.exceptions import ValidationError, Warning


class E2yunCsutomerExtends(models.Model):
    _inherit = 'res.partner'

    app_code = fields.Char(string='', copy=False, readonly=True, default=lambda self: _('New'))
    shop_code = fields.Char(string='')
    shop_name = fields.Char(string='')
    referrer = fields.Many2one('res.users', string='')
    occupation = fields.Char(string='')
    car_brand = fields.Char(string='')
    user_nick_name = fields.Char(string='')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ], string='')
    customer_source = fields.Selection([
        ('barcode', 'Barcode'),
        ('manual', 'Manual'),
    ], string='', default='manual')
    pos_state = fields.Boolean(String='Sync Pos State',default=False)
    state = fields.Selection([
        ('potential_customer', 'Potential Customer'),
        ('intention_customer', 'Intention Customer'),
        ('intention_customer_loss', 'Intention Customer Loss'),
        ('target_customer', 'Target Customer'),
        ('target_customer_loss', 'Target Customer Loss'),
        ('contract_customers', 'Contract Customers')
    ], string='', default='potential_customer', group_expand='_group_expand_stage_id')

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

        result = super(E2yunCsutomerExtends, self).create(vals)
        return result

    @api.multi
    def set_intention(self):
        for record in self:
            if not record.mobile or not record.street or not record.street2 or not record.city or not record.state_id or not record.zip or not record.country_id:
                raise Warning(_("Please fill in partner's mobile and address!"))
            record.state = 'intention_customer'

    @api.multi
    def set_intention_loss(self):
        for record in self:
            record.state = 'intention_customer_loss'

    @api.multi
    def set_target(self):
        for record in self:
            record.state = 'target_customer'

    @api.multi
    def set_target_loss(self):
        for record in self:
            record.state = 'target_customer_loss'

    @api.multi
    def set_contract(self):
        for record in self:
            record.state = 'contract_customers'

    @api.multi
    def write(self, values):
        if 'state' in values:
            previous_state = self.state
            new_state = values.get('state')
            # intention_customer_loss  target_customer_loss  contract_customers
            if previous_state in ['potential_customer']:
                if not self.mobile or not self.street or not self.street2 or not self.city or not self.state_id or not self.zip or not self.country_id:
                    raise Warning(_("Please fill in partner's mobile and address!"))
            if previous_state in ['intention_customer_loss', 'target_customer_loss']:
                raise Warning(_("不能从流失客户转换到其他状态！"))
            elif previous_state in ['contract_customers']:
                raise Warning(_("不能从成交客户转换到其他状态！"))
        return super(E2yunCsutomerExtends, self).write(values)


    def run_send_wx_msg(self):
        intention_customer_msg_day = self.env['res.config.settings']._get_intention_customer_msg_day()
        target_customer_msg_day = self.env['res.config.settings']._get_target_customer_msg_day()

        self.send_wx_msg(state='intention_customer',day_num=intention_customer_msg_day)
        self.send_wx_msg(state='target_customer',day_num=target_customer_msg_day)

    def send_wx_msg(self,state,day_num):
        sql = """
            select sum(type_code),user_id,p_id from (select user_id,id as p_id,1 as type_code from res_partner 
                 where (CURRENT_TIMESTAMP - write_date) > interval '"""+day_num+""" day' 
                 and customer = 't' 
                 and active = 't' 
                 and state = '"""+state+"""' 
                 and user_id is not null
                 
                 union
                 
             select p.user_id,p.id as p_id,2 as type_code from crm_lead  l 
                 left join res_partner p on l.partner_id = p.id 
                 where p.customer = 't' 
                 and p.active = 't' 
                 and p.state = '"""+state+"""' 
                 and p.user_id is not null
                 group by p.user_id,p.id
                 having (CURRENT_TIMESTAMP - max(l.write_date)) > interval '"""+day_num+""" day'
                 
                 union
                 
             select p.user_id,p.id as p_id,3 as type_code from mail_activity a 
                 left join res_partner p on p.id = a.res_id
                 where a.res_model = 'res.partner' 
                 and p.customer = 't' 
                 and p.active = 't' 
                 and p.state = '"""+state+"""' 
                 and p.user_id is not null
                 group by p.user_id,p.id
                 having (CURRENT_TIMESTAMP - max(a.write_date)) > interval '"""+day_num+""" day' 
                 ) t group by user_id,p_id having sum(type_code) >= 6
                 
        """
        self._cr.execute(sql)
        users = self.env.cr.dictfetchall()
        if users and len(users) > 0:
            partner_obj = self.env['res.partner']
            wx_user_obj = self.env['wx.user']
            res_user_obj = self.env['res.users']

            for u in users:
                paerner = partner_obj.browse(u['p_id'])
                msg = ''
                if state == 'intention_customer':
                    msg = '意向客户:' + paerner.name + ' 超过' + day_num + '天没有新的服务状态更新'
                elif state == 'target_customer':
                    msg = '准客户:' + paerner.name + ' 超过' + day_num + '天未邀约客户进行方案洽谈'

                wx_user_obj.send_message(msg=msg,user=res_user_obj.browse(u['user_id']))



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

    # def sync_customer_to_pos(self):
    #     ctx = self._context.copy()
    #
    #     active_model = ctx.get('active_model')
    #     active_ids = ctx.get('active_ids', [])
    #
    #     rep = self.env['res.partner'].browse(active_ids)
    #     sync_list = []
    #     cart_items = suds.client.factory.create('ArrayOfCartItem')
    #     for r in rep:
    #         cart_item = suds.client.factory.create('CartItem')
    #
    #         cart_item.provice = r.state_id.name#省
    #         cart_item.city = r.city
    #         cart_item.area = r.street
    #         cart_item.detailaddress = r.street2
    #         cart_item.name1 = r.name
    #         cart_item.name2 = r.user_nick_name
    #         cart_item.mendian = r.shop_code
    #         cart_item.telf1 = r.phone
    #         cart_item.vtext = r.shop_name
    #         cart_item.remark = r.occupation
    #         cart_item.posid = r.app_code
    #         cart_item.pernam = r.create_uid.name
    #
    #
    #         sync_list.append(cart_item)
    #
    #         # sync_list.append({
    #         #     'provice':r.state_id.name,#省
    #         #     'city':r.city,#城市
    #         #     'area':r.street,#县区
    #         #     'detailaddress':r.street2,#地址
    #         #     'name1':r.name,#名称
    #         #     'name2':r.user_nick_name,#昵称
    #         #     'mendian':r.shop_code,#门店编码
    #         #     'telf1':r.phone,#电话
    #         #     'vtext':r.shop_name,#门店名称
    #         #     'remark':r.occupation,#职业
    #         #     'posid':r.app_code,#app编码
    #         #     'pernam':r.create_uid.name,#创建人
    #         # })
    #         cart_items.CartItem = cart_items
    #     if cart_items:
    #         ICPSudo = self.env['ir.config_parameter'].sudo()
    #
    #         url = ICPSudo.get_param('e2yun.sync_pos_member_webservice_url')  # webservice调用地址
    #         client = suds.client.Client(url)
    #
    #         result = client.service.createMember(sync_list)# 调用方法所需要的参数
    #         print(result)
    def sync_customer_to_pos(self):
        ctx = self._context.copy()

        #active_model = ctx.get('active_model')
        active_ids = ctx.get('active_ids', [])

        rep = self.env['res.partner'].browse(active_ids)
        for r in rep:
            ICPSudo = self.env['ir.config_parameter'].sudo()

            url = ICPSudo.get_param('e2yun.sync_pos_member_webservice_url')  # webservice调用地址
            client = suds.client.Client(url)

            result = client.service.createMember(r.state_id.name or '',     #省
                                                 r.city or '',              #城市
                                                 r.street or '',            #县区
                                                 r.street2 or '',           #地址
                                                 r.name or '',              #名称
                                                 r.user_nick_name or '',    #昵称
                                                 r.shop_code or '',         #门店编码
                                                 r.mobile or '',             #手机号码
                                                 r.phone or '',             #电话号码
                                                 r.email or '',             #邮箱
                                                 r.shop_name or '',         #门店名称
                                                 r.occupation or '',        #职业
                                                 r.app_code or '',          #app编码
                                                 r.create_uid.name)          #创建人

            if result != 'S':
                raise exceptions.Warning(result)
            else:
                r.pos_state = True

        return {
            'warning': {
                'title': 'Tips',
                'message': '同步成功'
            }
        }