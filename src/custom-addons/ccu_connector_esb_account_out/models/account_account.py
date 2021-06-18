from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    send_cost_center = fields.Boolean(string="Send Cost Center to ESB", default=False)
    send_profit_center = fields.Boolean(string="Send profit Center to ESB", default=False)
