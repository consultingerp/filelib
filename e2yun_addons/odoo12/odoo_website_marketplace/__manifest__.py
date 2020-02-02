# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Odoo Multi Seller Marketplace",
    "version" : "12.0.0.4",
    "category" : "eCommerce",
    'summary': 'This apps helps to enable Online multi seller marketplace on Odoo to sell thier product, manage product, manage orders and their profile.',
    "description": """

    Purpose :-
This Module Helps Odoo Website Marketplace.
marketplace in Odoo
multi vendor marketplace in Odoo
multivendor marketplace in Odoo
multi-seller marketplace
odoo multi-seller marketplace
multi-vendor marketplace
multiseller marketplace in Odoo
ecommerce marketplace in Odoo
Odoo marketplace
Odoo multiplevendor
Odoo multi seller
marketplace for multivendor 
Odoo marketplace multi seller
Amazon Marketplace
e-commerce platform
Odoo e-commerce platform
third-party sellers
online marketplace
Odoo thirdparty marketplace
Marketplace For All Buy And Sell Online
Odoo Multi Vendor Marketplace for your eCommerce Platform
Multi Vendor Marketplace for your eCommerce Platform
Marketplace for your eCommerce Platform
Marketplace eCommerce Platform
odoo vendor marketplace supplier marketplace odoo
odoo seller marketplace seller marketplace odoo
odoo vendor marketplace supplier marketplace odoo
multi supplier marketplace on odoo
odoo marketplace for vendor
odoo marketplace for supplier
odoo marketplace for seller

odoo website vendor marketplace website supplier marketplace odoo
odoo website seller marketplace website seller marketplace odoo
odoo website vendor marketplace website supplier marketplace odoo
website multi supplier marketplace on odoo
odoo website marketplace for vendor
odoo website marketplace for supplier
odoo website marketplace for seller

odoo webshop vendor marketplace webshop supplier marketplace odoo
odoo webshop seller marketplace webshop seller marketplace odoo
odoo webshop vendor marketplace webshop supplier marketplace odoo
webshop multi supplier marketplace on odoo
odoo webshop marketplace for vendor website marketplace
odoo webshop marketplace for supplier website marketplace
odoo webshop marketplace for seller website marketplace

odoo shop vendor marketplace shop supplier marketplace odoo
odoo shop seller marketplace shop seller marketplace odoo
odoo shop vendor marketplace shop supplier marketplace odoo
shop multi supplier marketplace on odoo
odoo shop marketplace for vendor webshop marketplace
odoo shop marketplace for supplier webshop marketplace
odoo shop marketplace for seller webshop marketplace


odoo webstore vendor marketplace webstore supplier marketplace odoo
odoo webstore seller marketplace webstore seller marketplace odoo
odoo webstore vendor marketplace webstore supplier marketplace odoo
webstore multi supplier marketplace on odoo
odoo webstore marketplace for vendor webstore marketplace
odoo webstore marketplace for supplier webstore marketplace
odoo webstore marketplace for seller webstore marketplace


marketplace Odoo 
This Module Helps Odoo Website Marketplace.
marketplace in Odoo
multi vendor marketplace in Odoo
multivendor marketplace in Odoo
multiseller marketplace in Odoo
ecommerce marketplace in Odoo
Odoo marketplace
Odoo multiplevendor
Odoo multi seller
marketplace for multivendor 
Odoo marketplace multi seller
Amazon Marketplace
e-commerce platform
Odoo e-commerce platform
third-party sellers
online marketplace
Odoo thirdparty marketplace
Marketplace For All Buy And Sell Online
Odoo Multi Vendor Marketplace for your eCommerce Platform
Multi Vendor Marketplace for your eCommerce Platform
Marketplace for your eCommerce Platform
Marketplace eCommerce Platform

marketplace Odoo 

    Odoo Multi Seller Marketplace, Odoo Multi seller Marketplace. Odoo marketplace, Marketplace for seller, Marketplace for vendor, marketplace odoo seller
    """,
    "author": "BrowseInfo",
    "website" : "www.browseinfo.in",
    "price": 169,
    "currency": 'EUR',
    "depends" : ['base', 'sale_management', 'product','uom','stock', 'sale_stock', 'website', 'website_sale', 'website_partner'],
    "data": [
        'security/marketplace_security.xml',
        'security/ir.model.access2.csv',
        'data/data.xml',
        'data/email_template_signup.xml',
        'views/res_partner_view.xml',
        'views/sales_view.xml',
        'wizard/request_payment_view.xml',
        'views/product_view.xml',
        'views/payment_view.xml',
        'views/shop_view.xml',
        'views/mail_message_view.xml',
        'views/dashboard_action_view.xml',
        'views/dashboard_view.xml',
        'views/assets.xml',
        'views/marketplace_template_view.xml',
        'views/profile_template_view.xml',
        'views/signup_template_view.xml',
        'views/res_config_settings_views.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
    'live_test_url':'https://youtu.be/p6O_pe94sXY',
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
