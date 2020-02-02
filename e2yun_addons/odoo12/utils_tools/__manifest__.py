# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '通用工具类',
    'category': 'Website',
    'summary': '通用工具 ',
    'description': """通用工具.""",
    'application': True,
    'depends': [
        'web', 'base'
    ],
    'data': [
        'security/ir.model.access2.csv',
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
