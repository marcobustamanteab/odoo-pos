# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    ccu_code = fields.Char(string='CCU Code')
