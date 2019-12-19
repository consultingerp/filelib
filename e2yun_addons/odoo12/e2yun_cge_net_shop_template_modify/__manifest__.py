# -*- coding: utf-8 -*-
{
    'name': "e2yun_cge_net_shop_template_modify",

    'summary': """
        网上商城订单页面模板修正""",

    'description': """
        解决订单页面城市显示异常
    """,

    'author': "Kangyu.Wang",
    'website': "www.e2yun.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','website_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}