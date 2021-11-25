# -*- coding: utf-8 -*-
{
    'name': "ccu_sale_book_report",

    'summary': """ Reporte Avanzados de Ventas """,

    'description': """ Reporte Avanzados de Ventas """,

    'author': "In Nova TI SpA",
    'website': "https://www.innovati.cl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "account",
        # "ccu_connector_esb_account_out",
        "l10n_cl",
        "point_of_sale",
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/etd_account_report.xml',
        # 'reports/report_cuadratura_asientos.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}