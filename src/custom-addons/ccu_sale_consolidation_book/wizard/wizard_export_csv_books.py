
import io
import csv
import base64
import logging
import time
from datetime import datetime
from dateutil import relativedelta

from odoo import models, api, fields
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class WizardExportCsv(models.TransientModel):

    _name = 'wizard.export.csv.books'
    _description = 'Wizar de Exportación'
    company = fields.Many2one('res.company', string="Compañía")
    delimiter = {
        'comma':  ',',
        'dot_coma':  ';',
        'tab':  '\t',
    }
    quotechar = {
        'colon':  '"',
        'semicolon':  "'",
        'none':  '',
    } 
    
    date_from = fields.Date('Fecha Inicial', required=True, default=lambda self: time.strftime('%Y-%m-01'))
    date_to = fields.Date('Fecha Final', required=True, default=lambda self: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    file_data = fields.Binary('Archivo Generado')
    file_name = fields.Char('Nombre de archivo')

    delimiter_option = fields.Selection([
        ('colon','Comillas Dobles(")'),
        ('semicolon',"Comillas Simples(')"),
        ('none',"Ninguno"),
        ], string='Separador de Texto', default='colon', required=True)

    delimiter_field_option = fields.Selection([
        ('comma','Coma(,)'),
        ('dot_coma',"Punto y coma(;)"),
        ('tab',"Tabulador"),
        ], string='Separador de Campos', default='dot_coma', required=True)
    
    #@api.multi
    def show_view(self, name):
        search_ids = self.env['wizard.export.csv.books'].search([])
        last_id = search_ids and max(search_ids)        
        return {
            'name': name,
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.export.csv.books',
            'res_id': last_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    
    # @api.multi
    def action_generate_csv(self):
        file_name = "DTE_LVDE_%s_%s%s_%s.txt" % (
        self.env.user.company_id.vat[:-2], self.date_from.strftime('%Y'), self.date_from.strftime('%m'),
        self.date_from.strftime('%d'))
        folder_path = "/lv_truck/"

        if self.env.context.get('remote_folder') == 1:
            output = open(folder_path + file_name, "w")
        else:
            output = io.StringIO()

        if self.delimiter_option == 'none':
            writer = csv.writer(output, delimiter=self.delimiter[self.delimiter_field_option], quoting=csv.QUOTE_NONE)
        else:
            writer = csv.writer(output, delimiter=self.delimiter[self.delimiter_field_option], quotechar=self.quotechar[self.delimiter_option], quoting=csv.QUOTE_NONE)
        # sales_journal = self.env['account.journal'].search([('name', '=', 'Ventas'),], limit=1)
        #invoice_recs = self.env['account.invoice'].search([('date_invoice','>=',self.date_from), ('date_invoice','<=',self.date_to),('journal_id','=',sales_journal.id),  ('state' ,'not in',['canceled','draft'])])
        invoice_recs = self.env['account.move'].search(
            [
                ('company_id.id', '=', self.company.id),
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', 'not in', ['canceled', 'draft'])
            ]
        )
        for invoice in invoice_recs:
            if invoice.l10n_latam_document_type_id.code and  invoice.name:
                tax_19 = 0
                tax_iaba = 0

                config = self.env['fiscal.dte.printing.config'].search([('company_id', '=', invoice.company_id.id)],
                                                                       limit=1)
                for tax_group in invoice.amount_by_group:
                    group_id = tax_group[6]
                    if group_id == config.tax_6_id.id:
                        tax_19 += tax_group[1]
                    else:
                        tax_iaba += tax_group[1]
                line_invoice = [
                                 #Descripción
                                 invoice.l10n_latam_document_type_id.code or '',
                                 #Descripción
                                 int(''.join([i for i in invoice.name if i.isdigit()])) or '',
                                 #3
                                 "",
                                 #4
                                 "",
                                 #5
                                 "",
                                "19",
                                 #7
                                 "",
                                 #8
                                 "",
                                 #9
                                 "",
                                 invoice.invoice_date,
                                 #11
                                 "",
                                 invoice.partner_id.vat,
                                 invoice.partner_id.name,
                                 #14
                                 "",                             
                                 #15
                                 "",
                                 "0",
                                 int(invoice.amount_untaxed),
                                 int(tax_19),
                                 #19
                                 int(tax_iaba),
                                 #20
                                 "",
                                 #21
                                 "",
                                 #22
                                 "",
                                 #23
                                 "",
                                 #24
                                 "",
                                 #25
                                 "",
                                 #26
                                 "",
                                 #27
                                 "",
                                 #28
                                 "",
                                 #29
                                 "",
                                 #30
                                 "",
                                 #31
                                 "",
                                 #32
                                 "",
                                 #33
                                 "",
                                 #34
                                 "",
                                 #35
                                 "",
                                 #36
                                 "",
                                 #37
                                 "",
                                 #38
                                 "",
                                 #39
                                 "",
                                 #40
                                 "",
                                 #41
                                 "",
                                 #42
                                 "",
                                 #43
                                 "",
                                 #44
                                 "",
                                 #45
                                 "",
                                 #46
                                 "",
                                 #47
                                 "",
                                 #48
                                 "",
                                 #49
                                 "",
                                 #50
                                 "",
                                 #51
                                 "",
                                 #52
                                 "",
                                 #53
                                 "",
                                 #54
                                 "",
                                 #55
                                 "",
                                 #56
                                 "",
                                 #57
                                 "",
                                 #58
                                 "",
                                 #59
                                 "",
                                 #60
                                 "",
                                 #61
                                 "",
                                 #62
                                 "",
                                 #63
                                 "",
                                 #64
                                 "",
                                 #65
                                 "",
                                 #66
                                 "",
                                 #67
                                 "",
                                 #68
                                 "",
                                 #69
                                 "",
                                 #70
                                 "",
                                 #71
                                 "",
                                 #72
                                 "",
                                 #73
                                 "",
                                 #74
                                 "",
                                 #75
                                 "",
                                 #76
                                 "",
                                 #77
                                 "",
                                 #78
                                 "",
                                 #79
                                 "",
                                 #70
                                 "",
                                 #81
                                 "",
                                 #82
                                 "",
                                 #83
                                 "",
                                 #84
                                 "",
                                 #85
                                 "",
                                 #86
                                 "",
                                 #87
                                 "",
                                 #88
                                 "",
                                 #89
                                 "",
                                 #90
                                 "",
                                 #91
                                 "",
                                 #92
                                 "",
                                 #93
                                 "",
                                 #94
                                 "",
                                 #95
                                 "",
                                 #96
                                 int(invoice.amount_total),
                                 #97
                                 "",
                                 #98
                                 "",
                                 #99
                                 "",
                                 #100
                                 "",
                                 #101
                                 "",
                                 #102
                                 "",
                                 #103
                                 "",
                                 #104
                                 "",
                                 "0",
                                 #104
                                 "S",
                                 #105
                                 invoice.team_id.branch_ccu_code or 0,
                                 ]
                writer.writerow([str(l) for l in line_invoice])
        if self.env.context.get('remote_folder') == 1:
            return self.show_view(u'Libro enviado a Truck')
        else:
            self.write({'file_data': base64.encodebytes(output.getvalue().encode()), 'file_name': file_name, })
            return self.show_view(u'Libro Generado')
