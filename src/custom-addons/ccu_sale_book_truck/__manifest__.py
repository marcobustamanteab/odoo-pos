# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# noinspection PyStatementEffect
{
    "name": "CCU Customization - Libro de Venta",
    "version": "0.1.3",
    "category": "customizations",
    "sequence": 1000,
    "license": "LGPL-3",
    "summary": "CCU Companies Customizations for book sale",
    "author": "In Nova TI SpA",
    "maintainer": "In Nova TI SpA",
    "depends": [
        # "point_of_sale",
        "ccu_base",
        # "l10n_cl",
        # "l10n_cl_edi",
        # "l10n_cl_counties",
    ],
    'data': [
        'views/account_move.xml',
        'views/res_company_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    # 'qweb': [
    #     'views/account_move.xml',
        # 'static/src/xml/ProductScreenValidate.xml',
    # ],
    "website": "https://www.ccu.cl",
}
