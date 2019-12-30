# -*- coding: utf-8 -*-
{
    'name': 'E2yun Agreement Docx Import ',
    'version': '12.0.0.1',
    'depends': ['agreement','agreement_legal'],
    'author': 'chuqiu.xu',
    'website': 'http://e2yun.cn',
    'summary': '',
    'description': """ docx import""",
    'data': [
        'views/view.xml',
        'views/agreement_extend.xml',
        'views/agreement_word_data.xml',
        'views/agreement_placeholder.xml',
        'views/agreement_recital_extend.xml',
        'qweb/agreement_word_edit.xml',

    ],
    'installable': True,
    'auto_install': False,

}
