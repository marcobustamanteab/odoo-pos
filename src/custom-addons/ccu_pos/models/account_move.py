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
            pos_session = self.env['pos.session'].search([('name','=ilike',self.ref)])
            if pos_session:
                prefix = pos_session.config_id.sequence_id.prefix
                return prefix.strip('/') if prefix else 'XXXX2'
        return "XXXX3"

    pos_sequence_prefix = fields.Char("Cashier Prefix", compute='_compute_pos_sequence_prefix', store=True,
                                  default=_default_sequence_prefix)
    pos_order_id = fields.Many2one('pos.order', string="Origin POS Order ID")
    pos_session_id = fields.Many2one('pos.session', string="Origin POS Session ID")

    def _compute_pos_sequence_prefix(self):
        for rec in self:
            if len(rec.pos_order_ids) > 0:
                pos_order = rec.pos_order_ids[0]
                prefix = pos_order.session_id.config_id.sequence_id.prefix
                rec.pos_sequence_prefix = prefix.strip('/') if prefix else 'XXXX4'
            else:
                pos_session = rec.env['pos.session'].search([('name', '=ilike', rec.ref)])
                if pos_session:
                    prefix = pos_session.config_id.sequence_id.prefix
                    rec.pos_sequence_prefix = prefix.strip('/') if prefix else 'XXXX5'
                else:
                    rec.pos_sequence_prefix = "XXXX6"

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    pos_order_id = fields.Many2one('pos.order', string="Origin POS Order ID")