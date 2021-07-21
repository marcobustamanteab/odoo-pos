# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    alternative_barcode = fields.Char("Alternative Barcode")
    
    def get_available_stock(self):
        return self.virtual_available - self.min_stock

    def check_stock(self, quantity):
        return self.get_available_stock() - quantity