from odoo import fields, models


class IntegrationAccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'integration account move'

    integration_line_ids = fields.One2many('integration.account.move.line', 'parent_id', string='Lines')


class IntegrationAccountMoveLine(models.Model):
    _name = 'integration.account.move.line'
    _description = 'integration account move'

    parent_id = fields.Many2one('account.move')
    response_status = fields.Boolean('status')
    response_description = fields.Char('resultado_sap')
    response_payload = fields.Binary('json_payload')
    response_date_sync = fields.Date('fecha_trx')
    response_id_trx = fields.Char('id_sap_trx')

   # @api.model
   # def _get_account_configuration(self):
   #      self.env[]


