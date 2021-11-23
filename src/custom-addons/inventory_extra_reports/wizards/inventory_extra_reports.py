from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
import requests, json, io, xlwt
import xlsxwriter, base64
import tempfile

class InventoryExtraReports(models.TransientModel):
    _name = 'inventory.extra.reports'

    company = fields.Many2one('res.company',string="Compañía", required=True)
    fecha_beg = fields.Date(string="Fecha Inicio", required=True)
    fecha_end = fields.Date(string="Fecha Fin", required=True)
    tipo_doc = fields.Selection([('xlsx', 'Excel'), ('html', 'HTML')], default='html', string='Formato')

    def load_inventory_report(self):
        data = {
            'model': 'inventory.extra.reports',
            'form': self.read()[0]
        }

        self.env.cr.execute("""select A.BUIN, A.default_code, A.sentido, sum(qty_sum)
                from (
                 select (case when b2.ccu_code is null then c2.ccu_code else b2.ccu_code end) as BUIN
                 , f.default_code
                 , j.ccu_code_usage as SENTIDO
                 , j.ccu_code_usage as ORIGEN
                 , sum(d.qty_done) as qty_sum
                 from stock_picking a
                  left join stock_picking_type j on j.id = a.picking_type_id
                  left join sale_order k on k.id = a.sale_id
                  left join stock_location b on b.id = a.location_id
                  left join stock_location b2 on b2.id = b.location_id
                  left join stock_location c on c.id = a.location_dest_id
                  left join stock_location c2 on c2.id = c.location_id
                  left join stock_move_line d on d.picking_id = a.id
                  left join product_product e on e.id = d.product_id
                  left join product_template f on f.id = product_tmpl_id
                  left join product_category g on g.id = f.categ_id
                  left join res_partner h on h.id = a.partner_id
                  left join res_partner i on i.id = h.commercial_partner_id
                 where date(a.date_done) between '""" + str(self.read()[0]['fecha_beg']) + "' and '" +  str(self.read()[0]['fecha_end'])+
                "' and (b.company_id = " +str(self.company.id) + " or c.company_id = "+ str(self.company.id) +")" 
                 """ 
                 and (b2.ccu_code is not null or c2.ccu_code is not null)
                 and f.type = 'product'
                 group by b2.ccu_code, c2.ccu_code, f.default_code, a.location_id, g.incoming_code, g.incoming_code_related, g.incoming_code_subsidiary
                  , g.outgoing_code, g.outgoing_code_related, g.outgoing_code_subsidiary, j.ccu_code_usage, g.outgoing_code_no_charge
                ) A
                where A.BUIN is not null
                group by A.BUIN, A.default_code, A.sentido
                order by 1, 2, 4""")

        odoo_results = self.env.cr.fetchall()

        #en vez de consultar en PS, replico query anterior y agrego filtro is_sync = True
        self.env.cr.execute("""select A.BUIN, A.default_code, A.sentido, sum(qty_sum)
                from (
                 select (case when b2.ccu_code is null then c2.ccu_code else b2.ccu_code end) as BUIN
                 , f.default_code
                 , j.ccu_code_usage as SENTIDO
                 , j.ccu_code_usage as ORIGEN
                 , sum(d.qty_done) as qty_sum
                 from stock_picking a
                  left join stock_picking_type j on j.id = a.picking_type_id
                  left join sale_order k on k.id = a.sale_id
                  left join stock_location b on b.id = a.location_id
                  left join stock_location b2 on b2.id = b.location_id
                  left join stock_location c on c.id = a.location_dest_id
                  left join stock_location c2 on c2.id = c.location_id
                  left join stock_move_line d on d.picking_id = a.id
                  left join product_product e on e.id = d.product_id
                  left join product_template f on f.id = product_tmpl_id
                  left join product_category g on g.id = f.categ_id
                  left join res_partner h on h.id = a.partner_id
                  left join res_partner i on i.id = h.commercial_partner_id
                 where date(a.date_done) between '""" + str(self.read()[0]['fecha_beg']) + "' and '" +  str(self.read()[0]['fecha_end'])+
                "' and (b.company_id = " +str(self.company.id) + " or c.company_id = "+ str(self.company.id) +")" 
                 """ 
                 and (b2.ccu_code is not null or c2.ccu_code is not null)
                 and f.type = 'product' and a.is_sync = true
                 group by b2.ccu_code, c2.ccu_code, f.default_code, a.location_id, g.incoming_code, g.incoming_code_related, g.incoming_code_subsidiary
                  , g.outgoing_code, g.outgoing_code_related, g.outgoing_code_subsidiary, j.ccu_code_usage, g.outgoing_code_no_charge
                ) A
                where A.BUIN is not null
                group by A.BUIN, A.default_code, A.sentido
                order by 1, 2, 4""")

        SAP_results = self.env.cr.fetchall()

        temp = []
        index_temp = []
        # url_base = self.get_BUS_url()
        # resp = requests.get(
        # url_base + '/services/movimientosInventario/TransaccionesInventarioResumen?BUSINESS_UNIT=EM81B&V84IN_FECHA_INI=' + str(
        #     self.read()[0]['fecha_beg']) + "&V84IN_FECHA_END=" + str(self.read()[0]['fecha_end']),
        # headers={"Accept": "application/json"})

        # if resp.status_code != 200:
        #     raise UserError("Error, no se pudo conectar a Peoplesoft")

        var_dict_ps = {
            "EM9780": "DISPENSADOR PEDESTAL BOT. AF",
            "EM9781": "DISPENSADOR PEDESTAL RED AF",
            "EM9784": "DISPENSADOR AGUA Y HIELO",
            "ET8703078": "MANANTIAL SG BOTELLON 20LT",
            "ET8703086": "MANANTIAL SG BOTELLON 12LT",
            "E56621": "ENVASE BOTELLON 20 LTS",
            "269064": "SOPORTE BOTELLON",
            "269066": "SOPORTE DE CERAMICA SOBREMESA",
            "269092": "ENVASE BOTELLON 20 LTS VENTA"
        }

        for line in odoo_results:
            if line[1] in var_dict_ps:
                product_name = var_dict_ps[str(line[1])]
            else:
                product_name = self.env['product.template'].search([('default_code', '=', line[1])], limit=1).name

            if line[1] is None:
                product_name = ''
            total_ps = 0

            if len(SAP_results)>0:
                for reg in SAP_results:
                    if reg[0] == line[0] and reg[1] == line[1] and reg[2] == line[2]:
                        total_ps = reg[3]

            vals = {
                'BU': line[0],
                'INV_ITEM_ID': line[1],
                'NAME': product_name,
                'SENTIDO': line[2],
                'ODOO_TOTAL_QTY': line[3],
                'PS_TOTAL_QTY': total_ps,
                'DIFF': str(int(line[3]) - int(total_ps))
            }
            temp.append(vals)
        # if len(resp.json()['Entries']['Entry']) > 0:
        # for reg in resp.json()['Entries']['Entry']:
        #     if not resp.json()['Entries']['Entry'].index(reg) in index_temp:
        #         product_name = self.env['product.template'].search([('code_peoplesoft', '=', reg['INV_ITEM_ID'])],
        #                                                       limit=1).name
        #         vals = {
        #             'BU': reg['BUSINESS_UNIT'],
        #             'INV_ITEM_ID': reg['INV_ITEM_ID'],
        #             'NAME': product_name,
        #             'SENTIDO': reg['V84IN_SENTIDO'],
        #             'ORIGEN': reg['V84IN_ORIGEN_INFO'],
        #             'ODOO_TOTAL_QTY': 0,
        #             'PS_TOTAL_QTY': reg['TOTAL_QTY'],
        #             'DIFF': str(0 - int(reg['TOTAL_QTY']))
        #         }
        #         temp.append(vals)

        data['rows'] = temp
        data['now'] = datetime.now()
        data['reporte'] = "Reporte Cuadratura Transacciones de Inventario por Ventas SAP"

        if (self.read()[0]['tipo_doc'] == 'xlsx'):
            return self.report_to_xlsx(data)
        else:
            return self.env.ref('inventory_extra_reports.cuadratura_inventario_report').report_action(self, data=data)

    def report_to_xlsx(self, data):

        filename = 'Reporte' + str(data['form']['fecha_end']) + '.xls'
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Hoja 1')
        worksheet.write(0, 0, data['reporte'])
        worksheet.write(1, 0, 'Fecha desde: ' + str(data['form']['fecha_beg']))
        worksheet.write(2, 0, 'Fecha hasta: ' + str(data['form']['fecha_end']))
        worksheet.write(2, 4, 'Fecha generación: ' + str(data['now']))

        f = 4
        c = 0
        for key, value in data['rows'][0].items():
            worksheet.write(f, c, key)
            c = c + 1
        c = 0
        f = 5
        for item in data['rows']:
            for key, value in item.items():
                worksheet.write(f, c, value)
                c = c + 1
            f = f + 1
            c = 0

        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['inventory.extra.reports.excel'].create(
            {'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        fp.close()

        action = self.env.ref('inventory_extra_reports.inventory_extra_reports_excel_view_wizard').read()[0]
        action['res_id'] = export_id.id
        return action

    def get_BUS_url(self):
        bus_server = self.env['backend.acp'].search([('connection_type', '=', 'esb'), ('active', '=', True)])
        bus_server.ensure_one()
        return bus_server.host + ':' + str(bus_server.port)


class ReportExcel(models.TransientModel):
    _name = 'inventory.extra.reports.excel'

    excel_file = fields.Binary('Excel Report for Checks')
    file_name = fields.Char()
