#noinspection PyStatementEffect
{
    "name": "ESB Stock Out Connector",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "category": "Localization",
    "summary": "Post picking move to SAP",
    "depends": [
        "queue_job",
        "connector",
        "base_rest",
        "base_rest_datamodel",
        "component",
        "ccu_connector_esb",
        "stock",
        "ccu_stock",
        "base_automation",
        "account",

    ],
    "author": "CCU S.A.",
    "website": "https://ccu.cl",
    "data": [
        "data/jobs.xml",
        "data/automated_actions.xml",
        "views/stock_location_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_picking_type_view.xml",
        "views/product_view.xml",
    ],
    "development_status": "Beta",
    "maintainers": ["dclaver"],
}
