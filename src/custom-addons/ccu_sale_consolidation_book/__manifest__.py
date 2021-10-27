{
    'name': 'Truck Consolidation Books',
    'author': 'Daniel CLavería',
    'website': 'http://ccu.cl',
    'license': 'AGPL-3',
    'depends': [
        "account",
        "ccu_connector_esb_account_out",
        "l10n_cl",
        ],
    'contributors': [
        "Daniel Clavería dclaver@ccu.cl",
    ],
    'license': 'AGPL-3',
    'version': '12.0.1.0.0',
    'description': """
Truck Consolidation Books.
==================================
    * Truck Consolidation Plain Text
    , ...
    Report
  """,
    'active': True,
    'data': [
        'views/wizard_export_csv_books_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
