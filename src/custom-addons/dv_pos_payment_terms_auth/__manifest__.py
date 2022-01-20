# -*- coding: utf-8 -*-
{
    'name' : 'Transbank Information on POS',
    'version': '0.0.1.2',
    'author': 'Konos',
    'website': 'https://konos.cl',
    'category': 'Point of Sale/Localization/Chile',
    'summary': 'Transbank Information on POS',
    'description': """ This app use to print Transbank Information Information on the receipt..
     """,
    'license' : 'OPL-1',
    'depends' : ['base','point_of_sale','account','ccu_pos_payment'],
    'data': [
        'views/pos_order_views.xml',
        'views/pos_payment_method_views.xml',
        'templates/point_of_sale_assets.xml',
    ],
    'qweb': [
        'static/src/xml/Popups/PaymentTermsInput.xml',
        'static/src/xml/Popups/PaymentTermsPopup.xml',
        'static/src/xml/Screens/PaymentScreen/PaymentMethodButton.xml',
        'static/src/xml/pos.xml'
    ],
    'images': ['static/description/banner.gif'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
