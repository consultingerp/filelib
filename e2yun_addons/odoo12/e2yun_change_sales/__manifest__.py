# Copyright 2016 Siddharth Bhalgami <siddharth.bhalgami@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "E2yun HHJC Change Sales",
    "summary": "批量更改客户导购:联系人&销售订单",
    "version": "12.0.1.0.0",
    "category": "CRM",
    "website": "http://e2yun.com",
    "author": "Li Haonan, "
              "e2yun.com ",
    "license": "LGPL-3",
    "data": [
        "views/change_sales.xml",
        # "views/sale_order_change_sales.xml",
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
     "depends": [
        "base", 'sale'
    ],
    "installable": True
}