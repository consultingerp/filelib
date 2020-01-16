# -*- coding: utf-8 -*-
{
    'name': "SRM Package",

    'summary': """ Package Manager""",

    'description': """
        SRM 包裹
    """,
    'author': "liqiang",
    'website': "http://www.e2yun.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'SRM Management',
    'version': '12.0.1.0.0',
    # any module necessary for this one to work correctly
    'depends': ['base','purchase','stock','srm_delivery_order'],
    # always loaded
    'data': [
        'views/sequence_data.xml',
        'views/srm_pack_view.xml',
        'views/report_template_packing_tag.xml',
        'views/tag_print.xml',
    ],
    "installable": True,
}