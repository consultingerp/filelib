# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Mail message file',
    'category': 'Hidden',
    'summary': 'Portal回复信息增加上传文件',
    'version': '0.1',
    'description': """
 Website 回复信息可传文件
""",
    'depends': ['website', 'mail'],
    'data': [
        'views/portal_chatter.xml',
    ],
    'qweb': [
        'static/src/xml/portal_chatter_messagefiles.xml'
    ]
}
