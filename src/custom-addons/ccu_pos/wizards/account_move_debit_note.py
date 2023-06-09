# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountDebitNote(models.TransientModel):
    _inherit = 'account.debit.note'

    def default_get(self, fields):
        res = super(AccountDebitNote, self).default_get(fields)
        res.update({'copy_lines': True})
        for a, b, move_id in res.get('move_ids', []):
            move = self.env['account.move'].browse(move_id)
            if move.move_type == 'out_invoice':
                res.update({'l10n_cl_edi_reference_doc_code': '3'})
            elif move.move_type == 'out_refund':
                res.update({'l10n_cl_edi_reference_doc_code': '1'})
        journals = self.env['account.journal'].search(
            [
                ('default_latam_document_type_id.code', '=', '56')
            ], limit=1
        )
        if journals:
            res.update({'journal_id': journals.id})
        return res

    # Redefined
    def create_debit(self):
        self.ensure_one()
        new_moves = self.env['account.move']
        for move in self.move_ids.with_context(include_business_fields=True):  # copy sale/purchase links
            if move.move_type == 'out_invoice' and self.l10n_cl_edi_reference_doc_code in ('1', '2'):
                raise UserError(
                    "Código de Motivo %s no disponible para este comprobante" % (self.l10n_cl_edi_reference_doc_code))
            if move.move_type == 'out_refund' and self.l10n_cl_edi_reference_doc_code in ('2', '3'):
                raise UserError(
                    "Código de Motivo %s no disponible para este comprobante" % (self.l10n_cl_edi_reference_doc_code))
            default_values = self._prepare_default_values(move)
            lines_to_add = []
            for lines in move.line_ids:
                line_vals = {}
                line_vals['product_id'] = lines.product_id.id
                line_vals['account_id'] = lines.account_id.id
                line_vals['analytic_account_id'] = lines.analytic_account_id.id
                line_vals['analytic_tag_ids'] = [x.id for x in lines.analytic_tag_ids]
                line_vals['name'] = lines.name
                line_vals['quantity'] = lines.quantity
                line_vals['price_unit'] = lines.price_unit
                line_vals['exclude_from_invoice_tab'] = lines.exclude_from_invoice_tab
                line_vals['tax_ids'] = [x.id for x in lines.tax_ids]
                line_vals['tax_tag_ids'] = [x.id for x in lines.tax_tag_ids]
                line_vals['tax_repartition_line_id'] = lines.tax_repartition_line_id.id
                # print(["LINE_VALS", line_vals])
                lines_to_add.append([0,0,line_vals])
            default_values['line_ids'] = lines_to_add
            new_move = move.copy(default=default_values)
            new_move._compute_invoice_taxes_by_group()
            move_msg = _(
                "This debit note was created from:") + " <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>" % (
                           move.id, move.name)

            new_move.message_post(body=move_msg)
            new_moves |= new_move

        action = {
            'name': _('Debit Notes'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        if len(new_moves) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': new_moves.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', new_moves.ids)],
            })
        return action
