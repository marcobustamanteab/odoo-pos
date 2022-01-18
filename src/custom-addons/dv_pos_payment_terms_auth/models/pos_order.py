from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _payment_fields(self, order, ui_paymentline, pos_order):
        payment_method = self.env['pos.payment.method'].browse(ui_paymentline['payment_method_id'])
        payment_fields = super(PosOrder, self)._payment_fields(order, ui_paymentline, pos_order)
        payment_fields['payment_terms'] = ui_paymentline.get('payment_terms')
        payment_fields['payment_authorization_code'] = ui_paymentline.get(
            'payment_authorization_code')
        #Override transaction_id
        payment_fields['transaction_id'] = ui_paymentline.get(
                'payment_authorization_code')
        return payment_fields
