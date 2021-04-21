# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


{
    "name": "CCU Customization - Base",
    "version": "0.1",
    "category": "customizations",
    "license": "LGPL-3",
    "summary": "CCU Companies Customizations for Base module",
    "author": "Compañia Cervecerias Unidas S.A. (CCU)",
    "maintainer": "Compañia Cervecerias Unidas S.A. (CCU)",
    "website": "https://www.ccu.cl",
    "depends": [
        "base",
        "ccu_mail",
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/distribution_center.xml',
        # 'data/product_pricelist.xml',
        # 'data/user_confirmation_email.xml',
        'views/res_partner.xml',
    ],
    "application": True,
    "sequence": 0,
}
