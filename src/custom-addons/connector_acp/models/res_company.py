from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    backend_acp_id = fields.Many2one(
        "backend.acp", string="Authorized Certification Provider"
    )
