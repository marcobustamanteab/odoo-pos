from odoo import models

class ReportPOSInvoice(models.AbstractModel):
    _inherit = 'report.ccu_l10n_cl_edi.generic_invoice_report'
    _name = 'report.ccu_l10n_cl_edi.pos_invoice_report'

    def get_docids(self, docids):
        pos_orders = self.env['pos.order'].browse(docids)
        invoice_to_print = []
        for order in pos_orders:
            if order.account_move:
                invoice_to_print.append(order.account_move[0].id)
        return invoice_to_print
