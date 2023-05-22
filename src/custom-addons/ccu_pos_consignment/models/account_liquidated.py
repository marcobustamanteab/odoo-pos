from odoo import api, fields, models


class AccountLiquidated(models.Model):
    _inherit = 'account.move'

    name = fields.Char(string="name")