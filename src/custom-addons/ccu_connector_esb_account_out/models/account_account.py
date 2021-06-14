from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    ccu_sync = fields.Boolean(string="Syncs with ESB", default=False)
    ccu_code = fields.Char(string='CCU Code')