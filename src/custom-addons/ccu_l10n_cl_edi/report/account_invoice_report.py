from odoo import api, models
from lxml import etree
import re

class AccountInvoiceReport(models.AbstractModel):
    _name = 'report.ccu_l10n_cl_edi.account_invoice_report'

    def _get_tax_amount(self, tax_group_id, info):
        amount = 0
        for tax in info:
            if tax_group_id == tax[6]:
                amount = tax[1]
                break
        return amount

    def _get_report_values(self, docids, data=None):
        print(["DATA", data])
        print(["DOC_IDS", docids])
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('ccu_l10n_cl_edi.account_invoice_report')
        doc = []
        record = self.env['account.move'].browse(docids)
        doc.append(record)
        doc_extra = {}
        for rec in record:
            printing_config = self.env['fiscal.dte.printing.config'].search(
                [('company_id', '=', rec.company_id.id)])
            doc_extra[rec.id] = {}
            doc_extra[rec.id]['subtotal_values'] = ['0.0', '10.0', '19.0', '20.5', '20.5', '31.5', '0.0', '19.0']
            doc_extra[rec.id]['subtotal_values'] = []
            doc_extra[rec.id]['subtotal_values'].append(rec.amount_untaxed)
            if rec.l10n_latam_document_type_id.code == '39':
                doc_extra[rec.id]['is_voucher_document'] = True
            else:
                doc_extra[rec.id]['is_voucher_document'] = False
                for ref_rec in rec.l10n_cl_reference_ids:
                    print(ref_rec, ref_rec, ref_rec.l10n_cl_reference_doc_type_selection)
                    if ref_rec.l10n_cl_reference_doc_type_selection == '39':
                        doc_extra[rec.id]['is_voucher_document'] = True
                        break
                print(["IS_VOUCHER", doc_extra[rec.id]['is_voucher_document']])
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

            ted = record._l10n_cl_get_dte_barcode_xml()
            ted_groups = re.search("(?P<ted>.*)\<TmstFirma>.*</TmstFirma>", ted.get('ted', ''), flags=re.DOTALL)
            ted_xml = etree.XML(ted_groups.group('ted'))
            ted_string_list = etree.tostring(ted_xml, encoding='utf-8').decode().split("\n")
            ted_string = ''.join([x.strip() for x in ted_string_list])
            doc_extra[rec.id]['pdf417'] = rec._pdf417_barcode(ted_string)
            if rec.pos_order_ids:
                print(rec.pos_order_ids)
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

        # print(["EXTRA", doc_extra])

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': doc,
            'docs_extra': doc_extra
        }
        print(["DOCARGS", docargs])
        return docargs
