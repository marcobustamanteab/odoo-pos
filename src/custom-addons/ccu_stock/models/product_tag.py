#encoding: utf-8
from odoo import api, fields, models

class ProductTag(models.Model):
    # _inherit = ['res.partner']
    _name = "product.tag"
    _description = "Product Tag"

    name = fields.Char()
