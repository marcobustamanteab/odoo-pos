from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'
    _description = 'Account Move Reversal'

    refund_type = fields.Selection(
        [
            ('refund','Refund'),
            ('return','Stock Return'),
        ]
    )