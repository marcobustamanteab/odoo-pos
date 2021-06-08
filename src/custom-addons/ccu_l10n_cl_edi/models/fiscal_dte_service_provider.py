from odoo import models, api, fields

class FiscalDTEServiceProvider(models. Model):
    _name = 'fiscal.dte.service.provider'
    _description = "Fiscal DTE Service Provider Server"

    name = fields.Char("Name")
    url = fields.Char("URL")
    type = fields.Selection([
        ('cert', 'Certification'),
        ('prod', 'Production'),
    ])