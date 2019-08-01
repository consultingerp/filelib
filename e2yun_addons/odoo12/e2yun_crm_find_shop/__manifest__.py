# Copyright 2016 Siddharth Bhalgami <siddharth.bhalgami@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "E2yun Shop Find",
    "summary": "CRM客户门店查询",
    "version": "12.0.1.0.0",
    "category": "CRM",
    "website": "http://e2yun.com",
    "author": "Li Haonan, "
              "e2yun.com ",
    "license": "LGPL-3",
    "data": [
        "views/crm_find_shop.xml",
        "views/gaode_template.xml",
    ],
    "depends": [
        "crm", "base", "e2yun_crm_shop_maintain", "sales_team","wx_tools"
    ],
    "installable": True
}