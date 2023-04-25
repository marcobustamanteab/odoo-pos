# Copyright (C) 20233 CCU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Concept based on OCA module pos_user_restriction developed by Lorenzo Battistini @ TAKOBI
{
    "name": "Point of Sale - Restrict users",
    "summary": "Restrict some users to see and use only certain points of sale",
    "version": "14.0.1.0.0",
    "category": "Point of Sale",
    "license": "LGPL-3",
    "author": "Compañia Cervecerias Unidas S.A. (CCU)",
    "maintainer": "Compañia Cervecerias Unidas S.A. (CCU)",
    "website": "https://www.ccu.cl",
    "application": False,
    "installable": True,
    "depends": ["point_of_sale"],
    "data": [
        "security/pos_security.xml",
        "views/pos_config_views.xml",
    ],
}
