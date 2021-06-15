from odoo import models, fields, api

class AccountTax(models.Model):
    _inherit = ["account.tax"]

    dte_service_code = fields.Char("DTE Service Code")
