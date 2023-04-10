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
        "l10n_cl_edi",
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/account_move_reversal_view.xml',
        'wizard/account_move_invoice_reference_view.xml',
        'views/account_move.xml'
    ],
    "application": True,
}
