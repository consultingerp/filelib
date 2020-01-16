# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "SRM Base",
    "summary": "SRM Base",
    "category": "SRM Management",
    "description": " SRM 基础模块，主数据增强，主菜单创建 ",
    "version": "12.0",
    "license": "LGPL-3",
    "author": "liqiang",
    "website": "https://www.e2yun.com/",
    "depends": ["base","purchase","stock"],
    "data": [
        "views/res_partner_view.xml",
        "views/product_supplierinfo_view.xml",
        "views/res_company_view.xml",
        "views/stock_picking_type_view.xml",
        "views/stock_warehouse_view.xml",
        "views/base_menu.xml",
        "views/purchase_order_view.xml",
    ],
    "installable": True,
}
