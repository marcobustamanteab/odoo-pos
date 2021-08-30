# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    def default_get(self, fields):
        res = super(AccountMoveReversal, self).default_get(fields)
        journals = self.env['account.journal'].search(
            [
                ('default_latam_document_type_id.code','=','61')
            ], limit=1
        )
        if journals:
            print(["DEFAULT_GET_", journals.id])
            res.update({'journal_id':journals.id})
        return res

    def reverse_moves(self):
        if self.l10n_cl_edi_reference_doc_code == "2":
            raise UserError("Código de Referencia SII 2 no disponible")
        return super(AccountMoveReversal, self.with_context(
            default_l10n_cl_edi_reference_doc_code=self.l10n_cl_edi_reference_doc_code,
            default_l10n_cl_original_text=self.l10n_cl_original_text,
            default_l10n_cl_corrected_text=self.l10n_cl_corrected_text
        )).reverse_moves()
