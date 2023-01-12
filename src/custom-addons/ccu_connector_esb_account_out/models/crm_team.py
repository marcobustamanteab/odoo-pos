from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Team(models.Model):
    _inherit = "crm.team"

    branch_ccu_code = fields.Char(string='Branch CCU Code')
    profit_center_code = fields.Char(string='Profit center code for products', index=True)
    profit_center_code_services = fields.Char(string='Profit center code for services', index=True)
