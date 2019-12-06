# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, exceptions, tools, _
from datetime import timedelta
import logging
import suds.client
import json
from . import myjsondateencode
from datetime import date, datetime

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = ['helpdesk.ticket']

    address = fields.Char(string='联系地址')
    u_address = fields.Char(string='所在地')
    j_address = fields.Char(string='具体位置')
    is_wx_client = fields.Char(string='wx')
    order_datetime = fields.Datetime(string='预约时间', required=True, default=lambda self: fields.Datetime.now())
    user_phone = fields.Char('购买电话')
    phone = fields.Char('联系电话')
    brand = fields.Many2one('helpdesk.ticket.brandtype', string="售后品牌")
    userip = fields.Char('IP 地址')
    matnrs = fields.Char('物料')
    arktxs = fields.Char('物料描述')
    posserviceorderid = fields.Char('POS服务订单编号')
    area_id = fields.Char('地区')
    city_id = fields.Char('城市')
    state_id = fields.Char('区县')

    @api.model
    def create(self, vals):
        res = super(HelpdeskTicket, self).create(vals)
        if res.id:
            res_user_obj = self.env['res.users']
            action_xmlid = 'helpdesk.helpdesk_ticket_action_main_tree'
            action_url = '/web?#menu_id=%s&action=%s&id=%s&model=helpdesk.ticket&view_type=form' % (
                self.env.ref('helpdesk.menu_helpdesk_root').id,
                self.env.ref(action_xmlid).id,
                str(res.id)
            )
            try:
                if res.team_id.member_ids:  # 发送微信给团队成团
                    for user in res.team_id.member_ids:
                        member_data = {
                            "first": {
                                "value": "您好，您有一个新的售后服务单"
                            },
                            "keyword1": {
                                "value": "售后服务单"
                            },
                            "keyword2": {
                                "value": res.id
                            },
                            "keyword3": {
                                "value": res.name
                            },
                            "keyword4": {
                                "value": res.order_datetime.strftime("%Y-%m-%d")  # (datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                            },
                            "remark": {
                                "value": "地址:%s" % res.address or ''
                            }
                        }
                        if user.wx_user_id:
                            user.wx_user_id.send_template_message(member_data, template_name='售后服务单通知', user=user, url=action_url)
                user_data = {
                    "first": {
                        "value": "您的申请服务订单,我们%s的团队已收到并正在审核" % res.team_id.name
                    },
                    "keyword1": {
                        "value": "售后服务单",
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": res.id
                    },
                    "keyword3": {
                        "value": res.name
                    },
                    "keyword4": {
                        "value": res.order_datetime.strftime("%Y-%m-%d")  # (datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                    },
                    "remark": {
                        "value": "服务地地址:%s，我们将24小时电话联系。谢谢！" % res.address,
                        "color": "#173177"
                    }
                }
                if res.partner_id.wx_user_id:
                    res.partner_id.wx_user_id.send_template_message(user_data, template_name='售后服务订单接收通知', partner=res.partner_id, url=res.access_url)

            except Exception as e:

                _logger.warning(str(e))

        return res

    @api.multi
    def write(self, vals):
        user_old = ''
        res = super(HelpdeskTicket, self).write(vals)
        if vals.get('user_id'):
            ok = ''
        if vals.get('user_id'):
            _logger.debug("分配单")
            wx_user_obj = self.env['wx.user']
            res_user_obj = self.env['res.users']
            action_xmlid = 'helpdesk.helpdesk_ticket_action_main_tree'
            action_url = '/web?#menu_id=%s&action=%s&id=%s&model=helpdesk.ticket&view_type=form' % (
                self.env.ref('helpdesk.menu_helpdesk_root').id,
                self.env.ref(action_xmlid).id,
                str(self.id)
            )
            if not user_old:
                first_str = "您好，售后服务订单已分配给%s" % self.user_id.name
            else:
                first_str = "您好，售后服务订单已从%s分配给%s" % (user_old, self.user_id.name)
            url = self.env['ir.config_parameter'].sudo().get_param('e2yun.pos_url') + "/esb/webservice/Serviceorder?wsdl"  # webservice调用地址
            client = suds.client.Client(url)
            datajsonstring = dict()
            datajsonstring['store'] = self.partner_id.shop_code.shop_code
            datajsonstring['customerid'] = self.partner_id.app_code
            datajsonstring['telephone'] = self.phone
            datajsonstring['address'] = self.address
            datajsonstring['app_code'] = self.partner_id.app_code
            datajsonstring['taskdate'] = self.order_datetime
            datajsonstring['serviceorderid'] = self.posserviceorderid or ''
            datajsonstring['taskcontent2'] = self.name
            datajsonstring['mesage'] = first_str
            datajsonstring['creater'] = self.env.user.name
            # 不同步服务订单到POS
            # result = client.service.synServiceOrderFromCrm(json.dumps(datajsonstring, cls=myjsondateencode.MyJsonEncode))
            # resultjson = json.loads(result)
            #
            # if resultjson['sucess'] != 'ok':
            #     raise exceptions.Warning('同步创建POS服务单出错' + result)
            # else:
            #     self.write({'posserviceorderid': resultjson['serviceorderid']})
            for user in self.team_id.member_ids:

                member_data = {
                    "first": {
                        "value": first_str
                    },
                    "keyword1": {
                        "value": "售后服务单",
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": self.id
                    },
                    "keyword3": {
                        "value": self.name
                    },
                    "keyword4": {
                        "value": self.order_datetime.strftime("%Y-%m-%d")
                    },
                    "remark": {
                        "value": "地址:%s" % self.address,
                        "color": "#173177"
                    }
                }
                if user.wx_user_id:
                    wx_user_obj.send_template_message(member_data, template_name='售后服务单通知', user=user, url=action_url)

        if vals.get('stage_id'):
            _logger.info("change stage_id%s" % vals.get('stage_id'))
            datavalues = self.env['helpdesk.stage'].browse(vals.get('stage_id'))
            member_data = {
                "first": {
                    "value": "售后服务订单状态变更"
                },
                "keyword1": {
                    "value": "售后服务单"
                },
                "keyword2": {
                    "value": self.id,
                    "color": "#173177"
                },
                "keyword3": {
                    "value": self.name
                },
                "keyword4": {
                    "value": self.order_datetime.strftime("%Y-%m-%d")
                },
                "remark": {
                    "value": "服务订单状态已变更为%s" % datavalues.display_name,
                    "color": "#173177"
                }
            }
            if self.partner_id.wx_user_id:
                self.partner_id.wx_user_id.send_template_message(member_data, template_name='售后服务单通知', user=self.partner_id, url=self.access_url)
            if vals.get('stage_id') == 3:
                member_data = {
                    "first": {
                        "value": "你的售后服务订单已完成"
                    },
                    "keyword1": {
                        "value": "售后服务单"
                    },
                    "keyword2": {
                        "value": self.id,
                        "color": "#173177"
                    },
                    "keyword3": {
                        "value": self.name
                    },
                    "keyword4": {
                        "value": self.order_datetime.strftime("%Y-%m-%d")
                    },
                    "remark": {
                        "value": "请花点时间给我们的服务打分，告诉我们你对我们服务的评价。",
                        "color": "#173177"
                    }
                }
                if self.partner_id.wx_user_id:
                    access_url = "/im_livechat/user_rating/%s" % self.id
                    self.partner_id.wx_user_id.send_template_message(member_data, template_name='售后服务单通知',
                                                                     user=self.partner_id, url_type='', url=access_url)

        return res

    @api.multi
    def synserviceorder(self):
        url = self.env['ir.config_parameter'].sudo().get_param('e2yun.pos_url') + "/esb/webservice/Serviceorder?wsdl"  # webservice调用地址
        client = suds.client.Client(url)
        datajsonstring = dict()
        datajsonstring['customerid'] = self.partner_id.app_code
        telephone = "%s/%s" % (self.phone, self.user_phone)
        datajsonstring['telephone'] = telephone
        address = self.u_address or ''
        address = address.replace(' ', '|');
        j_address = self.j_address or ''
        datajsonstring['address'] = address + j_address
        datajsonstring['app_code'] = self.partner_id.app_code
        datajsonstring['taskdate'] = self.order_datetime
        datajsonstring['serviceorderid'] = self.posserviceorderid or ''
        datajsonstring['taskcontent2'] = self.name
        datajsonstring['mesage'] = '同步服务订单'
        datajsonstring['creater'] = self.env.user.name
        datajsonstring['account'] = self.env.user.login
        bukrs = self.team_id.company_id.company_code or '1000'
        datajsonstring['bukrs'] = self.team_id.company_id.company_code
        # datajsonstring['store'] = self.partner_id.shop_code.shop_code
        store = '100002002' if bukrs == '1000' else '200002002'
        datajsonstring['store'] = store
        result = client.service.synServiceOrderFromCrm(json.dumps(datajsonstring, cls=myjsondateencode.MyJsonEncode))

        resultjson = json.loads(result)
        if resultjson['sucess'] != 'ok':
            raise exceptions.Warning('同步创建POS服务单出错:%s客户:%s' % (resultjson['message'], self.partner_id.name))
        else:
            self.write({'posserviceorderid': resultjson['serviceorderid']})
        return {'success': True,
                'error_message': False,
                'warning_message': False}
