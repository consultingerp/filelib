# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "SRM Delivery Order",
    "summary": "SRM Delivery Order",
    "category": "SRM Management",
    "description": " SRM 交货单 ",
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "author": "liqiang",
    "website": "https://www.e2yun.com/",
    "depends": ["base","purchase","stock","srm_base"],
    "data": [
        "views/delivery_order_line_rep_view.xml",
        "views/delivery_order_print.xml",
        "views/delivery_order_rep_view.xml",
        "views/delivery_order_view.xml",
        "views/report_template_delivery.xml",
        "views/sequence_data.xml",
        "views/delivery_order_import.xml",
        "views/menu_view.xml",
    ],
    "installable": True,
}
