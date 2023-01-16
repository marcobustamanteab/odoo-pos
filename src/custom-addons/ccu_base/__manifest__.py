# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# noinspection PyStatementEffect
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
        "account",
        "stock",
        "ccu_mail",
    ],
    'data': [
        # 'data/res_users.xml',
        'security/ir.model.access.csv',
        'data/distribution_center.xml',
        # 'data/product_pricelist.xml',
        # 'data/user_confirmation_email.xml',
        'views/res_partner.xml',
        'views/res_partner_category.xml',
        'views/account_move.xml',
        'views/account_journal.xml',
        'views/account_account.xml',
        'views/analytic_account.xml',
        'views/stock_picking.xml',
    ],
    "application": True,
    "sequence": 0,
}
