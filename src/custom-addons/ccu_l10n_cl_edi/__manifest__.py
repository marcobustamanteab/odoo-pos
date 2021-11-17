# -*- coding: utf-8 -*-
# noinspection PyStatementEffect
{
    'name': "Customization for l10n_cl_edi",
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
    'version': '0.20210630.1401',
    # any module necessary for this one to work correctly
    'depends': ['l10n_cl_edi',
                'account',
                'product',
                'point_of_sale',
                'l10n_latam_invoice_document',
                ],
    # always loaded
    'data': [
        'data/paper_format.xml',
        'data/fiscal.dte.service.provider.csv',
        'entries/module_actions_act_window.xml',
        'entries/module_menu.xml',
        'report/account_move_invoice.xml',
        'entries/module_actions_report.xml',
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/fiscal_dte_log.xml',
        'views/l10n_cl_dte_caf.xml',
        'views/res_company_view.xml',
        'views/res_config_settings_view.xml',
        'views/fiscal_dte_service_provider.xml',
        'views/fiscal_dte_config_settings.xml',
        'views/l10n_latam_document_type.xml',
        'template/dte_template.xml',

    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'installable': True,
    'application': True,
}
