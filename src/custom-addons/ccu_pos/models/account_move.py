from odoo import api, fields, models, _


class AccountMove(models.Model):
    _name = 'account.move'
    _description = 'Account Move or Invoice'
    _inherit = ['account.move']

    def _default_sequence_prefix(self):
        if len(self.pos_order_ids) > 0:
            pos_order = self.pos_order_ids[0]
            prefix = pos_order.session_id.config_id.sequence_id.prefix
            return prefix.strip('/') if prefix else 'XXXX1'
        else:
            pos_session = self.env['pos.session'].search([('name', '=ilike', self.ref)])
            if pos_session:
                prefix = pos_session.config_id.sequence_id.prefix
                return prefix.strip('/') if prefix else 'XXXX2'
        return "XXXX3"

    pos_sequence_prefix = fields.Char("Cashier Prefix", compute='_compute_pos_sequence_prefix', store=True)
    # pos_sequence_prefix = fields.Char("Cashier Prefix")
    pos_order_id = fields.Many2one('pos.order', string="POS Order")
    pos_session_id = fields.Many2one('pos.session', string="POS Session")
    printer_code = fields.Char("Printer Queue Code")

    def _compute_pos_sequence_prefix(self):
        for rec in self:
            rec.pos_sequence_prefix = ''
            print(["RESETING", rec.name])
            if self.pos_order_id:
                rec.pos_sequence_prefix = self.pos_order_id.session_id.config_id.sequence_id.prefix.strip('/')
            else:
                if self.pos_session_id:
                    rec.pos_sequence_prefix = self.pos_session_id.config_id.sequence_id.prefix.strip('/')
            if not rec.pos_sequence_prefix:
                pos_order = rec.env['pos.order'].search([('name', '=ilike', rec.payment_reference)], limit=1)
                if pos_order:
                    rec.pos_order_id = pos_order[0].id
                    rec.pos_session_id = pos_order[0].session_id.id
                pos_session = rec.env['pos.session'].search([('name', '=ilike', rec.ref)], limit=1)
                if pos_session:
                    rec.pos_session_id = pos_session[0].id
            if not rec.pos_sequence_prefix:
                if len(rec.pos_order_ids) > 0:
                    pos_order = rec.pos_order_ids[0]
                    if pos_order:
                        rec.pos_order_id = pos_order[0].id
                        rec.pos_session_id = pos_order[0].session_id.id
            if rec.pos_order_id or rec.pos_session_id:
                rec._compute_pos_sequence_prefix()

    def reset_cashier_prefix(self):
        moves = self.env['account.move'].search([])
        moves._compute_pos_sequence_prefix()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    pos_order_id = fields.Many2one('pos.order', string="POS Order")
