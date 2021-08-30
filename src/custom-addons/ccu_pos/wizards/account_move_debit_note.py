# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountDebitNote(models.TransientModel):
    _inherit = 'account.debit.note'

    def default_get(self, fields):
        res = super(AccountDebitNote, self).default_get(fields)
        res.update({'copy_lines':True})
        for a, b, move_id in res.get('move_ids', []):
            move = self.env['account.move'].browse(move_id)
            if move.move_type == 'out_invoice':
                res.update({'l10n_cl_edi_reference_doc_code': '3'})
            elif move.move_type == 'out_refund':
                res.update({'l10n_cl_edi_reference_doc_code': '1'})
        journals = self.env['account.journal'].search(
            [
                ('default_latam_document_type_id.code','=','56')
            ], limit=1
        )
        if journals:
            res.update({'journal_id':journals.id})
        return res

    def create_debit(self):
        self.ensure_one()
        for move in self.move_ids:
            if move.move_type == 'out_invoice' and self.l10n_cl_edi_reference_doc_code in ('1', '2'):
                raise UserError(
                    "Código de Motivo %s no disponible para este comprobante" % (self.l10n_cl_edi_reference_doc_code))
            if move.move_type == 'out_refund' and self.l10n_cl_edi_reference_doc_code in ('2', '3'):
                raise UserError(
                    "Código de Motivo %s no disponible para este comprobante" % (self.l10n_cl_edi_reference_doc_code))
        return super(AccountDebitNote, self).create_debit()
