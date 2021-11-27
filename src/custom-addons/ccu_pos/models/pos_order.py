from odoo import api, fields, models, _


class PosOrder(models.Model):
    _name = 'pos.order'
    _description = 'Point of Sale Order'
    _inherit = ['pos.order']

    def _default_sequence_prefix(self):
        if self.session_id.config_id.sequence_id.prefix:
            return self.session_id.config_id.sequence_id.prefix.strip('/')
        return False

    sequence_prefix = fields.Char("Cashier Prefix", compute='_compute_sequence_prefix', store=True,
                                  default=_default_sequence_prefix)

    @api.depends('session_id')
    def _compute_sequence_prefix(self):
        for rec in self:
            rec.sequence_prefix = rec._default_sequence_prefix()

    def _prepare_invoice_vals(self):
        vals = super(PosOrder, self)._prepare_invoice_vals()
        vals['pos_order_id'] = self.id
        vals['pos_session_id'] = self.session_id.id
        vals['printer_code'] = self.session_id.config_id.printer_code or ''
        return vals

    def reset_cashier_prefix(self):
        moves = self.env['pos.order'].search([])
        moves._compute_sequence_prefix()
