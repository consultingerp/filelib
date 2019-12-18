# -*- coding: utf-8 -*-
{
    'name': "e2yun_cge_net_shop_default",

    'summary': """
        网上商城/我的简介增加默认值""",

    'description': """
        动作中 增加context，在default_get中判断上下文，增加'销售员'默认值。在动作中增加'是卖家'的默认值
    """,

    'author': "Li Haonan",
    'website': "www.e2yun.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}