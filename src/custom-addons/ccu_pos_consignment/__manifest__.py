# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# noinspection PyStatementEffect
{
    "name": "CCU Customization - POS Consignment",
    "version": "0.1",
    "category": "customizations",
    "sequence": 1000,
    "license": "LGPL-3",
    "summary": "CCU Companies Customizations for POS module",
    "author": "Compañia Cervecerias Unidas S.A. (CCU)",
    "maintainer": "Compañia Cervecerias Unidas S.A. (CCU)",
    "depends": [
        "ccu_pos",
        "ccu_l10n_cl_edi",
        "ccu_connector_esb_stock_out",
        "account"
    ],
    'data': [
        'views/product_template.xml',
        'views/account_move.xml',
        'views/pos_order.xml'
    ],
    'installable': True,
    'application': False,
    "website": "https://www.ccu.cl",
}
