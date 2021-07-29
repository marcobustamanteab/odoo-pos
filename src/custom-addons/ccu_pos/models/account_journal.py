from odoo import fields, api, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    _name = 'account.journal'

    split_payments = fields.Boolean("Split Payments by Partner")
