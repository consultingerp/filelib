# -*- coding: utf-8 -*-
{
    'name': "e2yun_sales_report",

    'summary': """
        销售明细报表""",

    'description': """
        销售明细报表
    """,

    'author': "Li Haonan",
    'website': "http://www.e2yun.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Report',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'e2yun_hhjc_sale_order_extends'],

    # always loaded
    'data': [
        'security/ir.model.access2.csv',
        'views/views.xml',
        'views/newmodels.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/outbound_button_template.xml',
        # 'static/src/xml/sales_report_tamplate.xml',
    ],
    'installable': True
}