import models

from . import fields, model

class integration_account_move(models.Model):
    _inherit = 'account.account_move'

    status = field.Boolean()
    resultado = fields.Char()
    payload = fields.Blob()
    date_sync = fields.Date()
    id_sap_trx = fields.Char()


