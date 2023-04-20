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

    def add_invoice_reference(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add invoice reference',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'account.move.invoice.reference',
            'context': {'default_move_id': self.id}
        }

    def del_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delete invoice reference',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'account.move.invoice.reference.delete',
            'context': {'default_move_id': self.id}
        }