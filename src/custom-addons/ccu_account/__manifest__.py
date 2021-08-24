# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# noinspection PyStatementEffect
{
    "name": "CCU Customization - Account",
    "version": "0.1",
    "category": "customizations",
    "license": "LGPL-3",
    "summary": "CCU Companies Customizations for Account module",
    "author": "Compañia Cervecerias Unidas S.A. (CCU)",
    "maintainer": "Compañia Cervecerias Unidas S.A. (CCU)",
    "website": "https://www.ccu.cl",
    "depends": [
        "ccu_base",
        "account",
    ],
    'data': [
        # 'data/res_users.xml',
        # 'security/ir.model.access.csv',
        # 'data/distribution_center.xml',
        # 'data/product_pricelist.xml',
        # 'data/user_confirmation_email.xml',
        'views/account_move.xml',
    ],
    "application": True,
}
