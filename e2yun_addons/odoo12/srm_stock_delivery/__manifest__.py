# -*- coding: utf-8 -*-
{
    'name': "SRM Stock Delivery",
    'summary': """
        SRM Stock Delivery""",
    'description': """
        SRM 收货操作
    """,
    'author': "liqiang",
    'website': "http://www.e2yun.com",
    'category': 'SRM Management',
    'version': '12.0.1.0.0',
    'depends': ['base','purchase','srm_delivery_order','stock','web'],
    'data': [
        'views/delivery.xml',
        'views/delivery_kanban.xml',
        'views/sap_voucher_view.xml',
        'views/stock_return_picking_view.xml',
        #'static/src/xml/template.xml',
    ],
    'qweb': ['static/src/xml/template.xml',],
    'installable': True,
    'auto_install': False,
}