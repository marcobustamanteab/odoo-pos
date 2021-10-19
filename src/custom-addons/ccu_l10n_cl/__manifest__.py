# -*- coding: utf-8 -*-
# noinspection PyStatementEffect
{
    'name': "Customization for l10n_cl",
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
    'version': '0.20210727.1057',
    # any module necessary for this one to work correctly
    'depends': ['l10n_cl',
                ],
    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'application': True,
}
