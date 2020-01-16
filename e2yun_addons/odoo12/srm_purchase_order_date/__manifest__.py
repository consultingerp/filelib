# -*- coding: utf-8 -*-
{
    'name': "SRM Purchase Order Date",

    'summary': """ SRM Purchase Order Date""",

    'description': """
        SRM 采购订单增加日期
    """,
    'author': "liqiang",
    'website': "http://www.e2yun.com",
    'category': 'SRM Management',
    'version': '12.0.1.0.0',
    'depends': ['base','purchase'],
    'data': [
        'views/view_purchase_order.xml',
    ],
    "installable": True,
}