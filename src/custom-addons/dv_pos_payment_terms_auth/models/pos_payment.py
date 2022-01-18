from odoo import api, fields, models


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    payment_authorization_code = fields.Char(string='Código Autorización')
    payment_terms = fields.Char(string='Plazos de Pago')
