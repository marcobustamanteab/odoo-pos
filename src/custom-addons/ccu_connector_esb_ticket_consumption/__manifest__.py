{
    "name": "ESB Account Out Ticket Fiolio Consumption Connector",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Localization",
    "summary": "Send Odoo accounting of ticket entries to the bus.",
    "depends": [
        "ccu_connector_esb_account_out",
        "account",
        "queue_job",
        "connector",
        "base_rest",
        "component",
        "sales_team",
        "ccu_connector_esb",
        "ccu_base",
        "ccu_pos",
    ],
    "author": "CCU S.A.",
    "website": "http://gitlab.ccu.cl/odoo-pos/odoo-pos",
    "data": [
        "views/account_move.xml",
        "data/jobs.xml",
        "views/res_company.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["dclaver"],
}
