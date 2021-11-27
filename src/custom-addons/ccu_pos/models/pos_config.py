from odoo import models, api, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'

    printer_code = fields.Char("Printer Queue Code")