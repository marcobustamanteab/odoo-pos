# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.base_rest.controllers import main

class AccountMoveApiController(main.RestController):
    _root_path = "/base_rest_account_api/"
    _collection_name = "base.rest.account.api.services"
    _default_auth = "public"
