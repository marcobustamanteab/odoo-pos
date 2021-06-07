# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.base_rest.controllers import main

class InventoryApiController(main.RestController):
    _root_path = "/base_rest_inventory_api/"
    _collection_name = "base.rest.inventory.api.services"
    _default_auth = "public"
