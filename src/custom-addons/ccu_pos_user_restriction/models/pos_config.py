from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    assigned_user_ids = fields.Many2many(
        "res.users",
        string="Assigned users",
        help="Restrict some users to only access their assigned points of sale.",
    )
