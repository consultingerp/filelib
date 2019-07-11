# -*- coding: utf-8 -*-

from odoo import models, fields, api, http
import werkzeug.utils

class UserCenter(http.Controller):

    # @api.one
    # def _get_current_login_user(self):
    #     user_obj = self.env['res.users'].search([])
    #     for user_login in user_obj:
    #         current_login = self.env.user
    #         if user_login == current_login:
    #             self.processing_staff = current_login
    #             return

    # 个人中心首页
    @http.route('/user-center', auth='user')
    def main_page(self, **kwargs):
        user = http.request.env.user
        # 通过res.partner模型下的customer属性，判断是否为内部用户，来跳转到不同样式的个人中心页面
        is_customer = user.partner_id.customer
        if is_customer:
            return http.request.render('e2yun_user_center.e2yun_user_center_index_customer_template', {'current_user': user})
        else:
            return http.request.render('e2yun_user_center.e2yun_user_center_index_employee_template', {'current_user': user})

    # 个人中心用户信息页面
    @http.route('/user-center/my-info', auth='user')
    def my_info(self, **kwargs):
        user = http.request.env.user
        is_customer = user.partner_id.customer
        if is_customer:
            return http.request.render('e2yun_user_center.e2yun_user_center_my_info_customer_template', {'current_user': user})
        else:
            return http.request.render('e2yun_user_center.e2yun_user_center_my_info_employee_template', {'current_user': user})

    # 个人中心跳转到系统内部“个人信息修改”页面
    @http.route('/user-center/my-settings', auth='user')
    def my_settings(self, **kwargs):
        user = http.request.env.user
        partner_id = user.partner_id.id
        url = "/web?#id=" + str(partner_id) + "&action=51&model=res.partner&view_type=form&menu_id=111"
        return werkzeug.utils.redirect(url)

    # 个人中心跳转到Odoo应用中心首页
    @http.route('/user-center/back-to-app-center', auth='user')
    def back_to_app_center(self, **kwargs):
        return werkzeug.utils.redirect('/web')

    # 个人中心跳转到附近门店页面
    @http.route('/user-center/nearby-shop', auth='user')
    def nearby_shop(self):
        return werkzeug.utils.redirect('/web#action=604&model=crm.team&view_type=kanban&menu_id=111')

    # 个人中心跳转到我的导购页面
    @http.route('/user-center/my-guide', auth='user')
    def my_sales_manager(self, **kwargs):
        user = http.request.env.user
        related_guides = user.related_guide
        return http.request.render('e2yun_user_center.e2yun_user_center_my_guide_template', {'related_guides': related_guides})
