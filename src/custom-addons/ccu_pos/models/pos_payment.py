from odoo import api, fields, models, _

class PosPayment(models.Model):
    _name = 'pos.payment'
    _description = 'Point of Sale Payment'
    _inherit = ['pos.payment']

    sequence_prefix = fields.Char("Cashier Prefix", compute='_compute_sequence_prefix',
                                  default=lambda x: x.session_id.config_id.sequence_id.prefix.strip(
                                      '/') if x.session_id.config_id.sequence_id.prefix else 'XXXXX')

    def _compute_sequence_prefix(self):
        for rec in self:
            prefix = rec.session_id.config_id.sequence_id.prefix
            rec.sequence_prefix = prefix.strip('/') if prefix else 'XXXXX'
