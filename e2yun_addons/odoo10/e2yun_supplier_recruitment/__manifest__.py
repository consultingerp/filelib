# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Suppler Recruitment Process',
    'version': '1.0',
    'category': 'Purchases',
    'sequence': 90,
    'summary': 'Jobs, Recruitment, Applications, Job Interviews',
    'description': """
Manage job positions and the recruitment process
================================================

This application allows you to easily keep track of jobs, vacancies, applications, interviews...

It is integrated with the mail gateway to automatically fetch email sent to <jobs@yourcompany.com> in the list of applications. It's also integrated with the document management system to store and search in the CV base and find the candidate that you are looking for. Similarly, it may integrated with the survey module to allow you to define interviews for different jobs.		
You can define the different phases of interviews and easily rate the applicant from the kanban view.
""",
    'website': 'https://www.odoo.com/page/recruitment',
    'depends': [
        'decimal_precision',
        'product',
        'purchase',
        'calendar',
        'fetchmail',
        'web_kanban_gauge',
        'utm',
        'document',
        'web_tour',
    ],
    'data': [
        'security/supplier_recruitment_security.xml',
        'security/ir.model.access.csv',
        'data/supplier_recruitment_data.xml',
        'views/supplier_recruitment_views.xml',
        'report/supplier_recruitment_report_views.xml',
        'views/supplier_recruitment_config_settings_views.xml',
        'views/supplier_recruitment_templates.xml',
        'views/supplier_product_views.xml',
        'views/supplier_job_views.xml',
        'views/tour_views.xml',
    ],
    'demo': ['data/supplier_recruitment_demo.xml'],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
