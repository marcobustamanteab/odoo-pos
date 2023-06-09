{
    "name": "SAP - Integrations",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "summary": "SAP Integrations",
    "author": "CCU S.A",
    "maintainer": "Daniel Clavería",
    "website": "http://gitlab.ccu.cl/odoo-pos/odoo-pos",
    "depends": [
        "ccu_connector_esb",
        "ccu_connector_esb_account_out",
        "ccu_connector_esb_stock_in",
        "ccu_connector_esb_stock_out",
        "inventory_extra_reports",
        "accounting_extra_reports",
        "connector_acp",
        "ccu_stock",
    ],
    'installable': True,
    'application': True,
    "sequence": 0,
}
