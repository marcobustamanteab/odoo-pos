# -*- coding: utf-8 -*-
##############################################################################
#
#    Konos
#    Copyright (C) 2020 Konos (<http://konos.cl/>)
#
##############################################################################

from odoo.tools.misc import str2bool, xlwt
from xlsxwriter.workbook import Workbook
import base64
import json
import io
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from xlwt import easyxf
import csv
import time
from datetime import datetime, date

import logging
_logger = logging.getLogger(__name__)


class etd_account_excel_wizard_form(models.TransientModel):
    _name ='wizard.export.etd.document.detail'

    date_to = fields.Date('Fecha Final', required=True, default=lambda self: str(datetime.now()))
    date_from = fields.Date('Fecha Inicial', required=True, default=lambda self: time.strftime('%Y-%m-%d'))
    
    def etd_document_excel(self):

        num_of_days = (self.date_to-self.date_from).days
        if num_of_days > 30:
            raise ValidationError('La consulta no puede superar 30 días de busqueda')
            return False

        date_stop = self.date_to
        fecha = date_stop.strftime("%Y-%m-%d")       
        i = 1
        sheetName = 1
        workbook = xlwt.Workbook()
        
        n = 2
        c = 0
        style1 = xlwt.easyxf('pattern: pattern solid, fore_colour blue;''font: colour white, bold True;')
        filename = 'LibroVentasDetalladoFA'+str(self.date_to)+'.xls'
        style = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;') # 36pt
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        font.height = 250
        currency = xlwt.easyxf('font: height 180; align: wrap yes, horiz right', num_format_str='#,##0.00')
        formato_fecha=xlwt.easyxf(num_format_str='DD-MM-YY')
        formato_periodo=xlwt.easyxf(num_format_str='YYYY-MM')
        worksheet = workbook.add_sheet("Libro de Ventas Detallado al "+str(self.date_to))
        
        #Se buscan los picking en estado distinto a cancelado, fecha hoy u antes, y de salida
        #('date_invoice','>=',self.date_from), ('date_invoice','<=',self.date_to),  ('state' ,'not in',['canceled','draft'])
        sales_journal = self.env['account.journal'].sudo().search(
            [('name', '=', 'Ventas')],
            limit=1)
        etd_document_obj = self.env['account.move'].sudo().search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', 'not in', ['canceled', 'draft']),
            ('move_type', 'in', ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']),
            ('company_id.name', '=', self.env.company.name),
        ])
        # ('journal_id', '<=', sales_journal.id), is_sync

        #,('picking_type_id.code', '=', 'outgoing')


        worksheet.col(0).width = 3000
        worksheet.col(1).width = 2500
        #LINE
        worksheet.col(2).width = 4500
        #JOURNAL
        worksheet.col(3).width = 4500
        #FECHA EMISION
        worksheet.col(4).width = 5000
        #DATE
        worksheet.col(5).width = 7000
        worksheet.col(6).width = 3000
        worksheet.col(7).width = 3000
        worksheet.col(8).width = 2000
        worksheet.col(9).width = 8000
        worksheet.col(10).width = 3000
        worksheet.col(11).width = 3000
        worksheet.col(12).width = 3000
        worksheet.col(13).width = 3000
        worksheet.col(14).width = 3000
        worksheet.col(15).width = 3000
        worksheet.col(16).width = 3000
        worksheet.col(17).width = 3000
        worksheet.col(18).width = 3000
        worksheet.col(19).width = 3001
        worksheet.col(20).width = 3001
        worksheet.col(21).width = 3002
        worksheet.col(22).width = 3002
        worksheet.col(23).width = 3003
        worksheet.col(24).width = 3004
        worksheet.col(25).width = 3004
        worksheet.col(26).width = 3005
        worksheet.col(27).width = 3005
        worksheet.col(28).width = 3006
        worksheet.col(29).width = 3006
        worksheet.col(30).width = 3007
        worksheet.col(31).width = 3007
        worksheet.col(32).width = 3008
        worksheet.col(33).width = 3008
        worksheet.col(34).width = 3009
        worksheet.col(35).width = 3009
        worksheet.col(36).width = 3010
        worksheet.col(37).width = 3010

        worksheet.merge(0, 0, 0, 20, style1)

        worksheet.write(n-1, 0, 'SOCIEDAD FINACIERA',  style1)
        worksheet.write(n-1, 1, 'PUNTO DE VENTA',  style1)
        worksheet.write(n-1, 2, 'N° DOCUMENTO INTERNO',  style1)
        worksheet.write(n-1, 3, 'FOLIO LEGAL',  style1)
        worksheet.write(n-1, 4, 'CONDICION_DE_PAGO',  style1)
        worksheet.write(n - 1, 5, 'TRANSBANK ID', style1)
        worksheet.write(n-1, 6, 'NUMERO DE PEDIDO DE VENTA',  style1)
        # worksheet.write(n-1, 6, 'FOLIO REFENCIA  EN  EL  CASO  DE NOTAS DE CREDITO  Y  DEBITO',  style1)
        # worksheet.write(n-1, 7, 'DESCR_DTE',  style1)
        worksheet.write(n-1, 7, 'FECHA DOCUMENTO ODOO',  style1)
        worksheet.write(n-1, 8, 'VENDEDOR',  style1)
        worksheet.write(n-1, 9, 'TIPO  DE  DOCUMENTO',  style1)
        worksheet.write(n-1, 10, 'RUT CLIENTE',  style1)
        # worksheet.write(n-1, 12, 'ID CLIENTE SAP EN EL CASO DE QUE EXISTA',  style1)
        # worksheet.write(n-1, 13, 'ID CLIENTE ODOO',  style1)
        worksheet.write(n-1, 11, 'NOMBRE',  style1)
        worksheet.write(n-1, 12, 'GRUPO DE CLIENTE ',  style1)
        worksheet.write(n-1, 13, 'ESTADO',  style1)
        worksheet.write(n-1, 14, 'CODIGO MATERIAL',  style1)
        worksheet.write(n-1, 15, 'DECRIPCION CODIGO MATERIAL',  style1)
        # worksheet.write(n-1, 19, 'GRUPO DE MATERIAL  INVENTARIO',  style1)
        # worksheet.write(n-1, 20, 'GRUPO DE MATERIAL VENTA',  style1)
        worksheet.write(n-1, 16, 'TASA DE IMP ADICIONAL',  style1)
        worksheet.write(n-1, 17, 'CANTIDAD',  style1)
        worksheet.write(n-1, 18, 'UNIDAD DE MEDIDA',  style1)
        worksheet.write(n-1, 19, 'PRECIO  UNITARIO',  style1)
        worksheet.write(n-1, 20, 'NETO',  style1)
        worksheet.write(n-1, 21, 'MONTO IABA',  style1)
        worksheet.write(n-1, 22, 'MONTO IVA',  style1)
        worksheet.write(n-1, 23, 'DESCUENTO',  style1)
        # worksheet.write(n-1, 29, 'FLETE',  style1)
        worksheet.write(n-1, 24, 'TOTAL',  style1)
        worksheet.write(n-1, 25, 'CUENTA CONTABLE CLIENTE',  style1)
        worksheet.write(n-1, 26, 'DESCRIPCION CUENTA CONTABLE CLIENTE',  style1)
        worksheet.write(n-1, 27, 'SOCIEDAD ASOCIADA CTA CLIENTE',  style1)
        worksheet.write(n-1, 28, 'CUENTA E INGRESO',  style1)
        worksheet.write(n-1, 29, 'DESCRIPCION CUENTA CONTABLE INGRESO',  style1)
        worksheet.write(n-1, 30, 'SOCIEDAD ASOCIADA INGRESO',  style1)
        worksheet.write(n-1, 31, 'CEBE',  style1)
        worksheet.write(n-1, 32, 'MONEDA',  style1)
        worksheet.write(n-1, 33, 'NOTA  EN FACTURA',  style1)
        worksheet.write(n-1, 34, 'FECHA DOCUMENT CONTABLE',  style1)
        worksheet.write(n-1, 35, 'ASIENTO CONTABLE',  style1)
        worksheet.write(n-1, 36, 'USUARIO IMPRIME DOCUMENTO',  style1)
        # worksheet.write(n-1, 37, 'DOCUMENTO REBAJA DE INVENTARIO',  style1)


        for rec in etd_document_obj:
            # if rec.class_id.code and rec.number:
                # warehouse = '41'

            for line in rec.invoice_line_ids:

                worksheet.write(n, 0, rec.company_id.name, style)
                worksheet.write(n, 1, rec.invoice_origin or '', style)
                worksheet.write(n, 2, rec.invoice_origin or '', style)
                worksheet.write(n, 3, rec.name or '', style)
                worksheet.write(n, 4, rec.pos_order_ids.payment_ids.payment_method_id.name or '', style)
                worksheet.write(n, 5, rec.pos_order_ids.payment_ids.transaction_id or '', style)
                worksheet.write(n, 6, rec.ref or '', style)
                # worksheet.write(n, 6, rec.ref or '', style)
                # worksheet.write(n, 7, rec.l10n_cl_claim_description or '', style)
                worksheet.write(n, 7, rec.date or '', formato_fecha)
                worksheet.write(n, 8, rec.pos_order_ids.user_id.display_name or '', style)
                worksheet.write(n, 9, rec.type_name or '', style)
                worksheet.write(n, 10, rec.partner_id_vat or '', style)
                # worksheet.write(n, 12, line.sync_reference or '', style)
                # worksheet.write(n, 13, rec.partner_id.id or '', style)
                worksheet.write(n, 11, rec.partner_id.name or '', style)
                worksheet.write(n, 12, rec.partner_id.name or '', style)
                worksheet.write(n, 13, rec.state or '', style)
                worksheet.write(n, 14, line.product_id.code or '', style)
                # worksheet.write(n, 19, '', style)
                # worksheet.write(n, 20, '', style)

                iaba = ''
                iva = ''
                if line.tax_ids:
                    largo = len(line.tax_ids)
                    if largo == 1:
                        iaba = ''
                    else:
                        iaba = line.tax_ids[1].amount
                    iva = line.tax_ids[0].amount

                total_imp = round(line.price_total - line.price_subtotal, 0)

                _logger.info(iaba)
                _logger.info(iva)
                total_imp_tasa = float(iaba or 0.0) + float(iva)

                if iaba is '' or False:
                    iaba = 0
                else:
                    iaba_amount = round((total_imp * iaba) / total_imp_tasa, 0)
                iva_amount = round((total_imp * iva) / total_imp_tasa, 0)

                worksheet.write(n, 15, line.product_id.display_name, style)
                worksheet.write(n, 16, iaba, style)
                worksheet.write(n, 17, line.quantity or '', style)
                worksheet.write(n, 18, line.product_id.uom_name or '', style)
                worksheet.write(n, 19, line.price_unit or '', style)
                worksheet.write(n, 20, line.price_subtotal or '', style)
                worksheet.write(n, 21, iaba_amount, style)
                worksheet.write(n, 22, iva_amount, style)
                worksheet.write(n, 23, line.discount or '', style)
                # worksheet.write(n, 29, line.price_total or '', style)
                worksheet.write(n, 24, line.price_total or '', style)
                worksheet.write(n, 25, rec.partner_id.property_account_receivable_id.code or '', style)
                worksheet.write(n, 26, rec.partner_id.property_account_receivable_id.name or '', style)
                worksheet.write(n, 27, rec.partner_id.property_account_receivable_id.company_id.name or '', style)

                cebe = ''
                if line.posted_payload is not False:
                    assent = json.loads(line.posted_payload)
                    _logger.info(line.posted_payload)
                    _logger.info(type(line.posted_payload))
                    header_temp = assent['HEADER']
                    assent_tmp = assent['DOCUMENT_POST']['ASSENT']
                    _logger.info('largo -> ' + str(len(assent_tmp)))
                    for iterf in assent_tmp:
                        _logger.info('CEBE' + iterf['CEBE'])
                        cebe = iterf['CEBE']
                        account_val = iterf['ACCOUNT']
                        account_desc_val = iterf['GLOSA']
                    sociedad_val = header_temp['SOCIEDAD']

                worksheet.write(n, 28, account_val or '', style)
                worksheet.write(n, 29, account_desc_val or '', style)
                worksheet.write(n, 30, sociedad_val or '', style)
                worksheet.write(n, 31, cebe or '', style)
                worksheet.write(n, 32, rec.currency_id.name or '', style)
                worksheet.write(n, 33, rec.l10n_cl_claim_description or '', style)
                worksheet.write(n, 34, rec.date or '', formato_fecha)
                worksheet.write(n, 35, line.sync_reference or '', style)
                worksheet.write(n, 36, rec.pos_order_ids.user_id.display_name or '', style)
                n = n+1

        fp = io.BytesIO()
        workbook.save(fp)  
        export_id = self.env['etd.document.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()
        
        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'etd.document.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
            
        }
        return True


class EtdDocumentExcel(models.TransientModel):
    _name = "etd.document.excel"
    excel_file = fields.Binary('Excel Report for SaleBook')
    file_name = fields.Char('Excel File', size=64)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
