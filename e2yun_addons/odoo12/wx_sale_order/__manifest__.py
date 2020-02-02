# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': '销售订单发送微信',
    'category': 'Website',
    'summary': '销售订单发送微信 ',
    'description': """销售订单发送微信.""",
    'application': True,
    'depends': [
        'web','sale_management'
    ],
    'data': [
        'security/ir.model.access2.csv',
        'views/templates.xml',
        'views/sale_order_test.xml'
    ],
    'qweb': [

    ],
    'license': 'OEEL-1',
    'installable': True,
    'auto_install': False,
    'active': False,
    'web': True,
}
