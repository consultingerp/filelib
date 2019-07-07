# Copyright 2016 Siddharth Bhalgami <siddharth.bhalgami@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "E2yun Cards OCR",
    "summary": "using baidu aip OCR to identify business Cards",
    "version": "12.0.1.0.0",
    "category": "Customer Relationship Management",
    "website": "http://e2yun.com",
    "author": "Joytao, "
              "e2yun.com ",
    "license": "LGPL-3",
    "data": [
        "views/assets.xml",
        "views/contact_view.xml",
        "views/contact_import_wizard_view.xml",
    ],
    "depends": [
        "web","contacts"
    ],
    "qweb": [
        "static/src/xml/e2yun_cards_ocr.xml",
    ],
    "installable": True,
}
