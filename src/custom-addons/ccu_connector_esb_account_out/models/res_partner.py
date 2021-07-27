from odoo import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cost_center_code = fields.Char(string='Cost Center Code', index=True)