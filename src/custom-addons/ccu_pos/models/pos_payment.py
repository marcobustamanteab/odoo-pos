from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PosPayment(models.Model):
    _name = 'pos.payment'
    _description = 'Point of Sale Payment'
    _inherit = ['pos.payment']

    sequence_prefix = fields.Char("Cashier Prefix", compute='_compute_sequence_prefix', store=True,
                                  default=lambda x: x.session_id.config_id.sequence_id.prefix.strip(
                                      '/') if x.session_id.config_id.sequence_id.prefix else 'XXXXX')

    def _compute_sequence_prefix(self):
        for rec in self:
            prefix = rec.session_id.config_id.sequence_id.prefix
            rec.sequence_prefix = prefix.strip('/') if prefix else 'XXXXX'

    @api.model
    def create(self, vals):
        amount = vals.get("amount")
        method = self.env['pos.payment.method'].browse(vals.get('payment_method_id'))
        if method.max_payment_amount and amount > method.max_payment_amount:
            raise UserError("Max Payment Allowed %s")
        res = super(PosPayment, self).create(vals)
        return res