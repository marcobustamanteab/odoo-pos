from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    invoice_default_tnc = fields.Char("T&C Default Text")