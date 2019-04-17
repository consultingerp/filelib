# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Online Supplier Jobs',
    'category': 'Website',
    'version': '1.0',
    'summary': 'Supplier Job Descriptions And Application Forms',
    'description': """
Odoo Contact Form
====================

        """,
    'depends': ['website_partner', 'e2yun_supplier_recruitment', 'website_mail', 'website_form'],
    'data': [
        'security/ir.model.access.csv',
        'security/website_supplier_recruitment_security.xml',
        'data/config_data.xml',
        'views/website_supplier_recruitment_templates.xml',
        'views/supplier_recruitment_views.xml',
    ],
    'demo': [
        'data/supplier_job_demo.xml',
    ],
    'installable': True,
}
