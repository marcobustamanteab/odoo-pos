from odoo import models, fields


class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'
    _description = 'Account Move Reversal'

    refund_type = fields.Selection(
        [
            ('refund','Credit Note'),
            ('return','Stock Return'),
        ], default='refund', required=True
    )
