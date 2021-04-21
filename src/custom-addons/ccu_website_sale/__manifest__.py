# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# noinspection PyStatementEffect
{
    "name": "CCU Customization - E-Commerce",
    "version": "0.1",
    "category": "customizations",
    "license": "LGPL-3",
    "summary": "CCU Companies Customizations for E-Commerce",
    "author": "Compañia Cervecerias Unidas S.A. (CCU)",
    "maintainer": "Compañia Cervecerias Unidas S.A. (CCU)",
    "website": "https://www.ccu.cl",
    "depends": [
        "ccu_product",
        "website_sale",
        "contacts",
    ],
    'data': [
        "views/actions_act_window.xml",
        "views/menu.xml",
        "views/website_products_list_template.xml",
        "views/product_public_category_default.xml",
        "views/product_public_category.xml",
        'views/product_banner_config_view.xml',
        'views/res_city_district.xml',
        'views/res_holiday.xml',
        'views/res_weekday.xml',
        'security/res.groups.csv',
        'security/ir.model.access.csv',
        'data/res.weekday.csv',
    ],
    "application": True,
    "sequence": 0,
}
