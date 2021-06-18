{
    "name": "ESB Account Out Connector",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Localization",
    "summary": "Send Odoo accounting entries to the bus.",
    "depends": [
        "queue_job",
        "connector",
        "base_rest",
        "base_rest_datamodel",
        "component",
        "sales_team",
        "ccu_connector_esb",
        "account",
        "base_automation",
    ],
    "author": "CCU S.A.",
    "website": "http://gitlab.ccu.cl/odoo-pos/odoo-pos",
    "data": [
        "views/account_account.xml",
        "views/account_analytic_account.xml",
        "views/account_journal.xml",
        "views/account_move.xml",
        "views/crm_team.xml",
        "data/jobs.xml",
        "data/automated_actions.xml",
        "views/res_company.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["dclaver"],
}
