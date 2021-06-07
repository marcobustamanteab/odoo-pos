from odoo import fields, api, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    dte_service_code = fields.Char("DTE Service Code")
