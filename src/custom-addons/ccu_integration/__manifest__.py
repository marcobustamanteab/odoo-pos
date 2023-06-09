# -*- coding: utf-8 -*-
# noinspection PyStatementEffect
{
    'name': "Integration Layer",
    'summary': """
        Integration Layer Management""",
    'description': """
        Integration Layer 
    """,
    'author': "Martin Salcedo Pacheco",
    'website': "http://www.msalcedo.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'license': 'LGPL-3',
    'category': 'customizations',
    'version': '0.21',
    # any module necessary for this one to work correctly
    'depends': ['stock',
                'base_address_city',
                'contacts',
                'ccu_stock',
                'account'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'entries/module_actions_act_window.xml',
        'entries/module_menu.xml',
        # 'views/integration_account_move.xml',
        'views/integration_accounting.xml',
        'views/integration_task_definition.xml',
        'views/integration_endpoint.xml',
        'views/integration_request.xml',
        'views/integration_request_log.xml',
        'views/integration_settings.xml',
        'views/product_template.xml',
        'views/res_city.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/integration.endpoint.csv',
    ],
    'installable': True,
    'application': True,
}
