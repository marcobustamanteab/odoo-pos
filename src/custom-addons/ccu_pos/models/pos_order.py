from odoo import api, fields, models, _

class PosOrder(models.Model):
    _name = 'pos.order'
    _description = 'Point of Sale Order'
    _inherit = ['pos.order']

    sequence_prefix = fields.Char("Cashier Prefix", compute='_compute_sequence_prefix', store=True,
                                  default=lambda x: x.config_id.sequence_id.prefix.strip(
                                      '/') if x.config_id.sequence_id.prefix else 'XXXXX')

    def _compute_sequence_prefix(self):
        for rec in self:
            prefix = rec.session_id.config_id.sequence_id.prefix
            rec.sequence_prefix = prefix.strip('/') if prefix else 'XXXXX'

    def _prepare_invoice_vals(self):
        vals = super(PosOrder, self)._prepare_invoice_vals()
        vals['pos_order_id'] = self.id
        vals['pos_session_id'] = self.session_id.id
        return vals