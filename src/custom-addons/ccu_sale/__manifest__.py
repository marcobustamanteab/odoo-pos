# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# noinspection PyStatementEffect
{
    "name": "CCU Customization - Sale",
    "version": "0.1",
    "category": "customizations",
    "sequence": 0,
    "license": "LGPL-3",
    "summary": "CCU Companies Customizations for Sale module",
    "author": "Compañia Cervecerias Unidas S.A. (CCU)",
    "maintainer": "Compañia Cervecerias Unidas S.A. (CCU)",
    "depends": [ "sale", "ccu_base", "point_of_sale"],
    'data': [
        # "security/ir.model.access.csv",
        # "views/stock_actions_act_window.xml",
        # "views/stock_menu.xml",
        # "views/product_brand.xml",
        # "views/product_property.xml",
        # "views/product_tag.xml",
        # "views/product_template_only.xml",
        'views/PaymentLinesValidator.xml'
    ],
    'installable': True,
    'application': True,
    'qweb': [
        'static/src/xml/PaymentTransbankLinesValidator.xml',
        'static/src/xml/OrderReceiptTransbank.xml',
        'static/src/xml/PaymentScreenStatusTransbank.xml',
        'static/src/xml/PaymentScreenValidator.xml',
    ],
    "website": "https://www.ccu.cl",
}
