from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Team(models.Model):
    _inherit = "crm.team"

    branch_ccu_code = fields.Char(string='Branch CCU Code')
    profit_center_code = fields.Char(string='Profit Center Code', index=True)
