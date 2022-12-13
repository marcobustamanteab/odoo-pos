from datetime import date
import base64
import requests
import logging
import json
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = ['account.move']


    _truck_operation = 'Venta'
    _truck_origen = 'ODOO'
    _truck_date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    lvdet_sync_date = fields.Date(
        string='Fecha de sincronizacion'
    )
    lvdet_sync_confirmado_date = fields.Date(
        string='Fecha de cierre de periodo'
    )    
    lvdet_sync = fields.Boolean(
        string='Dato Sincronizado'
    )
    lvdet_sync_confirmado = fields.Boolean(
        string='Confirmación de cierre de periodo'
    )
    lvdet_payload = fields.Binary(
        string='Datos Transferidos'
    )
    lvdet_message = fields.Char(
        string='Mensajes y comentarios'
    )

    def lvdet_sync_registry(self):
        registry = self._create_lvdet_registry()
        return ''
        

    def _lvdet_sync_data(self):
        invoice_recs = self.env['account.move'].sudo().search(
            [
                ('company_id.id', '=', self.company.id),
                ('invoice_date', '>=', self.date_from),
                ('invoice_date', '<=', self.date_to),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', 'not in', ['cancel', 'draft'])
            ]
        )
        for rec in invoice_recs:
            self._create_async_header.with_delay(rec)


    def _create_async_header(self, invoice):
        header = self._create_async_header(invoice)
        response = self._sync_create_registry(header)
        if response.code is not True:
            raise ValueError('error en los datos')


    def _sync_create_registry(self, header):
        return self.post(header)

    def _sync_local_get_origin(self):
        return ''

    def _sync_local_get_header(self):
        return ''


    def _get_lvdet_monthly_header_api_data(self, mes, anio):
        return {
            'razon_social_comercial': self.company_id.lvta_razon_social_comercial,
            'periodo_anio': anio,
            'periodo_mes': mes,
            'tipo_operacion': self.company_id.lvta_tipo_operacion
        }

    def _get_lvdet_monthly_origin_api_data(self, mes, anio):
        return {
            'razon_social_comercial': self.company_id.lvta_razon_social_comercial,
            'periodo_anio': anio,
            'periodo_mes': mes,
            'tipo_operacion': self.company_id.lvta_tipo_operacion,
            'tipo_origen': self.company_id.lvta_tipo_origen
        }

    def _get_lvdet_monthly_registry_api_data(self, mes, anio, tipo_doc, num_doc):
        return {
            'razon_social_comercial': self.company_id.lvta_razon_social_comercial,
            'periodo_anio': anio,
            'periodo_mes': mes,
            'tipo_operacion': self.company_id.lvta_tipo_operacion,
            'tipo_origen': self.company_id.lvta_tipo_origen,
            'tipo_de_documento': tipo_doc,
            'numero_de_documento': num_doc
        }

    def _create_lvdet_monthly_header_api_data(self, mes, anio):
        return {
            'razon_social_comercial': self.company_id.lvta_razon_social_comercial,
            'periodo_anio': anio,
            'periodo_mes': mes,
            'tipo_operacion': self.company_id.lvta_tipo_operacion,
            'tipo_origen': self.company_id.lvta_tipo_origen,
            'flag_carga_truck': 'N',
            'flag_carga_peoplesoft': 'N',
            'flag_carga_vyd': 'N',
            'codigo_de_estado': 'AB',
            'fecha_envio_sii': date.today.strftime(self._truck_date_format),
            'flag_carga_odoo': 'S',
            'origen_5': 'N',
            'origen_6': 'N',
            'origen_7': 'N',
            'origen_8': 'N'
        }


    def _create_lvdet_monthly_origin_api_data(self, mes, anio):
        return {
            'razon_social_comercial': self.company_id.lvta_razon_social_comercial,
            'periodo_anio': anio,
            'periodo_mes': mes,
            'tipo_operacion': self.company_id.lvta_tipo_operacion,
            'tipo_operacion': self.company_id.lvta_tipo_origen,
            'origen_fecha': date.today.strftime(self._truck_date_format),
            'estado_origen': 'GEN',
            'ruta_archivo': '',
            'tipo_proceso': 'A'
        }

    #### Client Api Operation

    def _create_lvdet_registry_api(self, data):
        backend = self.company_id.backend_esb_id
        url = backend.host + ':' + str(backend.port) + '/api/libroventas/libro/crear'
        headers = {
            'Content-Type': 'application/json',
        }
        r = self._api_client(data, 'PUT', headers, url)
        _logger.info(type(r))
        resp = r.json()
        # resp = {
        #     "respuesta": "Creacion Exitosa de Registros",
        #     "detalle": "Los registros fueron creacion exitosamente"
        # }
        _logger.info(resp)        
        return resp

    def _get_lvdet_monthly_header_api(self, mes, anio):
        data = self._get_lvdet_monthly_header_api_data(mes, anio)
        backend = self.company_id.backend_esb_id
        url = backend.host + ':' + str(backend.port) + 'api/libroventas/cabecera/obtener'
        headers = {
            'Content-Type': 'application/json',
        }
        r = self._api_client(data, 'POST', headers, url)
        # raise ValueError(r)
        # respuesta = r.json()
        # respuesta = {
        #     "cabeceras": {
        #         "cabecera": {
        #             "razon_social_comercial": 7,
        #             "fecha_envio_sii": "2021-12-30T01:00:00.000-03:00",
        #             "codigo_de_estado": "AB",
        #             "origen_5": "S",
        #             "origen_6": "S",
        #             "flag_carga_vyd": "S",
        #             "origen_7": "S",
        #             "origen_8": "S",
        #             "periodo_mes": 12,
        #             "flag_carga_odoo": "N",
        #             "periodo_anio": 2022,
        #             "flag_carga_peoplesoft": "S",
        #             "flag_carga_truck": "S",
        #             "tipo_operacion": "Venta"
        #         }
        #     }
        # }
        _logger.info(r)        
        # return respuesta

    def _get_lvdet_monthly_origin_api(self, mes, anio):
        data = self._get_lvdet_monthly_origin_api_data(mes, anio)
        backend = self.company_id.backend_esb_id
        url = backend.host + ':' + str(backend.port) + 'api/libroventas/origen/obtener'
        headers = {
            'Content-Type': 'application/json',
        }
        r = self._api_client(data, 'POST', headers, url)
        # raise ValueError(type(r))
        _logger.info(type(r))
        # respuesta = r.json()
        # respuesta = {
        #     "origenes": {
        #         "origen": {
        #             "razon_social_comercial": 7,
        #             "tipo_origen": "ODO",
        #             "estado_origen": "GEN",
        #             "ruta_archivo": "nnnnnnn                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         ",
        #             "periodo_mes": 12,
        #             "tipo_proceso": "A",
        #             "periodo_anio": 2022,
        #             "origen_fecha": "2021-12-30T01:00:00.000-03:00",
        #             "tipo_operacion": "Venta"
        #         }
        #     }
        # }
        _logger.info(r)        
        return r


    def _lvdet_sync_registry_data(self, impuestos, iva):
        return {
                'registro': {
                    'razon_social_comercial': self.partner_id.id,
                    'periodo_anio': self.date.year,
                    'periodo_mes': self.date.month,
                    'tipo_operacion': str(self._truck_operation),
                    'tipo_origen': str(self._truck_origen),
                    'tipo_de_documento': self.l10n_latam_document_type_id_code,
                    'numero_de_documento': self.l10n_latam_document_number,
                    'numero_interno': self.id,
                    'centro_distribución': 0,
                    'mes_documento': self.date.month,
                    'dia_documento': self.date.day,
                    'fecha': date.today().strftime(self._truck_date_format),
                    'documento_anulado': '.',
                    'codigo_operación': 0,
                    'tipo_impuesto': 0,
                    'tasa_impuesto': iva.tax_line_id.amount,
                    'indicador_servicio': 0,
                    'indicador_sin_costo': 0,
                    'fecha_documento': self.date.strftime(self._truck_date_format),
                    'codigo_sucursal': 0,
                    'rut_documento': self.partner_id_vat.split('-')[0],
                    'dv': self.partner_id_vat.split('-')[1],
                    'razon_social': self.invoice_partner_display_name,
                    'tipo_documento_referencia': 0,
                    'folio_documento_referencia': 0,
                    'monto_exento': 0,
                    'monto_neto': self.amount_untaxed,
                    'monto_iva': iva.l10n_latam_price_subtotal,
                    'monto_activo_fijo': 0,
                    'iva_uso_comun': 0,
                    'iva_fuera_de_plazo': 0,
                    'total_ley18211': 0,
                    'monto_sin_credito': 0,
                    'iva_retenido_total': 0,
                    'iva_retenido_parcial': 0,
                    'cre_dec': 0,
                    'deposito_de_envase': 0,
                    'monto_total': self.amount_total_signed,
                    'iva_no_etenido': 0,
                    'total_monto_no_facturado': 0,
                    'total_monto_per': 0,
                    'venta_pasaje_nacional': 0,
                    'venta_pasaje_internacional': 0,
                    'puros': 0,
                    'cigarrillos': 0,
                    'elaborados': 0,
                    'impuesto_vehiculos': 0,
                    'uen_propietaria': 7,
                    'total_flete': 0,
                    'fecha_vencimiento': self.date.strftime(self._truck_date_format),
                    'total_descuento': 0,
                    'id_cliente': 0,
                    'monto_iva_propio': 0,
                    'monto_iva_tercero': 0,
                    'planilla': 0,
                    'id_oficina': 0,
                    'id_territorio': 0,
                    'cod_mov': 0,
                    'flag_factura_del_giro': 'S',
                    'numero_asiento': self.id,
                    'pendiente': 0,
                    'uuid': 'mm'
                },
                'impuestos': impuestos
            }


    def _create_lvdet_monthly_header_local(self):
        self.env['salebook.header'].write(
            {
                'razon_social_comercial': self.company_id.lvta_razon_social_comercial,
                'periodo_anio': self.date.year,
                'periodo_mes': self.date.month,
                'tipo_operacion': self.company_id.lvta_tipo_operacion,
                'tipo_origen': self.company_id.lvta_tipo_origen,
                'flag_carga_truck': 'N',
                'flag_carga_peoplesoft': 'N',
                'flag_carga_vyd': 'N',
                'codigo_de_estado': 'AB',
                'fecha_envio_sii': date.today().strftime(self._truck_date_format),
                'flag_carga_odoo': 'S',
                'origen_5': 'N',
                'origen_6': 'N',
                'origen_7': 'N',
                'origen_8': 'N'
            }            
        )


    def _create_lvdet_monthly_origin_local(self):
        self.env['salebook.origin'].write(
            {
                'razon_social_comercial': self.company_id.lvta_razon_social_comercial,
                'periodo_anio': self.date.year,
                'periodo_mes': self.date.month,
                'tipo_operacion': self.company_id.lvta_tipo_operacion,
                'tipo_operacion': self.company_id.lvta_tipo_origen,
                'origen_fecha': date.today().strftime(self._truck_date_format),
                'estado_origen': 'GEN',
                'ruta_archivo': '',
                'tipo_proceso': 'A'
            }           
        )        
        return 

    def _create_lvdet_registry_local(self, message, payload):
        self.lvdet_message = message
        # self.lvdet_payload = base64.b64encode(payload)
        self.lvdet_sync_date = date.today().strftime(self._truck_date_format)
        self.lvdet_sync = True


    def _create_lvdet_tax(self, rec):
        return {
                    'razon_social_comercial': self.partner_id.id,
                    'periodo_anio': self.date.year,
                    'periodo_mes': self.date.month,
                    'tipo_operacion': str(self._truck_operation),
                    'tipo_origen': str(self._truck_origen),
                    'tipo_de_documento': self.l10n_latam_document_type_id_code,
                    'numero_de_documento': self.l10n_latam_document_number,
                    'codigo_de_impuesto': rec.tax_line_id.l10n_cl_sii_code,
                    'tasa_del_impuesto': rec.tax_line_id.amount,
                    'monto_del_impuesto': rec.price_total,
                    'numero_interno': rec.id
                }

    def _create_lvdet_registry(self):
        impuestos = []
        iva = {}
        
        cabecera = self.env['salebook.header'].search(
            [
                ('razon_social_comercial', '=', self.company_id.lvta_razon_social_comercial),
                ('periodo_anio', '=', self.date.year),
                ('periodo_mes', '=', self.date.month),
                ('tipo_operacion', '=', self.company_id.lvta_tipo_operacion)
            ]
        )

        origen = self.env['salebook.origin'].search(
            [
                ('razon_social_comercial', '=', self.company_id.lvta_razon_social_comercial),
                ('periodo_anio', '=', self.date.year),
                ('periodo_mes', '=', self.date.month),
                ('tipo_operacion', '=', self.company_id.lvta_tipo_operacion),
                ('tipo_origen', '=', self.company_id.lvta_tipo_origen)
            ]
        )

        if cabecera.id is False and origen.id is False:
            cabecera_api = self._get_lvdet_monthly_header_api(self.date.month, self.date.year)
            origen_api = self._get_lvdet_monthly_origin_api(self.date.month, self.date.year)
            self._create_lvdet_monthly_header_local()
            self._create_lvdet_monthly_origin_local()

        for rec in self.l10n_latam_tax_ids:
            if rec.tax_line_id.description == 'IVA':
                iva = rec
            impuestos.append(self._create_lvdet_tax(rec))

        data_final = self._lvdet_sync_registry_data(impuestos, iva)

        respuesta = self._create_lvdet_registry_api(data_final)

        if respuesta:
            self._create_lvdet_registry_local(respuesta['respuesta'], data_final)

    def _api_client_create_lvdet(self):
        return True

    def _api_client(self, method, headers, data, url):
        respuesta = ''
        if method == 'PUT':
            _logger.info('PUT')
            respuesta = requests.put(url,headers=headers,data=data)
        if method == 'POST':
            _logger.info('PUT')
            respuesta = requests.put(url,headers=headers,data=data)
        if method == 'DEL':
            _logger.info('PUT')
            respuesta = requests.delete(url,headers=headers,data=data)                        
        return respuesta

    def action_pos(self, values):
        self.lvdet_sync_registry()
        return super(AccountMove, self).write(values)



