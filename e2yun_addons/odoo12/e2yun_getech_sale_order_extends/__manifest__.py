# -*- coding: utf-8 -*-
{
    'name': 'E2yun getech Sale Order Extends',
    'version': '12.0.0.1',
    'sequence': '10',
    'category': 'sale',
    'depends': ['sale', 'product'],
    'author': 'FengZhou',
    'website': 'http://e2yun.cn',
    'summary': 'Sale Order Extends',
    'description': """格创东智销售订单扩展""",
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/category_view.xml',
        'data/data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
