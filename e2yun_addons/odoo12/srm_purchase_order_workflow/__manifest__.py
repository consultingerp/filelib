# -*- coding: utf-8 -*-
{
    'name': "SRM Purchase Order Workflow",
    "summary": "Purchase",
    "category": "Purchase Management",
    "description": "采购订单工作流",
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "author": "chuqiu.xu",
    "website": "https://www.e2yun.com/",
    'depends': ['purchase'],
    'data': [
        'views/view_purchase_order.xml',
        'views/purchase_order_email_template.xml',
    ],
    "installable": True,
    'application': True,
    'auto_install': False,
}