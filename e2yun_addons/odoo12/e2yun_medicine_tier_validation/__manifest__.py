# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "E2yun Medicine Tier Validation",
    "summary": "Extends the functionality of Demo to "
               "support a tier validation process.",
    "version": "12.0.1.0.0",
    "category": "Medicine",
     'website': 'http://e2yun.cn',
    "author": "liqiang",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base_tier_validation","mrp","purchase"
    ],
    "data": [
        "views/purchase_order_view.xml",
        "views/production_view.xml",
    ]
}
