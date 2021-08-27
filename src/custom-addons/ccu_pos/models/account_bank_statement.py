from odoo import api, fields, models

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    pos_order_id = fields.Many2one('pos.order',string="Origin POS Order ID")

    @api.model
    def _prepare_liquidity_move_line_vals(self):
        vals = super(AccountBankStatementLine, self)._prepare_liquidity_move_line_vals()
        vals['pos_order_id'] = self.pos_order_id.id
        return vals

    @api.model
    def _prepare_counterpart_move_line_vals(self, counterpart_vals, move_line=None):
        vals = super(AccountBankStatementLine, self)._prepare_counterpart_move_line_vals(counterpart_vals, move_line)
        vals['pos_order_id'] = self.pos_order_id.id
        return vals
