# -*- coding: utf-8 -*-
{
    'name': "outbound_sync_from_pos",

    'summary': """
        从pos同步出库报表数据源""",

    'description': """
    """,

    'author': "Li Haonan",
    'website': "https://www.e2yuun.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'e2yun_sales_report'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/outbound_report_dashboard.xml',
    ],
    'qweb': [
        'static/src/xml/outbound_pos_button_template.xml',
             ],
}
