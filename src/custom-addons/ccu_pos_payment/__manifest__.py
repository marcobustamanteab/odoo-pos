# -*- coding: utf-8 -*-

{
    "name" : "Money Transfer Information on POS",
    "author": "Konos",
    "version" : "14.0.1.0",
    'summary': 'POS Money Transfer Information on POS ',
    "description": """ This app use to print Money Transfer Information on the receipt..

     """,
    "license" : "OPL-1",
    "depends" : ['base','point_of_sale','ccu_pos'],
    "data": [
        'views/custom_js_added.xml',
        'views/pos_config.xml',
        'views/pos_order.xml',
        'views/pos_payment_method.xml',
        'views/account_move.xml',
    ],
    'qweb': [
    'static/src/xml/pos.xml'
    ],
    "auto_install": False,
    "installable": True,
    "category" : "Point of Sale",

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
