# -*- coding: utf-8 -*-
{
    'name': "Supplier Recruitment Interview Forms",
    'version': '1.0',
    'category': 'Purchases',
    'summary': 'Surveys',
    'description': """
        Use interview forms during recruitment process.
        This module is integrated with the survey module
        to allow you to define interviews for different jobs.
    """,
    'depends': ['survey', 'e2yun_supplier_recruitment'],
    'data': [
        'security/supplier_recruitment_survey_security.xml',
        'security/ir.model.access.csv',
        'data/survey_survey_data.xml',
        'views/supplier_job_views.xml',
        'views/supplier_applicant_views.xml',
    ],
    'demo': [
        'data/supplier_job_demo.xml',
    ],
    'test': ['test/recruitment_process.yml'],
    'auto_install': False,
}
