# -*- coding: utf-8 -*-
{
    'name': "E2yun Blog Post Extends",

    'summary': """
        客户案例增加发送到微信
        """,

    'description': """
        客户案例增加发送到微信
    """,

    'author': "Feng Zhou",
    'website': "http://www.e2yun.cn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_blog', 'wx_tools'],

    # always loaded
    'data': [
        'views/views.xml',
        'static/src/xml/template.xml',
        # 'views/blog_post_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
