# -*- coding: utf-8 -*-
{
    'name': "accounting_extra_reports",

    'summary': """
        Conjunto de reportes de cuadratura - Contabilidad""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    "depends": [
        "account",
        "ccu_connector_esb_account_out",
        "l10n_cl",
        "base",
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/accounting_extra_reports.xml',
        'reports/report_cuadratura_asientos.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}