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
import re,sys
import io
from odoo import api, fields, models
from xlwt import easyxf
import csv
import time
from datetime import datetime, date

import logging
_logger = logging.getLogger(__name__)



class account_move_excel_wizard_form(models.TransientModel):
    _name ='wizard.export.account.invoice'

    company = fields.Many2one('res.company', string = "Compañía")
    date_to = fields.Date('Date To', required=True, default=lambda self: str(datetime.now()))
    date_from = fields.Date('Fecha Inicial', required=True, default=lambda self: time.strftime('%Y-%m-01'))

    def _compute_deposit(self):
        line = self.move_line_ids.filtered(lambda r: r.draft_assigned == True)
        if line:
            self.deposit_ok = True
            self.date_deposit = line.date_maturity
        else:
            self.deposit_ok = False


    
    def account_invoice_excel(self):

        date_stop = self.date_to
        fecha = date_stop.strftime("%Y-%m-%d")       
        i = 1
        sheetName = 1
        workbook = xlwt.Workbook()
        
        n = 2
        c = 0
        style1 = xlwt.easyxf('pattern: pattern solid, fore_colour blue;''font: colour white, bold True;')
        filename = 'LibroVentasCo'+str(self.date_to)+'.xls'
        style = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;') # 36pt
        font = xlwt.Font()
        font.name = 'Times New Roman'
        font.bold = True
        font.height = 250
        currency = xlwt.easyxf('font: height 180; align: wrap yes, horiz right',num_format_str='#,##0.00') 
        formato_fecha=xlwt.easyxf(num_format_str='DD-MM-YY')
        worksheet = workbook.add_sheet("Libro de Ventas "+str(self.date_to))
        
        #sales_journal = self.env['account.journal'].search([('name', '=', 'Ventas'),], limit=1)

        account_invoice_obj = self.env['account.move'].search(
            [
                ('company_id.id', '=', self.company.id),
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', 'not in', ['canceled', 'draft'])
            ]
        )

        #,('picking_type_id.code', '=', 'outgoing')


        worksheet.col(0).width = 3000
        worksheet.col(1).width = 2500
        #LINE
        worksheet.col(2).width = 1500
        #JOURNAL
        worksheet.col(3).width = 4500
        #FECHA EMISION
        worksheet.col(4).width = 5000
        #DATE
        worksheet.col(5).width = 5000
        worksheet.col(6).width = 3000
        worksheet.col(7).width = 3000
        worksheet.col(8).width = 3000
        worksheet.col(9).width = 13000
        worksheet.col(10).width = 3000
        worksheet.col(11).width = 3000
        worksheet.col(12).width = 3000
        worksheet.col(13).width = 3000
        worksheet.col(14).width = 3000
        worksheet.col(15).width = 3000
        worksheet.col(16).width = 3000
        worksheet.col(17).width = 3000
        worksheet.col(18).width = 3000
        worksheet.col(19).width = 3000
        worksheet.col(20).width = 3000
        worksheet.col(21).width = 3000
        worksheet.col(22).width = 3000

        
 
        worksheet.merge(0, 0, 0, 21, style1) 
        worksheet.write(n-2, 0, 'Libro de venta', style1)                    
        worksheet.write(n-1, 0, 'Tipo de venta', style1)
        worksheet.write(n-1, 1, 'Descripción', style1)
        worksheet.write(n-1, 2, 'Uen', style1)
        worksheet.write(n-1, 3, 'Tipo de documento', style1)
        worksheet.write(n-1, 4, 'Fecha de emisión', style1)
        worksheet.write(n-1, 5, 'Número de documento', style1)
        worksheet.write(n-1, 6, 'Rut', style1)
        worksheet.write(n-1, 7, 'Dv', style1)
        worksheet.write(n-1, 8, 'Cliente', style1)
        worksheet.write(n-1, 9, 'Razón social', style1)
        worksheet.write(n-1, 10, 'Planilla', style1)
        worksheet.write(n-1, 11, 'Depósito', style1)
        worksheet.write(n-1, 12, 'Territorio', style1)
        worksheet.write(n-1, 13, 'Oficina', style1)
        worksheet.write(n-1, 14, 'Origen', style1)
        worksheet.write(n-1, 15, 'Monto Neto', style1)
        worksheet.write(n-1, 16, 'Monto IVA', style1)
        worksheet.write(n-1, 17, 'Monto IABA', style1)
        worksheet.write(n-1, 18, 'Monto Exento', style1)
        worksheet.write(n-1, 19, 'Monto Total', style1)
        worksheet.write(n-1, 20, 'Uen Relacionada', style1)
        worksheet.write(n-1, 21, 'Anulado', style1)
        #worksheet.write(n-1, 22, 'Fecha de Firma', style1)

        
        for rec in account_invoice_obj:
            #if rec.class_id.code and rec.number:
            config = self.env['fiscal.dte.printing.config'].search([('company_id', '=', rec.company_id.id)], limit=1)
            if rec.name:
                worksheet.write(n, 0, rec.l10n_latam_document_type_id.name, style)
                worksheet.write(n, 1, "", style)
                worksheet.write(n, 2, self.env.user.company_id.ccu_business_unit or 'UEN', style)
                worksheet.write(n, 3, rec.l10n_latam_document_type_id.code or '', style)
                worksheet.write(n, 4, rec.invoice_date, formato_fecha)
                #TODO cambiar name por solo numeros
                worksheet.write(n, 5, rec.name, style)
                rut, dv = rec.partner_id.vat.split('-') if not rec.partner_id.use_generic_sap_client else rec.partner_id.generic_RUT.split('-')
                worksheet.write(n, 6, rut, style)
                worksheet.write(n, 7, dv, style)
                sap_code = rec.partner_id.sap_code if not rec.partner_id.use_generic_sap_client else rec.partner_id.generic_sap_code or ''
                worksheet.write(n, 8, sap_code or '', style)
                worksheet.write(n, 9, rec.partner_id.name or '', style)
                fs_name = ''
                # for line in rec.fsm_order_ids:
                #     if line.name:
                #         fs_name = line.name
                worksheet.write(n, 10, fs_name or '', style)
                #PENDIENTE
                warehouse = '123'
                warehouse = rec.team_id.branch_ccu_code or 0
                #if rec.origin:
                #    sale = self.env['sale.order'].search([('name', '=', rec.origin.split(',')[1].lstrip())])
                #    if sale:
                #        warehouse = sale.warehouse_id[:1]
                worksheet.write(n, 11, warehouse, style)
                worksheet.write(n, 12, '', style)
                # PENDIENTE
                #worksheet.write(n, 13, rec.partner_id.branch_id.commercial_office or "0", style)
                oficina = rec.pos_order_id.sequence_prefix or ''
                worksheet.write(n, 13, oficina, style)
                worksheet.write(n, 14, "ODOO", style)
                worksheet.write(n, 15, rec.amount_untaxed, style)

                # worksheet.write(n, 16, rec.amount_tax, style)
                # worksheet.write(n, 17, "", style)
                tax_19 = 0
                tax_iaba = 0
                print(rec.amount_by_group)
                for tax_group in rec.amount_by_group:
                    group_id = tax_group[6]
                    if group_id == config.tax_6_id.id:
                        tax_19 += tax_group[1]
                    else:
                        tax_iaba += tax_group[1]

                worksheet.write(n, 16, tax_19, style)
                worksheet.write(n, 17, tax_iaba, style)

                totals = 0
                # for line in rec.invoice_line_ids:
                #     if line.price_tax == 0:
                #         totals = totals + line.price_subtotal
                worksheet.write(n, 18, totals, style)
                worksheet.write(n, 19, rec.amount_total, style)
                #PENDIENTE
                #worksheet.write(n, 20, rec.company_id.backend_acp_id.xerox_company_code, style)
                worksheet.write(n, 20, "0", style)
                worksheet.write(n, 21, "", style)
                #worksheet.write(n, 22, rec.date_sign, formato_fecha)
                n = n+1
      
        fp = io.BytesIO()
        workbook.save(fp)  
        export_id = self.env['account.invoice.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()
        
        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'account.invoice.excel',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
            
        }
        return True

class picking_centralized_excel(models.TransientModel):
    _name= "account.invoice.excel"
    excel_file = fields.Binary('Excel Report for SaleBook')
    file_name = fields.Char('Excel File', size=64)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
