# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    alternative_barcode = fields.Char("Alternative Barcode")
    product_used = fields.Boolean("Product Used", compute="_compute_product_used")

    def _compute_product_used(self):
        for rec in self:
            products = self.env['account.move.line'].sudo().search([('product_id', '=', rec.id)])
            rec.product_used = False
            if len(products):
                rec.product_used = True
            products = self.env['pos.order.line'].sudo().search([('product_id', '=', rec.id)])
            if len(products):
                rec.product_used = True
            products = self.env['sale.order.line'].sudo().search([('product_id', '=', rec.id)])
            if len(products):
                rec.product_used = True
            products = self.env['stock.inventory.line'].sudo().search([('product_id', '=', rec.id)])
            if len(products):
                rec.product_used = True

    
    def get_available_stock(self):
        return self.virtual_available - self.min_stock

    def check_stock(self, quantity):
        return self.get_available_stock() - quantity