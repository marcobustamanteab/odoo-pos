# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# noinspection PyStatementEffect
{
    "name": "CCU Customization - Stock",
    "version": "0.1",
    "category": "customizations",
    "license": "LGPL-3",
    "summary": "CCU Companies Customizations for Stock module",
    "author": "Compañia Cervecerias Unidas S.A. (CCU)",
    "maintainer": "Compañia Cervecerias Unidas S.A. (CCU)",
    "website": "https://www.ccu.cl",
    "depends": [
        "stock",
        "ccu_product",
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/stock_actions_act_window.xml",
        "views/stock_menu.xml",
        "views/product_brand.xml",
        "views/product_property.xml",
        "views/product_tag.xml",
        "views/product_template_only.xml",
        "views/stock_warehouse.xml",
        "views/stock_location.xml",
    ],
    "application": True,
    "sequence": 0,
}
