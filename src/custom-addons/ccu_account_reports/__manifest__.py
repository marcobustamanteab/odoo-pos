# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2020 Konos
# Copyright (C) 2021 Konos
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "CCU Account Reports",
    "version": "12.0.1.0.8",
    "license": "LGPL-3",
    "summary": "Accounting Reports",
    "author": "CCU S.A.",
    "maintainer": "DCLAVER",
    "website": "http://gitlab.ccu.cl/odoo-pos/odoo-pos",
    "depends": [
        "account",
        "ccu_connector_esb_account_out",
        "l10n_cl",
    ],
    "data": [
        "wizard/sales_book_export.xml",
        "security/ir.model.access.csv",
    ],
    "application": False,
    "sequence": 0,
}
