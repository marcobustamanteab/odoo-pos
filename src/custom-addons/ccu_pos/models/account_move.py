from odoo import api, fields, models, _


class AccountMove(models.Model):
    _name = 'account.move'
    _description = 'Account Move or Invoice'
    _inherit = ['account.move']

    def _default_sequence_prefix(self):
        if len(self.pos_prder_ids) > 0:
            pos_order = self.pos_order_ids[0]
            prefix = pos_order.session_id.config_id.sequence_id.prefix
            return prefix.strip('/') if prefix else 'XXXXX'
        return "XXXXX"

    sequence_prefix = fields.Char("Cash Prefix", compute='_compute_sequence_prefix', store=True,
                                  default=_default_sequence_prefix)

    def _compute_sequence_prefix(self):
        for rec in self:
            if len(rec.pos_prder_ids) > 0:
                pos_order = rec.pos_order_ids[0]
                prefix = pos_order.session_id.config_id.sequence_id.prefix
                rec.sequence_prefix = prefix.strip('/') if prefix else 'XXXXX'
            else:
                rec.sequence_prefix = "XXXXX"
