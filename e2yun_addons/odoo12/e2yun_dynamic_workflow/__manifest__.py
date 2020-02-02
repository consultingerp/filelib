# -*- coding: utf-8 -*-
##########################################################
###                 Disclaimer                         ###
##########################################################
### Lately, I started to get very busy after I         ###
### started my new position and I couldn't keep up     ###
### with clients demands & requests for customizations ###
### & upgrades, so I decided to publish this module    ###
### for community free of charge. Building on that,    ###
### I expect respect from whoever gets his/her hands   ###
### on my code, not to copy nor rebrand the module &   ###
### sell it under their names.                         ###
##########################################################

{
    'name': 'E2yun Dynamic Workflow Builder',
    'version': '12.0.0.1',
    'sequence': '10',
    'category': 'Extra Tools',
    'author': 'Joytao.zhu',
    'website': 'http://e2yun.cn',
    'summary': 'E2yun Dynamic Workflow Builder',
    'images': [
        'static/description/banner.png',
    ],
    'description': """
E2yun Dynamic Workflow Builder
==============================
* You can build dynamic workflow for any model.
Base on the module odoo_dynamic_workflow,fix bug and support 12.0.
The original author Mohamed Youssef
http://mohamedhammad.info/
""",
    'data': [
        'templates/webclient_templates.xml',
        'security/groups.xml',
        'security/ir.model.access2.csv',
        'views/menu.xml',
        'wizards/views/e2yun_workflow_refuse_wizard_view.xml',
        'wizards/views/e2yun_workflow_update_wizard_view.xml',
        'views/e2yun_workflow_view.xml',
        'views/ir_actions_server_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
