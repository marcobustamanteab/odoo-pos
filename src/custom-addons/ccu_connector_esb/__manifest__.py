# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    "name": "ESB Connector",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "category": "Localization",
    "summary": "Basic infrastructure to configure and communicate"
    " with the ESB.",
    "depends": ["connector_acp"],
    "external_dependencies": {
        "python": ["simplejson"]
    },
    "author": "Open Source Integrators",
    "website": "https://gitlab.ccu.cl/equipo-desarrollo-odoo/proyecto-pewma",
    "data": [
        "views/backend_acp.xml",
        "views/res_company.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["max3903"],
}
