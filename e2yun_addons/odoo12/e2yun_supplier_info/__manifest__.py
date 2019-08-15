{
    'name': "潜在供应商管理",

    'summary': """
        Supplier Approver Info
        """,

    'description': """
       必须在工作流中，的倒数第二个流程中，增加python的代码方式执行：obj.customer_transfer_to_normal()，
       然后必须在流程中增加技术命名为'done'的流程节点，来座位obj.customer_transfer_to_normal()里的流程变更控制。
    """,

    'author': "Feng Zhou",
    'website': "http://www.e2yun.com",

    'category': 'Purchase',
    'version': '0.1',

    'depends': ['base', 'purchase', ],

    'data': [
        'views/e2yun_supplier_info_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    # 'installable': False,
}
# -*- coding: utf-8 -*-
