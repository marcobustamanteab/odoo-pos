from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
import requests, json, io, xlwt
import xlsxwriter, base64
import tempfile


class AccountingExtraReports(models.TransientModel):
    _name = 'accounting.extra.reports'

    company = fields.Many2one('res.company', string = "Compañía")
    fecha_beg = fields.Date(string = "Fecha Inicio")
    fecha_end = fields.Date(string = "Fecha Fin")
    tipo_doc = fields.Selection([('xlsx', 'Excel'), ('html', 'HTML')], default='html', string='Formato')
    cliente_id = fields.Many2one('res.partner', string="Cliente",  domain="[('parent_id', '=', False)]")

    def cargar_reporte_asientos(self):
        data = {
            'model': 'accounting.extra.reports',
            'form': self.read()[0]
        }
        temp=[]
        host = self.company.backend_esb_id.host
        port = self.company.backend_esb_id.port
        # resp = requests.get(str(host) + ":" + str(port) +"/services/PeopleSoft_AsientosContables/resumenasientos?BUSINESS_UNIT="+str(self.company.ccu_business_unit)+"&ACCOUNTING_DT_INI=" + str(self.read()[0]['fecha_beg']) + "&ACCOUNTING_DT_END=" + str(self.read()[0]['fecha_end']), headers={"Accept":"application/json"})
        # if resp.status_code != 200:
        #     raise UserError("Error, no se pudo conectar a Peoplesoft")

        journals_sync= self.env['account.journal'].search(
            [
                ('ccu_sync', '=', True), ('type', '!=', 'bank')
            ]
        )

        move_lines = self.env['account.move.line'].read_group(
            [
                ('date', '>=', str(self.read()[0]['fecha_beg'])),
                ('journal_id', 'in', journals_sync.ids),
                ('date', '<=', str(self.read()[0]['fecha_end']))
            ],
            ['account_id', 'balance'],
            ['account_id']
        )

        move_lines_in_sap = self.env['account.move.line'].read_group(
            [
                ('move_id.is_sync', '=', True),
                ('date', '>=', str(self.read()[0]['fecha_beg'])),
                ('journal_id', 'in', journals_sync.ids),
                ('date', '<=', str(self.read()[0]['fecha_end']))
            ],
            ['account_id', 'balance'],
            ['account_id']
        )
        move_lines_not_in_sap = self.env['account.move.line'].read_group(
            [
                ('move_id.is_sync', '=', False),
                ('date', '>=', str(self.read()[0]['fecha_beg'])),
                ('journal_id', 'in', journals_sync.ids),
                ('date', '<=', str(self.read()[0]['fecha_end']))
            ],
            ['account_id', 'balance'],
            ['account_id']
        )
        print(move_lines_in_sap)
        # Lista de ids de la cola de asientos con error desde la cola
        # id_pnd = self.pending_move_lines()
        #
        # pending_ml = self.env['account.move.line'].read_group(
        #     [
        #         ('move_id', 'in', id_pnd),
        #         ('date', '>=', str(self.read()[0]['fecha_beg'])),
        #         ('date', '<=', str(self.read()[0]['fecha_end']))
        #     ],
        #     ['account_id', 'balance'], ['account_id'])
        total_ps = 0
        total_odoo = 0
        total_trn = 0
        for ac in move_lines:
            ps_amount = 0
            odoo_pnd = 0
            ac_odoo = self.env['account.account'].search([('id', '=', ac['account_id'][0])])

            # if resp.json()['Entries']['Entry']:
            #     for ps_ac in resp.json()['Entries']['Entry']:
            #         if ps_ac['ACCOUNT'] == ac_odoo.code:
            #             ps_amount = ps_ac['TOTAL_MONETARY_AMOUNT']
            #             break

            if move_lines_in_sap:
                for ps_ac in move_lines_in_sap:
                    ac_odoo_line = self.env['account.account'].search([('id', '=', ps_ac['account_id'][0])])
                    if ac_odoo_line.code == ac_odoo.code:
                        ps_amount = ps_ac['balance']
                        break

            if move_lines_not_in_sap:
                for pnd in move_lines_not_in_sap:
                    if pnd['account_id'][0] == ac_odoo.id:
                        odoo_pnd = pnd['balance']
                        break
            vals = {
                'UEN': 'EM81B',
                'ACCOUNT': ac_odoo.ccu_code,
                'NAME': ac_odoo.name,
                'ODOO_AMOUNT': ac['balance'],
                'PS_AMOUNT': ps_amount,
                'DIFF': str(int(ac['balance'])-int(ps_amount)),
                'TRN_PND': odoo_pnd
            }
            total_ps = total_ps + int(ps_amount)
            total_odoo = total_odoo + int(ac['balance'])
            total_trn = total_trn + int(odoo_pnd)
            temp.append(vals)

        vals = {
            'UEN': '',
            'ACCOUNT': '',
            'NAME': 'TOTAL',
            'ODOO_AMOUNT': total_odoo,
            'PS_AMOUNT': total_ps,
            'DIFF': str(int(total_odoo) - int(total_ps)),
            'TRN_PND': total_trn
        }
        # Elimino totales, evaluar si se requiere
        #temp.append(vals)
        data['empresa'] = self.company.name
        data['rows'] = temp
        data['now'] = datetime.now()
        data['reporte'] = "Reporte Integridad Contable Odoo - PS"

        if (self.read()[0]['tipo_doc'] == 'xlsx'):
            return self.report_to_xlsx(data)
        else:
            return self.env.ref('accounting_extra_reports.cuadratura_asientos_report').report_action(self, data=data)


    def report_to_xlsx(self, data):

        filename = 'Reporte'+str(data['form']['fecha_end'])+'.xls'
        workbook=xlwt.Workbook()
        worksheet=workbook.add_sheet('Hoja 1')
        worksheet.write(0,0, data['reporte'])
        worksheet.write(1,0, 'Fecha desde: ' + str(data['form']['fecha_beg']))
        worksheet.write(2,0, 'Fecha hasta: ' + str(data['form']['fecha_end']))
        worksheet.write(2,4, 'Fecha generación: ' + str(data['now']))

        f = 4
        c = 0
        for key,value in data['rows'][0].items():
            worksheet.write(f, c, key)
            c=c+1
        c=0
        f=5
        for item in data['rows']:
            for key, value in item.items():
                worksheet.write(f, c, value)
                c=c+1
            f=f+1
            c=0

        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['accounting.extra.reports.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name':filename})
        fp.close()

        action = self.env.ref('accounting_extra_reports.accounting_extra_reports_excel_view_wizard').read()[0]
        action['res_id']=export_id.id
        return action

    # def pending_move_lines(self):
    #     pending_job = self.env['queue.job'].sudo().search([('state', '=', 'failed'), ('method_name', '=', 'esb_send_account_move'), ('company_id', '=', self.company.id)])
    #     temp=[]
    #     for pnd in pending_job:
    #         temp.append(pnd.record_ids[0])
    #     return temp
    #

class ReportExcel(models.TransientModel):
    _name = 'accounting.extra.reports.excel'

    excel_file = fields.Binary('Excel Report for Checks')
    file_name = fields.Char()