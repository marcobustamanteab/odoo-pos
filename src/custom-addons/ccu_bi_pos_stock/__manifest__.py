# Copyright (C) 2023 CCU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Hide out of stock products in POS
{
    "name": "Point of Sale - Hide Out of Stock Products",
    "summary": "Out of stock products are not showed in POS",
    "version": "14.0.1.0.0",
    "category": "Point of Sale",
    "license": "LGPL-3",
    "author": "Compañia Cervecerias Unidas S.A. (CCU)",
    "maintainer": "Compañia Cervecerias Unidas S.A. (CCU)",
    "website": "https://www.ccu.cl",
    "application": False,
    "installable": True,
    "depends": ["bi_pos_stock"],
    "data": [
        'views/assets.xml',
    ],
}
