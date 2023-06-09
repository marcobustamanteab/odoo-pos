# -*- coding: utf-8 -*-
# noinspection PyStatementEffect
{
    'name': "Customization for HR",
    'summary': """
        Chilean Customization for CCU""",
    'description': """
        Chilean Customization for CCU 
    """,
    'author': "Martin Salcedo Pacheco",
    'website': "http://www.msalcedo.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'license': 'LGPL-3',
    'category': 'customizations',
    'version': '0.10',
    # any module necessary for this one to work correctly
    'depends': ['hr'],
    # always loaded
    'data': [
        'entries/module_actions_act_window.xml',
        'entries/module_menu.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'application': True,
}
