# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# Copyright (C) 2020 Konos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "ESB Account Out Connector",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "category": "Localization",
    "summary": "Send Odoo accounting entries to the bus.",
    "depends": [
        "queue_job",
        "connector",
        "base_rest",
        "base_rest_datamodel",
        "component",
        "ccu_connector_esb",
        "account",
        "base_automation",
    ],
    "author": "Open Source Integrators",
    "website": "https://gitlab.ccu.cl/equipo-desarrollo-odoo/proyecto-pewma",
    "data": [
        "views/account_account.xml",
        "views/account_analytic_account.xml",
        "views/account_journal.xml",
        "views/account_move.xml",
        "data/jobs.xml",
        "data/automated_actions.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["dclaver"],
}
