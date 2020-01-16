# -*- coding: utf-8 -*-
{
    "name": "SRM Account Order",
    'description': """
        SRM 对账单
   """,
    "version": "11.0.1.0.0",
    "depends": ["base","stock", "purchase","website","mail"],
    "author": "liqiang",
    'license': 'AGPL-3',
    'website': 'http://www.e2yun.com',
    'data': [
        'views/srm_account_order_view.xml',
        'views/srm_account_order_sequence.xml',
        'views/srm_account_order_rep_view.xml',
        'views/website_quotation.xml',
        'data/srm_invoice_inquiry_redirect.xml',
        'views/srm_account_emil.xml',
        'views/menu_view.xml',
        #'views/srm_account_pdf.xml',
    ],
    'installable': True,
    'auto_install': False,
}
