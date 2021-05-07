from odoo import api, fields, models

class StockLocation(models.Model):
    _inherit = 'stock.location'

    external_code = fields.Char("External Code")