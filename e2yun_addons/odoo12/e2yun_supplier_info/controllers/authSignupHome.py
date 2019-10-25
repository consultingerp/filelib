# -*- coding: utf-8 -*-
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
from odoo.http import request
from odoo import http, _

class AuthSignupHome(AuthSignupHome):

    @http.route('/supplier/auth_register_base_info/', auth='public', website=True)
    def auth_base_info(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        login = qcontext.get('login', False)
        if login:
            user = request.env['e2yun.supplier.user'].sudo().search([('name', '=', login)], limit=1)
            db = request.env.cr.dbname
            if user:
                request.session.authenticate(db, login, user.password)
        if qcontext.get('redirect',False) == 'base_info':
            return request.redirect("/supplier/register_base_info/")
        elif qcontext.get('redirect',False) == 'index':
            return request.redirect("/supplier/register/")
        else:
            return request.redirect("/web/login")




    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = { key: qcontext.get(key) for key in ('login', 'password','vat','company_name') }
        if not values:
            raise UserError(_("The form was not properly filled in."))
        #验证公司名称
        supplier_info = request.env['e2yun.supplier.info'].sudo()
        partner_info = request.env['res.partner'].sudo()
        user_info = request.env['res.users'].sudo()
        if values.get('company_name'):

            name_count = supplier_info.search_count([('company_name','=',values.get('company_name'))])
            if name_count > 0:
                raise UserError("公司名称已经存在，请检查输入")

            name_count = partner_info.search_count([('company_name', '=', values.get('company_name'))])
            if name_count > 0:
                raise UserError("公司名称已经存在，请检查输入")

            name_count = user_info.search_count([('company_name', '=', values.get('company_name'))])
            if name_count > 0:
                raise UserError("公司名称已经存在，请检查输入")

        #验证统一社会信用代码
        if values.get('vat'):
            vat_count = supplier_info.search_count([('vat', '=', values.get('vat'))])
            if vat_count > 0:
                raise UserError("统一社会信用代码已经存在，请检查输入")

            vat_count = partner_info.search_count([('vat', '=', values.get('vat'))])
            if vat_count > 0:
                raise UserError("统一社会信用代码已经存在，请检查输入")

            vat_count = user_info.search_count([('vat', '=', values.get('vat'))])
            if vat_count > 0:
                raise UserError("统一社会信用代码已经存在，请检查输入")

        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))

        values['name'] = values.get('login')

        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)

        if values.get('login',False) and values.get('password',False):
            su = request.env['e2yun.supplier.user'].sudo()
            su_info = su.search([('name','=',values.get('login'))])
            if su_info:
                su_info.write({'password':values.get('password'),'confirm_password':values.get('password')})
            else:
                su.create({'name':values.get('login'),'password':values.get('password'),'confirm_password':values.get('password')})

        request.env.cr.commit()
        template_id = request.env.ref('supplier_register.register_user_mail_template')
        user = request.env.user
        request.env['mail.thread'].sudo().message_post_with_template(
            template_id.id,
            model='res.users',
            res_id=user.id,
            composition_mode='mass_mail',
            partner_ids=user.partner_id.ids,
        )