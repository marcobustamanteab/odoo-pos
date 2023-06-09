#noinspection PyStatementEffect

{
    "name": "ESB Stock In Connector",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Localization",
    "summary": "Get stock from SAP",
    "depends": [
        "queue_job",
        "connector",
        "stock",
        "ccu_stock",
        "ccu_connector_esb_stock_out",
    ],
    "author": "CCU S.A.",
    "website": "https://www.ccu.cl",
    "data": [
        "data/stock_location_cron.xml",
        "views/stock_location_view.xml",
        "views/wizard_stock_inventory_import_view.xml",
        "security/ir.model.access.csv"
    ],
    "development_status": "Beta",
    "maintainers": ["dclaver"],
}
