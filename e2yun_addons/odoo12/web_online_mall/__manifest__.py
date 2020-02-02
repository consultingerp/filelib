# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '在线商城',
    'category': 'Website',
    'summary': '在线商城 ',
    'description': """在线商城.""",
    'application': True,
    'depends': [
        'web', 'website', 'im_livechat', 'mail', 'web_user_center'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/online_mall_templates.xml',
        'views/online_mall_views.xml',
        'views/product_info_views.xml'
    ],
    'qweb': [

    ],
    'license': 'OEEL-1',
    'installable': True,
    'auto_install': False,
    'active': False,
    'web': True,
}
