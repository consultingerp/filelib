# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '在线客服聊天',
    'category': 'Website',
    'summary': '在线客服聊天 ',
    'description': """在线客服聊天.""",
    'application': True,
    'depends': [
        'web', 'website', 'im_livechat', 'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
    'qweb': [

    ],
    'license': 'OEEL-1',
    'installable': True,
    'auto_install': False,
    'active': False,
    'web': True,
}
