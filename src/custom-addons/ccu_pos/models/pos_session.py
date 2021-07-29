from collections import defaultdict
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare


class PosSession(models.Model):
    _name = 'pos.session'
    _order = 'id desc'
    _description = 'Point of Sale Session'
    _inherit = ['pos.session']

    def _create_account_move(self):
        """ Create account.move and account.move.line records for this session.

        Side-effects include:
            - setting self.move_id to the created account.move record
            - creating and validating account.bank.statement for cash payments
            - reconciling cash receivable lines, invoice receivable lines and stock output lines
        """
        journal = self.config_id.journal_id
        # Passing default_journal_id for the calculation of default currency of account move
        # See _get_default_currency in the account/account_move.py.
        account_move = self.env['account.move'].with_context(default_journal_id=journal.id).create({
            'journal_id': journal.id,
            'date': fields.Date.context_today(self),
            'ref': self.name,
        })
        self.write({'move_id': account_move.id})

        data = {}
        data = self._accumulate_amounts(data)
        data = self._create_non_reconciliable_move_lines(data)
        data = self._create_cash_statement_lines_and_cash_move_lines(data)
        print(["SPLIT_PAYMENTS", journal.split_payments])
        if journal.split_payments:
            data = self._create_invoice_receivable_lines_custom(data)
        else:
            data = self._create_invoice_receivable_lines(data)
        data = self._create_stock_output_lines(data)
        data = self._create_balancing_line(data)

        if account_move.line_ids:
            account_move._post()

        data = self._reconcile_account_move_lines(data)

    def _create_invoice_receivable_lines_custom(self, data):
        # Create invoice receivable lines for this session's move_id.
        # Keep reference of the invoice receivable lines because
        # they are reconciled with the lines in order_account_move_receivable_lines
        MoveLine = data.get('MoveLine')
        invoice_receivables = data.get('invoice_receivables')

        invoice_receivable_vals = defaultdict(list)
        invoice_receivable_lines = {}
        for receivable_account_id_and_partner_id, amounts in invoice_receivables.items():
            receivable_account_id = receivable_account_id_and_partner_id[0]
            partner_id = receivable_account_id_and_partner_id[1]
            invoice_vals = self._get_invoice_receivable_vals(receivable_account_id, amounts['amount'],
                                                             amounts['amount_converted'])
            invoice_vals['partner_id'] = partner_id
            invoice_vals['name'] = self.env['res.partner'].browse(partner_id).mapped('name')[0] or invoice_vals.get(
                'name')
            invoice_receivable_vals[receivable_account_id_and_partner_id].append(invoice_vals)
        print(["invoice_receivable_vals", invoice_receivable_vals])
        for receivable_account_id_and_partner_id, vals in invoice_receivable_vals.items():
            receivable_account_id = receivable_account_id_and_partner_id[0]
            partner_id = receivable_account_id_and_partner_id[1]
            receivable_line = MoveLine.create(vals)
            if (not receivable_line.reconciled):
                invoice_receivable_lines[receivable_account_id] = receivable_line

        data.update({'invoice_receivable_lines': invoice_receivable_lines})
        return data
