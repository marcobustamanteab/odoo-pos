from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        config = self.env['fiscal.dte.printing.config'].search([('company_id','=',self.company_id.id)])
        if config and self.move_type in self.get_invoice_types() and self.journal_id.type == 'sale':
                if self.partner_id and self.partner_id.l10n_cl_sii_taxpayer_type == '3':
                    self.l10n_latam_document_type_id = config.voucher_document_type.id

    def _is_doc_type_voucher(self):
        res = False
        if self.l10n_latam_document_type_id.code in ['35', '39', '906', '45', '46', '70', '71']:
            res = True
        for ref_rec in self.l10n_cl_reference_ids:
            found = False
            if ref_rec.l10n_cl_reference_doc_type_selection == '39' and not found:
                res = True
                found = True
            if ref_rec.l10n_cl_reference_doc_type_selection == '61' and not found:
                origin_doc = self.env['account.move'].search([]).filtered(
                    lambda inv: inv.l10n_latam_document_number == ref_rec.origin_doc_number)
                for ref_orig_rec in origin_doc:
                    if ref_orig_rec and ref_orig_rec.l10n_latam_document_type_id.code == '39' and not found:
                        res = True
                        found = True
        return res
