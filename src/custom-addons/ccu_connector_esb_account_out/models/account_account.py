# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    ccu_sync = fields.Boolean(string="Syncs with ESB", default=False)
