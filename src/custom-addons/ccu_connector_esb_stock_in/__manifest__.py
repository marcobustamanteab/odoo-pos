#noinspection PyStatementEffect

{
    "name": "ESB Stock In Connector",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "category": "Localization",
    "summary": "Get stcok from SAP",
    "depends": [
        "queue_job",
        "connector",
        "stock",
        "ccu_stock",
        "ccu_connector_esb_stock_out",
    ],
    "author": "Open Source Integrators",
    "website": "https://ccu.cl",
    "data": [
        "data/stock_location_cron.xml",
        "views/stock_location_view.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["dclaver"],
}
