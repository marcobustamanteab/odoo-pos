# -*- coding: utf-8 -*-
{
    'name': "inventory_extra_reports",

    'summary': """
        Conjunto de reportes de cuadratura - Transaciones de inventario por venta""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Daniel Clavería",
    'website': "http://www.ccu.cl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'ccu_connector_esb_stock_out',
        'stock',
    ],


# always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_extra_reports.xml',
        'reports/sales_inventory_transactions_report.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}