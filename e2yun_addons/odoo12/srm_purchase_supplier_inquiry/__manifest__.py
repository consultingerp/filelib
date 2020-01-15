# -*- coding: utf-8 -*-
{
    'name': "SRM Purchase Supplier Inquiry",
    'summary': """Supplier mail inquiry""",
    'description': """
            Supplier mail inquiry
    """,
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "author": "chuqiu.xu",
    "website": "https://www.e2yun.com/",
    'depends': ['website','purchase','web','mail'],
    'data': [
        'views/website_quotation.xml',
        'data/purchase_supplier_view.xml'
    ],
    "installable": True,
    'application': True,
    'auto_install': False,
}