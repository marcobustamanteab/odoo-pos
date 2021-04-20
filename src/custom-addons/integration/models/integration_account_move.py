from odoo import fields, models

class integration_account_move(models.Model):
    _inherit = 'account.move'

    response_status = fields.Boolean('status')
    response_description = fields.Char('resultado sap')
    response_payload = fields.Binary('json payload')
    response_date_sync = fields.Date('fecha trx')
    response_id_trx = fields.Char('id sap trx')

