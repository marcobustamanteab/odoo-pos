from odoo import models

class ReportPOSInvoice(models.AbstractModel):
    _inherit = 'report.ccu_l10n_cl_edi.generic_invoice_report'
    _name = 'report.ccu_l10n_cl_edi.pos_invoice_report'

    def get_docids(self, docids):
        pos_orders = self.env['pos.order'].browse(docids)
        moves = []
        for order in pos_orders:
            if 'account_moves' in self.env['pos.order'].fields_get().keys():
                account_moves = order.account_moves
            else:
                account_moves = order.account_move
            for move in account_moves:
                moves.append(move.id)
        return moves
