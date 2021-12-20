# -*- coding: utf-8 -*-
{
    'name': "Chilean states and cities",

    'summary': """
        Adds states and cities not included by default
    """,

    'author': "Konos Soluciones & Servicios",
    'website': "https://www.konos.cl",

    'category': 'Localization/Chile',
    'version': '0.2',

    'depends': [
        'base_address_city',
    ],

    'data': [
        'data/res.country.state.csv',
        'data/res.city.csv',
        'views/res_company.xml',
        'views/res_partner.xml',
    ],

    'demo': [
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
