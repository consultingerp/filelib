# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '个人中心',
    'category': 'Website',
    'summary': '个人中心信息 ',
    'description': """个人中心.""",
    'application': True,
    'depends': [
        'base', 'web', 'website',
    ],
    'data': [
        'security/user_center_security.xml',
        'security/ir.model.access2.csv',
        'views/web_user_center_templates.xml',
        'views/user_center_menus.xml',
        'views/user_center.xml',
        'views/usercenter_menu.xml',
        'views/usercenter_menu_seq.xml',
        'views/structure_iframe_page.xml',
        'views/user_info_page.xml',
        'views/login_page.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'license': 'OEEL-1',
    'installable': True,
    'auto_install': False,
    'active': False,
    'web': True,
}
