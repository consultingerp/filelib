{
    'name': "潜在供应商管理",
    'summary': """
        Supplier Approver Info
        """,
    'description': """
       必须在工作流中，的倒数第二个流程中，增加python的代码方式执行：obj.customer_transfer_to_normal()，
       然后必须在流程中增加技术命名为'done'的流程节点，来座位obj.customer_transfer_to_normal()里的流程变更控制。
    """,
    'author': "Feng Zhou,liqiang",
    'website': "http://www.e2yun.com",
    'category': 'Purchase',
    'version': '0.1',
    'depends': ['base', 'purchase','website','e2yun_partner_address' ],
    'data': [
        'security/ir.model.access.csv',
        'data/website_supplier_data.xml',
        'data/ir_sequence_data.xml',
        'views/e2yun_supplier_info_view.xml',
        'views/res_partner_view.xml',
        'static/src/xml/register.xml',
        'static/src/xml/register_index.xml',
        'static/src/xml/register_index_2.xml',
        'static/src/xml/register_index_3.xml',
        'static/src/xml/register_authentication_info.xml',
        'static/src/xml/register_base_info.xml',
        'static/src/xml/register_done.xml',
        'static/src/xml/website_layout.xml',
    ],
    'installable': True,
}
# -*- coding: utf-8 -*-
