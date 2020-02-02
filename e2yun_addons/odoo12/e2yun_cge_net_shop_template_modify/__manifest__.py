# -*- coding: utf-8 -*-
{
    'name': "e2yun_cge_net_shop_template_modify",

    'summary': """
        网上商城外部页面 末班订正相关""",

    'description': """
        网上商城外部页面 末班订正相关
        1. 解决订单页面城市显示异常
        2. 支付方式加上图标
    """,

    'author': "Kangyu.Wang",
    'website': "www.e2yun.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_sale', 'payment', 'odoo_website_marketplace'],

    # always loaded
    'data': [
        # 'security/ir.model.access2.csv',
        'views/views.xml',
    ],
    'installable': True
}