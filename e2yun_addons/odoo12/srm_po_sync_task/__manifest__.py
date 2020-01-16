# -*- coding: utf-8 -*-
{
    'name': "SRM Po Sync",
    'summary': """PO同步""",
    'description': """ PO同步""",
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "author": "chuqiu.xu",
    "website": "https://www.e2yun.com/",
    'depends': ['base','web','product','purchase'],
    'data': ['views/srm_product_category_view.xml',
             'qweb/yc_po_pdf.xml'],
    'installable': True,
    'auto_install': False,
    'application': True
}