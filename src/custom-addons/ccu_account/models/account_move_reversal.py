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
            ('refund','Credit Note'),
            ('return','Stock Return'),
        ], default='refund', required=True
    )

    def reverse_moves(self):
        res = self.reverse_moves()
        if self.refund_type == 'return':
            self.reverse_stock_picking()
        return res

    def reverse_stock_picking(self):
        for move in self.move_ids:
            stock_picking = self.env['stock.picking'].search(
                [
                    ('pos_order_id','=',move.pos_order_id.id),
                    ('picking_type_id.code','=','outgoing'),
                ]
            )


