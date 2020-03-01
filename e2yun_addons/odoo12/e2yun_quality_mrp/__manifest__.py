# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'E2yun MRP features for Quality Control',
    'summary': 'Quality Management with MRP',
    'version': '12.0.1.0.0',
    'category': 'Manufacturing',
    'author': 'Joytao.zhu',
    'website': 'https://www.e2yun.com',
    'depends': ['mrp','e2yun_quality_stock'],
    "excludes": ["quality_control_stock"],
    'data':['views/product_category_view.xml',
            'views/product_template_view.xml',
            'views/mrp_production_view.xml',
            'views/mrp_workorder_view.xml',
            'views/qc_inspection_view.xml',
    ],
    'license': 'AGPL-3',
}
