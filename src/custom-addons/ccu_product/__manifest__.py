# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# noinspection PyStatementEffect
{
    "name": "CCU Customization - Product",
    "version": "0.1",
    "category": "customizations",
    "license": "LGPL-3",
    "summary": "CCU Companies Customizations for Product module",
    "author": "Compañia Cervecerias Unidas S.A. (CCU)",
    "maintainer": "Compañia Cervecerias Unidas S.A. (CCU)",
    "website": "https://www.ccu.cl",
    "depends": [
        "product",
    ],
    'data': [
        'data/product_pricelist.xml',
        "views/product_template.xml",
        "views/product_pricelist.xml",
        "views/product_pricelist_item.xml",
    ],
    "application": True,
    "sequence": 0,
}
