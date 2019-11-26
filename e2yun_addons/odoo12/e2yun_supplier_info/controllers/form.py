# -*- coding: utf-8 -*-
import json

from odoo import http
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.http import request
from psycopg2 import IntegrityError
from odoo.exceptions import ValidationError


class ContactController(WebsiteForm):

    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        if model_name == 'e2yun.supplier.info' \
                or model_name == 'e2yun.supplier.authentication.info'\
                or model_name == 'e2yun.supplier.user':

            model_record = request.env['ir.model'].sudo().search(
                [('model', '=', model_name), ('website_form_access', '=', True)])
            if not model_record:
                return json.dumps(False)

            try:
                data = self.extract_data(model_record, request.params)
                # 认证信息每次添加都执行这个程序
                if model_name == 'e2yun.supplier.authentication.info' and data.get('record',False):
                    data['record']['supplier_info_id'] = request.session['e2yun_supplier_info_id']

                elif model_name == 'e2yun.supplier.info' and data.get('record',False):
                    try:
                        if data['record']['name']:
                            count = request.env['res.partner'].sudo().search([('name', '=', data['record']['name'])])
                            if count and  len(count) > 0 and count.user_ids.login != data['record']['login_name']:
                                error = {
                                    'name': '联系人名称已经存在，请重新输入'
                                }
                                return json.dumps({'error_fields': error})
                            else:
                                count = request.env['e2yun.supplier.info'].sudo().search_count(
                                    [('name', '=', data['record']['name']),('login_name','!=',data['record']['login_name'])])
                                if count > 0:
                                    error = {
                                        'name': '联系人名称已经存在，请重新输入'
                                    }
                                    return json.dumps({'error_fields': error})
                    except:
                        print('done')
                    # if data['record']['login_name']:
                    #     count = request.env['res.users'].sudo().search_count([('login','=',data['record']['login_name'])])
                    #     if count > 0:
                    #         error = {
                    #             'name': '登录名已经存在，请重新输入'
                    #         }
                    #         return json.dumps({'error_fields': error})
                    #     else:
                    #         count = request.env['e2yun.supplier.info'].sudo().search_count([('login_name', '=', data['record']['login_name'])])
                    #         if count > 0:
                    #             error = {
                    #                 'login_name': '登录名已经存在，请重新输入'
                    #             }
                    #             return json.dumps({'error_fields': error})

                    # if data['record']['password'] != data['record']['confirm_password']:
                    #     error = {
                    #         'confirm_password': '密码不匹配；请重新输入密码'
                    #     }
                    #     return json.dumps({'error_fields': error})

                    #data['record']['supplier_user'] = request.session['e2yun_supplier_user_id']
                    data['record']['customer'] = False
                    data['record']['supplier'] = True
                elif model_name == 'e2yun.supplier.user' and data.get('record',False) :
                    if data['record']['name']:
                        count = request.env['res.users'].sudo().search_count([('login','=',data['record']['name'])])
                        if count > 0:
                            error = {
                                'name': '登录名已经存在，请重新输入'
                            }
                            return json.dumps({'error_fields': error})
                        else:
                            count = request.env['e2yun.supplier.user'].sudo().search_count([('name', '=', data['record']['name'])])
                            if count > 0:
                                error = {
                                    'name': '登录名已经存在，请重新输入'
                                }
                                return json.dumps({'error_fields': error})

                    if data['record']['password'] != data['record']['confirm_password']:
                        error = {
                            'confirm_password': '密码不匹配；请重新输入密码'
                        }
                        return json.dumps({'error_fields': error})
            # If we encounter an issue while extracting data
            except ValidationError as e:
                # I couldn't find a cleaner way to pass data to an exception
                return json.dumps({'error_fields': e.args[0]})

            try:
                if model_name == 'e2yun.supplier.info':
                    supplier_info_obj = http.request.env['e2yun.supplier.info'].sudo()
                    # supplier_info = supplier_info_obj.search([('login_name', '=', data['record']['login_name'])])
                    # 分步添加
                    supplier_info = supplier_info_obj.search([('id', '=', request.session['e2yun_supplier_info_id'])])
                    data['record']['state'] = 'Draft'

                    #保存银行信息时检查
                    if data['record'].get('country_bank',False):
                        if not data['record'].get('enclosure_bank', False) and data['record'].get(
                                'enclosure_bank_value', False):
                            data['record']['enclosure_bank'] = data['record']['enclosure_bank_value']
                        if not data['record'].get('enclosure_bank', False):
                            error = {
                                'enclosure_bank': '开户行资料附件不能为空'
                            }
                            return json.dumps({'error_fields': error})

                    #保存公司信息时检查
                    if data['record'].get('company_name',False):
                        if not data['record'].get('business_license', False) and data['record'].get('business_license_value',False):
                            data['record']['business_license'] = data['record']['business_license_value']

                        if not data['record'].get('image_company', False) and data['record'].get('image_company_value',False):
                            data['record']['image_company'] = data['record']['image_company_value']

                        if not data['record'].get('organization_chart', False) and data['record'].get('organization_chart_value',False):
                            data['record']['organization_chart'] = data['record']['organization_chart_value']

                        if not data['record'].get('image_product', False) and data['record'].get('image_product_value',False):
                            data['record']['image_product'] = data['record']['image_product_value']



                        if not data['record'].get('business_license',False):
                            error = {
                                'business_license': '营业执照不能为空'
                            }
                            return json.dumps({'error_fields': error})

                        if not data['record'].get('image_company',False):
                            error = {
                                'image_company': '公司正门照片不能为空'
                            }
                            return json.dumps({'error_fields': error})

                        if not data['record'].get('organization_chart',False):
                            error = {
                                'organization_chart': '组织架构图不能为空'
                            }
                            return json.dumps({'error_fields': error})



                    supplier_info.write(data['record'])
                    id_record = supplier_info.id
                else:
                    if model_name == 'e2yun.supplier.authentication.info':
                        authentication = http.request.env['e2yun.supplier.authentication.info'].sudo()
                        authentication_info = authentication.search([('supplier_info_id', '=', data['record']['supplier_info_id']),('authentication_type','=',data['record']['authentication_type'])])
                        if authentication_info:
                            authentication_info.unlink()
                        if not data['record'].get('image',False) and data['record']['image_value']:
                            data['record']['image'] = data['record']['image_value']

                        supplier_info_obj = http.request.env['e2yun.supplier.info'].sudo()
                        supplier_info = supplier_info_obj.search([('id', '=', request.session['e2yun_supplier_info_id'])])
                        supplier_info.state = 'Draft'

                    id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
                    if id_record:
                        self.insert_attachment(model_record, id_record, data['attachments'])

            # Some fields have additional SQL constraints that we can't check generically
            # Ex: crm.lead.probability which is a float between 0 and 1
            # TODO: How to get the name of the erroneous field ?
            except IntegrityError:
                return json.dumps(False)

            request.session['form_builder_model_model'] = model_record.model
            request.session['form_builder_model'] = model_record.name
            request.session['form_builder_id'] = id_record
            if model_name == 'e2yun.supplier.user':
                request.session['e2yun_supplier_user_id'] = id_record
            elif model_name == 'e2yun.supplier.info':
                request.session['e2yun_supplier_info_id'] = id_record

            return json.dumps({'id': id_record})

        else:
            return super(ContactController, self).website_form(model_name, **kwargs)
