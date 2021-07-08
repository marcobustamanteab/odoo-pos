from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    cost_center_code = fields.Char(string='Cost Center Code', index=True)
    profit_center_code = fields.Char(string='Profit Center Code', index=True)