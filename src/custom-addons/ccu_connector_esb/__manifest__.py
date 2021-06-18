{
    "name": "ESB Connector",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Localization",
    "summary": "Basic infrastructure to configure and communicate"
    " with the ESB.",
    "depends": ["connector_acp"],
    "external_dependencies": {
        "python": ["simplejson"]
    },
    "author": "CCU S.A.",
    "website": "http://gitlab.ccu.cl/odoo-pos/odoo-pos",
    "data": [
        "views/backend_acp.xml",
        "views/res_company.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["DanielClaveria"],
}
