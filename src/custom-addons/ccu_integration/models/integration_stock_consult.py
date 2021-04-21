#encoding: utf-8
from odoo import fields, api, models

class IntegrationStockConsult(models.TransientModel):
    _name = "integration.stock.consult"
    _description = "Record for Online Stock Consult"

    def _get_default_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one('res.company', string="Company", default=_get_default_company)
    #TODO: Completar todo el concepto
