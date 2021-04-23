#encoding : utf-8
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name = 'product.template'

    sync_stock_qty = fields.Boolean("Synchronize Stock Qty.", default=True)
