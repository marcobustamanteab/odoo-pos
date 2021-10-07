# -*- coding: utf-8 -*-
{
    'name': "CCU Services",

    'summary': """CCU Services""",

    'description': """
        Provide Services to all CCU Odoo implementations""",

    'author': "Martin Salcedo Pacheco",
    'website': "http://www.msalcedo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'entries/module_actions_act_window.xml',
        'entries/module_menu.xml',
        'security/ir.model.access.csv',
        'wizards/account_invoice_export_attachment.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'application': True,
}
