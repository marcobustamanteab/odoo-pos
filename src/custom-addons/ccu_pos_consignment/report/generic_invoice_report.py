from lxml import etree
from odoo import models
import re


class GenericInvoiceReport(models.AbstractModel):
    _name = 'report.ccu_l10n_cl_edi.generic_invoice_report'

    def _get_report_values(self, docids, data=None):
        docids = self.get_docids(docids)
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('ccu_l10n_cl_edi.account_invoice_report')
        records = self.env['account.move'].browse(docids)
        doc_extra = {}
        for rec in records:
            printing_config = self.env['fiscal.dte.printing.config'].search(
                [('company_id', '=', rec.company_id.id)])
            doc_extra[rec.id] = {}
            doc_extra[rec.id]['subtotal_values'] = ['0.0', '10.0', '19.0', '20.5', '20.5', '31.5', '0.0', '19.0']
            doc_extra[rec.id]['subtotal_values'] = []
            doc_extra[rec.id]['subtotal_values'].append(rec.amount_untaxed)
            doc_extra[rec.id]['is_voucher_document'] = "0"
            if rec.l10n_latam_document_type_id.code == '39':
                doc_extra[rec.id]['is_voucher_document'] = "1"
            else:
                doc_extra[rec.id]['is_voucher_document'] = "0"
                for ref_rec in rec.l10n_cl_reference_ids:
                    found = False
                    # print(ref_rec, ref_rec, ref_rec.l10n_cl_reference_doc_type_selection)
                    if ref_rec.l10n_cl_reference_doc_type_selection == '39' and not found:
                        doc_extra[rec.id]['is_voucher_document'] = "1"
                        found = True
                    if ref_rec.l10n_cl_reference_doc_type_selection == '61' and not found:
                        origin_doc = rec.env['account.move'].search([]).filtered(lambda inv: inv.l10n_latam_document_number == ref_rec.origin_doc_number)
                        for ref_orig_rec in origin_doc:
                            if ref_orig_rec and ref_orig_rec.l10n_latam_document_type_id.code == '39' and not found:
                                doc_extra[rec.id]['is_voucher_document'] = "1"
                                found = True
            if printing_config:
                tax_6 = self._get_tax_amount(printing_config.tax_6_id.id, list(rec.amount_by_group))
                doc_extra[rec.id]['subtotal_values'].append(
                    self._get_tax_amount(printing_config.tax_1_id.id, list(rec.amount_by_group)))
                doc_extra[rec.id]['subtotal_values'].append(
                    self._get_tax_amount(printing_config.tax_2_id.id, list(rec.amount_by_group)))
                doc_extra[rec.id]['subtotal_values'].append(
                    self._get_tax_amount(printing_config.tax_3_id.id, list(rec.amount_by_group)))
                doc_extra[rec.id]['subtotal_values'].append(
                    self._get_tax_amount(printing_config.tax_4_id.id, list(rec.amount_by_group)))
                doc_extra[rec.id]['subtotal_values'].append(
                    self._get_tax_amount(printing_config.tax_5_id.id, list(rec.amount_by_group)))
                doc_extra[rec.id]['subtotal_values'].append(rec.amount_total - tax_6)
                doc_extra[rec.id]['subtotal_values'].append(tax_6)
                doc_extra[rec.id]['vat_total'] = tax_6
            else:
                doc_extra[rec.id]['subtotal_values'].append(0)
                doc_extra[rec.id]['subtotal_values'].append(0)
                doc_extra[rec.id]['subtotal_values'].append(0)
                doc_extra[rec.id]['subtotal_values'].append(0)
                doc_extra[rec.id]['subtotal_values'].append(0)
                doc_extra[rec.id]['subtotal_values'].append(rec.amount_total)
                doc_extra[rec.id]['subtotal_values'].append(0)
                doc_extra[rec.id]['vat_total'] = 0
            ted = rec._l10n_cl_get_dte_barcode_xml()
            ted_groups = re.search("(?P<ted>.*)\<TmstFirma>.*</TmstFirma>", ted.get('ted', ''), flags=re.DOTALL)
            ted_xml = etree.XML(ted_groups.group('ted'))
            ted_string_list = etree.tostring(ted_xml, encoding='utf-8').decode().split("\n")
            ted_string = ''.join([x.strip() for x in ted_string_list])
            doc_extra[rec.id]['pdf417'] = rec._pdf417_barcode(ted_string)
            if rec.pos_order_ids:
                pos_order = self.env['pos.order'].browse(rec.pos_order_ids[0].id)
                stock_picking = self.env['stock.picking'].search([('pos_order_id', '=', pos_order.id)])
                if pos_order.payment_ids:
                    payment_form = pos_order.payment_ids[0].payment_method_id.name
                    doc_extra[rec.id]['payment_form'] = payment_form
                else:
                    doc_extra[rec.id]['payment_form'] = "-"
                doc_extra[rec.id]['pos_order'] = pos_order
                doc_extra[rec.id]['stock_picking'] = stock_picking
            else:
                doc_extra[rec.id]['payment_form'] = ''
                doc_extra[rec.id]['pos_order'] = ''
                doc_extra[rec.id]['stock_picking'] = ''

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': records,
            'docs_extra': doc_extra
        }
        return docargs
