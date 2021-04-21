#encoding: utf-8
from odoo import api, fields, models

class ProductBrand(models.Model):
    # _inherit = ['res.partner']
    _name = "product.brand"
    _description = "Product Brand"

    name = fields.Char("Name")
    url = fields.Char("URL")
