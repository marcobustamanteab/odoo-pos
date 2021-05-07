from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        config = self.env['fiscal.dte.printing.config'].search([('company_id','=',self.company_id.id)])
        if config and self.move_type in self.get_invoice_types() and self.journal_id.type == 'sale':
                if self.partner_id and self.partner_id.l10n_cl_sii_taxpayer_type == '3':
                    self.l10n_latam_document_type_id = config.voucher_document_type.id
