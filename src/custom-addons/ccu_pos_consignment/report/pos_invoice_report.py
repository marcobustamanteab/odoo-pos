from odoo import models


class ReportPOSInvoice(models.AbstractModel):
    _inherit = 'report.ccu_l10n_cl_edi.generic_invoice_report'
    _name = 'report.ccu_l10n_cl_edi.pos_invoice_report'

    def get_docids(self, docids):
        pos_orders = self.env['pos.order'].browse(docids)
        moves = []
        for order in pos_orders:
            for move in order.account_moves:
                moves.append(move.id)
        return moves
