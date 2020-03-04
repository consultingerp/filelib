# -*- coding: utf-8 -*-
{
    'name': 'E2yun Agreement Extend ',
    'version': '12.0.0.1',
    'depends': ['agreement','agreement_legal'],
    'author': 'chuqiu.xu',
    'website': 'http://e2yun.cn',
    'summary': '',
    'description': """内部合同项目扩展 """,
    'data': [
        'security/access_restricted_security.xml',
        'views/agreement_extend.xml',
        'views/agreement_sequence.xml',
        'data/mail_template_data.xml',
        'views/file_upload.xml',
        'views/agreement_crm_lead_view_extend.xml',
        'views/agreement_Income_type.xml',

    ],
    'installable': True,
    'auto_install': False,

}
