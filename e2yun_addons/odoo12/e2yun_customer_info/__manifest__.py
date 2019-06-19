{
    'name': "e2yun_customer_info",

    'summary': """
        Customer Approver Info
        """,

    'description': """
       必须在工作流中，的倒数第二个流程中，增加python的代码方式执行：obj.customer_transfer_to_normal()，
       然后必须在流程中增加技术命名为'done'的流程节点，来座位obj.customer_transfer_to_normal()里的流程变更控制。
    """,

    'author': "Feng Zhou",
    'website': "http://www.e2yun.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'crm', 'sales_team'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/access_restricted_security.xml',
        'views/e2yun_customer_info_view.xml',
        'views/crm_team_view.xml',
        'views/mail_activity_view.xml',
        'views/res_partner_view.xml',
        'views/res_currency_view.xml',
        'views/crm_lead_view.xml',

        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
