#encoding : utf-8
from odoo import models, fields, api

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    # external_code = fields.Char("External Code")
    external_center_code = fields.Char("External Center Code")
