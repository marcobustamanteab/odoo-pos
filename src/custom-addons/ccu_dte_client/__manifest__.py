# -*- coding: utf-8 -*-
{
    'name': "CCU DTE Client",

    'summary': """DTE Client for CCU Companies""",

    'description': """
        Provide the DTE Client Layout to integrate with Xerox or another DTE external Provider
    """,

    'author': "Martin Salcedo Pacheco",
    'website': "http://www.msalcedo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'customizations',
    'version': '0.20210630.1401',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account',
                'ccu_base',
                'ccu_services',
                'ccu_l10n_cl_edi',
                'account_accountant'],

    # always loaded
    'data': [
        'entries/module_actions_act_window.xml',
        'entries/module_menu.xml',
        'security/ir.model.access.csv',
        'views/dte_client_config.xml',
        'views/account_move.xml',
        'views/account_journal.xml',
        'views/account_tax.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': True,
}
