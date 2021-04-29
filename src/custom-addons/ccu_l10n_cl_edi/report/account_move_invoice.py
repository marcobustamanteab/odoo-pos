from odoo import api, models
from lxml import etree
import re

class ReportAccountMoveInvoice(models.AbstractModel):
    _name = 'report.ccu_l10n_cl_edi.report_account_move_invoice'

    def _get_tax_amount(self, tax_group_id, info):
        found = False
        amount = 0
        for tax in info:
            # print(tax)
            if tax_group_id == tax[6]:
                amount = tax[1]
                found = True
                break
        return amount


    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('action_report_stock_picking_batch_waybill')
        doc = []
        record = self.env['account.move'].browse(docids)
        doc.append(record)
        doc_extra = {}
        for rec in record:
            printing_config = self.env['fiscal.dte.printing.config'].search(
                [('company_id', '=', rec.company_id.id)])
            # print(rec.amount_by_group)
            doc_extra[rec.id] = {}
            doc_extra[rec.id]['subtotal_values'] = ['0.0','10.0','19.0','20.5','20.5','31.5','0.0','19.0']
            doc_extra[rec.id]['subtotal_values'] = []
            doc_extra[rec.id]['subtotal_values'].append(rec.amount_untaxed)
            if printing_config:
                tax_1 = self._get_tax_amount(printing_config.tax_1_id.id, list(rec.amount_by_group))
                tax_2 = self._get_tax_amount(printing_config.tax_2_id.id, list(rec.amount_by_group))
                tax_3 = self._get_tax_amount(printing_config.tax_3_id.id, list(rec.amount_by_group))
                tax_4 = self._get_tax_amount(printing_config.tax_4_id.id, list(rec.amount_by_group))
                tax_5 = self._get_tax_amount(printing_config.tax_5_id.id, list(rec.amount_by_group))
                subtotal_tax = tax_1 + tax_2 + tax_3 + tax_4 + tax_5
                tax_6 = self._get_tax_amount(printing_config.tax_6_id.id, list(rec.amount_by_group))
                doc_extra[rec.id]['subtotal_values'].append(tax_1)
                doc_extra[rec.id]['subtotal_values'].append(tax_2)
                doc_extra[rec.id]['subtotal_values'].append(tax_3)
                doc_extra[rec.id]['subtotal_values'].append(tax_4)
                doc_extra[rec.id]['subtotal_values'].append(tax_5)
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
            ted_groups = re.search("(?P<ted>.*)\<TmstFirma>.*</TmstFirma>",ted.get('ted',''),flags=re.DOTALL)
            ted_xml = etree.XML(ted_groups.group('ted'))
            ted_string_list = etree.tostring(ted_xml,encoding='utf-8').decode().split("\n")
            ted_string = ''.join([x.strip() for x in ted_string_list])
            doc_extra[rec.id]['pdf417'] = rec._pdf417_barcode(ted_string)
            if rec.pos_order_ids:
                # print(rec.pos_order_ids[0].id)
                pos_order = self.env['pos.order'].browse(rec.pos_order_ids[0].id)
                stock_picking = self.env['stock.picking'].search([('pos_order_id','=', pos_order.id)])
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
        return docargs