# -*- coding: utf-8 -*-

from odoo import models, fields, api, http
import werkzeug.utils


# class CurrentUserInfoModify(models.Model):
#     _inherit = 'res.partner'

class UserCenterUserExtends(models.Model):
    _inherit = 'res.users'

    def button_back_to_user_center(self):
        return {
                'type': 'ir.actions.act_url',
                'url': '/user-center',
                'target': 'self',
                'res_id': self.id,
            }


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
        # is_customer = user.partner_id.customer
        function = user.function
        if function:
            return http.request.render('e2yun_user_center.e2yun_user_center_index_employee_template',
                                       {'current_user': user})
        else:
            return http.request.render('e2yun_user_center.e2yun_user_center_index_customer_template',
                                       {'current_user': user})

    # 个人中心用户信息页面
    @http.route('/user-center/my-info', auth='user')
    def my_info(self, **kwargs):
        user = http.request.env.user
        # is_customer = user.partner_id.customer
        function = user.function
        if function:
            return http.request.render('e2yun_user_center.e2yun_user_center_my_info_employee_template',
                                       {'current_user': user})
        else:
            return http.request.render('e2yun_user_center.e2yun_user_center_my_info_customer_template',
                                       {'current_user': user})

    # # 个人中心跳转到系统内部“个人信息修改”页面
    # @http.route('/user-center/my-settings', auth='user')
    # def my_settings(self, **kwargs):
    #     user = http.request.env.user
    #     partner_id = user.partner_id.id
    #     url = "/web?#id=" + str(partner_id) + "&action=51&model=res.partner&view_type=form&menu_id=111"
    #     return werkzeug.utils.redirect(url)

    # 个人中心跳转到Odoo应用中心首页
    @http.route('/user-center/back-to-app-center', auth='user')
    def back_to_app_center(self, **kwargs):
        return werkzeug.utils.redirect('/web')

    # 个人中心跳转到附近门店页面
    @http.route('/user-center/nearby-shop', auth='user')
    def nearby_shop(self):
        return werkzeug.utils.redirect('/web#action=591&menu_id=111')

    # 个人中心跳转到CRM页面
    @http.route('/user-center/jump-to-crm', auth='user')
    def jump_to_crm(self, **kwargs):
        return werkzeug.utils.redirect('/web#action=51&model=res.partner&view_type=kanban&menu_id=111')

    # 个人中心跳转到日历页面
    @http.route('/user-center/jump-to-discussion', auth='user')
    def jump_to_discussion(self, **kwargs):
        return werkzeug.utils.redirect('/web#action=101&active_id=mailbox_inbox&menu_id=83')

    # 个人中心跳转到日历页面
    @http.route('/user-center/jump-to-calendar', auth='user')
    def jump_to_calendar(self, **kwargs):
        return werkzeug.utils.redirect('/web#action=116&model=calendar.event&view_type=calendar&menu_id=90')

    # 个人中心跳转到我的导购页面
    @http.route('/user-center/my-guide', auth='user')
    def my_sales_manager(self, **kwargs):
        user = http.request.env.user
        related_guides = user.related_guide
        return http.request.render('e2yun_user_center.e2yun_user_center_my_guide_template',
                                   {'related_guides': related_guides})

    # 个人中心跳转的到更改用户信息页面
    @http.route('/user-center/user-info-modify', auth='user')
    def user_info_modify(self, **kwargs):
        user = http.request.env.user
        user_id = user.id
        view_pool = http.request.env['ir.ui.view']
        view_name = 'Current User Info'
        view_id = view_pool.search([('name', 'like', view_name)]).id
        url = '/web#id=' + str(user_id) + '&model=res.users&view_type=form&view_id=' + str(view_id)
        return werkzeug.utils.redirect(url)

    # 个人中心跳转到我的优惠券页面
    @http.route('/user-center/my_coupon', auth='user')
    def my_coupon(self, **kwargs):
        # action_pool = http.request.env['ir.actions.act_window']
        # action_name = '已领优惠券'
        # action_id = action_pool.search([('name', 'like', action_name)]).id
        # url = 'web?#action=' + str(action_id) + '&model=sale.coupon&view_type=list'
        url = '/web?#action=589&model=sale.coupon&view_type=list&menu_id=191'
        return werkzeug.utils.redirect(url)

    # 个人中心 用户信息界面 跳转到个人二维码界面
    @http.route('/user_center/my_qrcode', auth='user')
    def my_qrcode(self, **kwargs):
        user = http.request.env.user
        return http.request.render('e2yun_user_center.e2yun_user_center_my_qrcode_template', {'current_user': user})
