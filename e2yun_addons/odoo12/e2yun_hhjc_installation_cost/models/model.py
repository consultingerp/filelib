# -*- coding: utf-8 -*-

from odoo import models, fields, api,http
import jinja2
import os
import json
from odoo.http import request
from odoo.addons.utils_tools.iptools.IpAddress import IpAddress


BASE_DIR = os.path.dirname((os.path.dirname(__file__)))
templateLoader = jinja2.FileSystemLoader(searchpath=BASE_DIR + "/static/src")
env = jinja2.Environment(loader=templateLoader)

class Head(models.Model):
    _name = 'hhjc.installation.head'
    _description = '安装费抬头表'

    def _default_company(self):
        return self.env['res.company']._company_default_get('hhjc.installation.head')

    name = fields.Char('名称')
    company_id = fields.Many2one('res.company','公司',default=_default_company)
    remark = fields.Html('备注')
    line_ids = fields.One2many('hhjc.installation.line','head_id')
    _sql_constraints = [
        ('company_id_uniq', 'unique(company_id)', u'公司数据已存在!')
    ]

class Item(models.Model):
    _name = 'hhjc.installation.line'
    _description = '安装费行项目表'

    name=fields.Char('产品类别')
    install_cost = fields.Char('安装标准')
    uninstall_cost = fields.Char('拆费标准')
    head_id = fields.Many2one('hhjc.installation.head')

class WebUserInfoController(http.Controller):

    @http.route('/hhjc_install_cost_page', type='http', auth="public", methods=['GET'])
    def hhjc_installation_page(self, **kwargs):
        template = env.get_template('index.html')
        html = template.render()
        return html

    @http.route('/hhjc_install_cost_data', csrf=False, type='http', auth="public")
    def get_data(self, **kwargs):
        #获取用户地区
        userip = request.httprequest.access_route[0]
        ipinfo = IpAddress.getregion(userip)
        company_id = request.env['res.company'].sudo().search([('company_code', '=', '1000')], limit=1).id
        if ipinfo:
            userregion = ipinfo['region']
            # 根据公司配置显示用户所在公司
            user_company = request.env['res.company'].sudo().search([('area_text_mate', 'like', '%' + userregion)], limit=1)
            if user_company:
                company_id = user_company.id

        #获取标题，备注，行数据
        data = {}
        head = request.env['hhjc.installation.head'].sudo()
        head_data = head.search([('company_id','=',company_id)],limit=1)
        data['name'] = head_data.name
        data['remark'] = head_data.remark
        lines = []
        for line in head_data.line_ids:
            lines.append({
                'name':line.name,
                'install_cost':line.install_cost,
                'uninstall_cost':line.uninstall_cost
            })
        data['lines'] = lines
        return request.make_response(json.dumps(data))


