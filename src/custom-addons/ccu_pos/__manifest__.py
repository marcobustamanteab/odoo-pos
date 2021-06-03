# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# noinspection PyStatementEffect
{
    "name": "CCU Customization - Pos",
    "version": "0.1",
    "category": "customizations",
    "sequence": 1000,
    "license": "LGPL-3",
    "summary": "CCU Companies Customizations for Pos module",
    "author": "Compañia Cervecerias Unidas S.A. (CCU)",
    "maintainer": "Compañia Cervecerias Unidas S.A. (CCU)",
    "depends": ["point_of_sale"],
    'data': [
        # "security/ir.model.access.csv",
        #'data/pos.payment.method.csv',
        'views/PosCommonAssets.xml',
    ],
    'installable': True,
    'application': True,
    'qweb': [
        #'static/src/xml/ClientLineValidate.xml',
        'static/src/xml/ClientDetailsEditValidate.xml',
        'static/src/xml/OrderReceiptTransbank.xml',
        'static/src/xml/PaymentLinesValidator.xml',
        'static/src/xml/PaymentScreenStatusTransbank.xml',
        'static/src/xml/PaymentScreenValidator.xml',
    ],
    "website": "https://www.ccu.cl",
}
