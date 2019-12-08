# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '个人中心',
    'category': 'Website',
    'summary': '个人中心信息 ',
    'description': """个人中心.""",
    'application': True,
    'depends': [
        'base', 'web', 'website', 'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/web_user_center_templates.xml',
        'views/user_center.xml',
        'views/user_center_menus.xml'
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
