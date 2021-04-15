# Copyright (C) 2020 CCU
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models
from datetime import date, datetime
from calendar import monthrange

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    min_stock = fields.Integer(string="Stock Mínimo",
                                     required=False, help="Mínimo de stock (cuando se llega al mínimo se rechaza la compra)")
    search_tag_ids = fields.Many2many("product.tag", string="Search Tags")
    brand_id = fields.Many2one("product.brand", string="Brand")
    property_ids = fields.Many2many("product.property", string="Properties")
