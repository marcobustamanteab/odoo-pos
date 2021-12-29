# -*- coding: utf-8 -*-

{
    'name': 'CCU POS Order Notes ',
    'version': '14.0.0.0',
    'category': 'Point of Sale',
    'summary': 'Order notes in POS Interface',
    'sequence': 1,
    'author': 'Konos',
    'website': 'http://www.konos.cl/',
    'description': """CCU Notes on POS Orders and print on receipt.
    """,
    'depends': ['point_of_sale'],
    'data': [
        'views/assests.xml',
        'views/pos_config.xml',
        'views/pos_order_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': ['static/src/xml/*.xml'],
}
