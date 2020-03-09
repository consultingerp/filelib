# Copyright 2018 Camptocamp SA
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2016 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Base Property ",
    "summary": "Property use for QC lots or Order",
    "version": "12.0.1.0.0",
    "author": "joytao.zhu@e2yun.com",
    "website": "https://www.e2yun.com",
    "category": "Warehouse Management",
    "depends": [
        "stock",
    ],
    "data": [
        "security/base_properties_access.xml",
        "security/ir.model.access.csv",
        "views/base_properties_views.xml",
        "views/stock_production_lot_views.xml",

    ],
    "license": "LGPL-3",
    "installable": True,
}
