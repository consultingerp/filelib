{
    'name': 'Friendly Website Error',
    'category': 'Website',
    'author': 'TheOdooGuy',
    'website': 'https://www.theodooguy.com',
    'summary': 'Style Odoo website errors and make the message more user friendly',
    'depends': ['website', 'base'],
    'images': ['images/main.png', 'images/main_screenshot.png'],
    'data': [
        'views/exceptions_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
