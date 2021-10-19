from odoo import api, models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move for CCU Customization'

    refund_type = fields.Selection(
        [
            ('credit_note','Credit Note'),
            ('stock_return','Stock Return'),
        ]
    )