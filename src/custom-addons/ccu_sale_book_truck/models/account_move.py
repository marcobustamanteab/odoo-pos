from datetime import date
import base64
import requests
import logging
import json
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.addons.queue_job.exception import RetryableJobError

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = ['account.move']


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
    lvdet_payload_request = fields.Text(
        string='Datos Enviados'
    )
    lvdet_payload_response = fields.Text(
        string='Datos Recibidos'
    )    
    lvdet_message = fields.Char(
        string='Mensajes y comentarios'
    )

    def button_lvdet_sync_registry(self):
        self.with_delay(channel='root.account')._create_lvdet_registry()        

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
            'razon_social_comercial': self.company_id.truck_UEN_code,
            'periodo_anio': anio,
            'periodo_mes': mes,
            'tipo_operacion': self.company_id.lvta_tipo_operacion
        }

    def _get_lvdet_monthly_origin_api_data(self, mes, anio):
        return {
            'razon_social_comercial': self.company_id.truck_UEN_code,
            'periodo_anio': anio,
            'periodo_mes': mes,
            'tipo_operacion': self.company_id.lvta_tipo_operacion,
            'tipo_origen': self.company_id.lvta_tipo_origen
        }

    def _get_lvdet_monthly_registry_api_data(self, mes, anio, tipo_doc, num_doc):
        return {
            'razon_social_comercial': self.company_id.truck_UEN_code,
            'periodo_anio': anio,
            'periodo_mes': mes,
            'tipo_operacion': self.company_id.lvta_tipo_operacion,
            'tipo_origen': self.company_id.lvta_tipo_origen,
            'tipo_de_documento': tipo_doc,
            'numero_de_documento': num_doc
        }

    def _create_lvdet_monthly_header_api_data(self, mes, anio):
        return {
            'razon_social_comercial': self.company_id.truck_UEN_code,
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
            'razon_social_comercial': self.company_id.truck_UEN_code,
            'periodo_anio': anio,
            'periodo_mes': mes,
            'tipo_operacion': self.company_id.lvta_tipo_operacion,
            'tipo_operacion': self.company_id.lvta_tipo_origen,
            'origen_fecha': date.today.strftime(self._truck_date_format),
            'estado_origen': 'GEN',
            'ruta_archivo': '',
            'tipo_proceso': 'A'
        }

    def _del_lvdet_monthly_registry_api_data(self, mes, anio, tipo_doc, num_doc):
        return {
            'razon_social_comercial': self.company_id.truck_UEN_code,
            'periodo_anio': anio,
            'periodo_mes': mes,
            'tipo_operacion': self.company_id.lvta_tipo_operacion,
            'tipo_origen': self.company_id.lvta_tipo_origen,
            'tipo_de_documento': tipo_doc,
            'numero_de_documento': num_doc
        }


    #### Client Api Operation  
    #### (self, method, headers, data, url):

    def _create_lvdet_registry_api(self, payload):
        backend = self.company_id.backend_esb_id
        esb_api_endpoint = '/api/libroventas/libro/crear'
        url = backend.host + ':' + str(backend.port) + esb_api_endpoint
        # res = backend.api_esb_call("PUT", esb_api_endpoint, payload)
        headers = {
            'Content-Type': 'application/json',
        }
        res = self._api_client('PUT', headers, payload, url)
        if not res:
            msg = "LibroVenta Synchornization Service Connection Error"
            raise RetryableJobError(msg)
        _logger.info(json.dumps(res, indent=4))        
        return res

    def _get_lvdet_monthly_header_api(self, mes, anio):
        payload = self._get_lvdet_monthly_header_api_data(mes, anio)
        backend = self.company_id.backend_esb_id
        esb_api_endpoint = '/api/libroventas/cabecera/obtener'
        url = backend.host + ':' + str(backend.port) + esb_api_endpoint
        # res = backend.api_esb_call("POST", esb_api_endpoint, payload)
        headers = {
            'Content-Type': 'application/json',
        }
        res = self._api_client('POST', headers, payload, url)
        if not res:
            msg = "LibroVenta Synchornization Service Connection Error"
            raise RetryableJobError(msg)
        _logger.info(json.dumps(res, indent=4))        
        return res

    def _get_lvdet_monthly_origin_api(self, mes, anio):
        payload = self._get_lvdet_monthly_origin_api_data(mes, anio)
        backend = self.company_id.backend_esb_id
        esb_api_endpoint = '/api/libroventas/origen/obtener'
        url = backend.host + ':' + str(backend.port) + esb_api_endpoint
        _logger.info(json.dumps(payload, indent=4)) 
        # res = backend.api_esb_call("POST", esb_api_endpoint, payload)
        headers = {
            'Content-Type': 'application/json',
        }

        res = self._api_client('POST', headers, payload, url)
        if not res:
            msg = "LibroVenta Synchornization Service Connection Error"
            raise RetryableJobError(msg)
        _logger.info(json.dumps(res, indent=4))        
        return res


    def _del_lvdet_monthly_registry_api(self, mes, anio, tipo_doc, num_doc):
        payload = self._del_lvdet_monthly_registry_api_data(mes, anio, tipo_doc, num_doc)
        backend = self.company_id.backend_esb_id
        esb_api_endpoint = '/api/libroventas/libro/eliminar'
        url = backend.host + ':' + str(backend.port) + esb_api_endpoint
        _logger.info(json.dumps(payload, indent=4)) 
        # res = backend.api_esb_call("POST", esb_api_endpoint, payload)
        headers = {
            'Content-Type': 'application/json',
        }
        res = self._api_client('DEL', headers, payload, url)
        if not res:
            msg = "LibroVenta Synchornization Service Connection Error"
            raise RetryableJobError(msg)
        _logger.info(json.dumps(res, indent=4))        
        return res

    def _get_lvdet_monthly_registry_api(self, mes, anio, tipo_doc, num_doc):
        payload = self._get_lvdet_monthly_registry_api_data(mes, anio, tipo_doc, num_doc)
        backend = self.company_id.backend_esb_id
        esb_api_endpoint = '/api/libroventas/libro/obtener'
        url = backend.host + ':' + str(backend.port) + esb_api_endpoint
        _logger.info(json.dumps(payload, indent=4)) 
        # res = backend.api_esb_call("POST", esb_api_endpoint, payload)
        headers = {
            'Content-Type': 'application/json',
        }
        res = self._api_client('POST', headers, payload, url)
        if not res:
            msg = "LibroVenta Synchornization Service Connection Error"
            raise RetryableJobError(msg)
        _logger.info(json.dumps(res, indent=4))        
        return res

    def _lvdet_sync_registry_data(self, impuestos, iva):
        registro = None
        header = {
                    'razon_social_comercial': self.company_id.truck_UEN_code,
                    'periodo_anio': self.date.year,
                    'periodo_mes': self.date.month,
                    'tipo_operacion': str(self.company_id.lvta_tipo_operacion),
                    'tipo_origen': str(self.company_id.lvta_tipo_origen),
                    'tipo_de_documento': self.l10n_latam_document_type_id_code,
                    'numero_de_documento': self.l10n_latam_document_number,
                    'numero_interno': self.l10n_latam_document_number,
                    'centro_distribución': 0,
                    'mes_documento': self.date.month,
                    'dia_documento': self.date.day,
                    'fecha': date.today().strftime(self._truck_date_format),
                    'documento_anulado': '.',
                    'codigo_operación': 0,
                    'tipo_impuesto': 0,
                    'tasa_impuesto': int(iva.tax_line_id.amount),
                    'indicador_servicio': 0,
                    'indicador_sin_costo': 0,
                    'fecha_documento': self.date.strftime(self._truck_date_format),
                    'codigo_sucursal': 0,
                    'rut_documento': self.partner_id_vat.split('-')[0],
                    'dv': self.partner_id_vat.split('-')[1],
                    'razon_social': self.invoice_partner_display_name[:49],
                    'tipo_documento_referencia': 0,
                    'folio_documento_referencia': 0,
                    'monto_exento': 0,
                    'monto_neto': int(self.amount_untaxed),
                    'monto_iva': int(iva.l10n_latam_price_subtotal),
                    'monto_activo_fijo': 0,
                    'iva_uso_comun': 0,
                    'iva_fuera_de_plazo': 0,
                    'total_ley18211': 0,
                    'monto_sin_credito': 0,
                    'iva_retenido_total': 0,
                    'iva_retenido_parcial': 0,
                    'cre_dec': 0,
                    'deposito_de_envase': 0,
                    'monto_total': int(self.amount_total_signed),
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
                }
        _logger.info('largo impuestos -> %s' % (len(impuestos)))
        impuestos.pop(0)
        _logger.info('recorte largo impuestos -> %s' % (len(impuestos)))
        _logger.info(json.dumps(impuestos, indent=4))
        if len(impuestos) > 0:
            registro = {
                'registro': header                                                                                                                                                                                                                                                                                            ,
                'impuestos': impuestos
                }
        else:
            registro = {
                'registro': registro
                }                
        return registro


    def _create_lvdet_monthly_header_local(self):
        self.env['salebook.header'].write(
            {
                'razon_social_comercial': self.company_id.truck_UEN_code,
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
                'razon_social_comercial': self.company_id.truck_UEN_code,
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


    def _delete_lvdet_monthly_registry_local(self):
        self.env['salebook.origin'].write(
            {
                'razon_social_comercial': self.company_id.truck_UEN_code,
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

    def _create_lvdet_registry_local(self, message, payload_request, payload_response):
        self.lvdet_message = message
        self.lvdet_payload_request = json.dumps(payload_request, indent=4)
        self.lvdet_payload_response = json.dumps(payload_response, indent=4)
        self.lvdet_sync_date = date.today().strftime(self._truck_date_format)
        self.lvdet_sync = True

    def _delete_lvdet_registry_local(self):
        self.lvdet_message = ''
        self.lvdet_payload_request = ''
        self.lvdet_payload_response = ''
        self.lvdet_sync_date = ''
        self.lvdet_sync = False

    def _create_lvdet_tax(self, rec):
        respuesta = {}
        if rec.tax_line_id.description != 'IVA':
            respuesta = {
                    'razon_social_comercial': self.company_id.truck_UEN_code,
                    'periodo_anio': self.date.year,
                    'periodo_mes': self.date.month,
                    'tipo_operacion': str(self.company_id.lvta_tipo_operacion),
                    'tipo_origen': str(self.company_id.lvta_tipo_origen),
                    'tipo_de_documento': int(self.l10n_latam_document_type_id_code),
                    'numero_de_documento': int(self.l10n_latam_document_number),
                    'codigo_de_impuesto': rec.tax_line_id.l10n_cl_sii_code,
                    'tasa_del_impuesto': rec.tax_line_id.amount,
                    'monto_del_impuesto': int(rec.price_total),
                    'numero_interno': int(self.l10n_latam_document_number)
                }
        return respuesta

    def _create_lvdet_registry(self):
        impuestos = []
        iva = {}
        
        cabecera = self.env['salebook.header'].search(
            [
                ('razon_social_comercial', '=', self.company_id.truck_UEN_code),
                ('periodo_anio', '=', self.date.year),
                ('periodo_mes', '=', self.date.month),
                ('tipo_operacion', '=', self.company_id.lvta_tipo_operacion)
            ]
        )

        origen = self.env['salebook.origin'].search(
            [
                ('razon_social_comercial', '=', self.company_id.truck_UEN_code),
                ('periodo_anio', '=', self.date.year),
                ('periodo_mes', '=', self.date.month),
                ('tipo_operacion', '=', self.company_id.lvta_tipo_operacion),
                ('tipo_origen', '=', self.company_id.lvta_tipo_origen)
            ]
        )

        registro = self._get_lvdet_monthly_registry_api(
            self.date.month, 
            self.date.year, 
            self.l10n_latam_document_type_id_code, 
            self.l10n_latam_document_number)
        _logger.info('verificando registro previo')
        _logger.info(json.dumps(registro, indent=4))

        if registro['causa'] == 'No se hab grabado registros aun':
            cabecera_api = self._get_lvdet_monthly_header_api(self.date.month, self.date.year)
            origen_api = self._get_lvdet_monthly_origin_api(self.date.month, self.date.year)
            if not cabecera:
                _logger.info('creando cabecera')
                self._create_lvdet_monthly_header_local()
            if not origen:
                _logger.info('creando origen')
                self._create_lvdet_monthly_origin_local()
            if cabecera_api['cabeceras']['cabecera']['codigo_de_estado'] != 'AB':
                msg = "LibroVenta cerrado, no se pueden modificar los datos"
                raise RetryableJobError(msg) 
            if origen_api['origenes']['origen']['tipo_proceso'] != 'A':
                msg = "LibroVenta esta configurado para carga manual, no automatica"
                raise RetryableJobError(msg)   

            for rec in self.l10n_latam_tax_ids:
                if rec.tax_line_id.description == 'IVA':
                    iva = rec
                impuestos.append(self._create_lvdet_tax(rec))

            data_final = self._lvdet_sync_registry_data(impuestos, iva)
            respuesta = self._create_lvdet_registry_api(data_final)
            _logger.info('respuesta registro')
            _logger.info(respuesta)
            if respuesta['respuesta'] == 'Creacion Exitosa de Registros':
                self._create_lvdet_registry_local(respuesta['respuesta'], data_final, respuesta)
            else:
                msg = "Error en api LibroVenta %s - detalle -> %s" % (respuesta['respuesta'], json.dumps(respuesta, indent=4))
                raise RetryableJobError(msg)             
        else:
            self._create_lvdet_registry_local('Respuesta confirmada por consulta', registro, 'Data confirmada por consulta directa')


    def _api_client_create_lvdet(self):
        return True

    def _api_client(self, method, headers, data, url):
        respuesta = ''
        _logger.info('antes de cliente')
        _logger.info(data)
        _logger.info(url)
        if method == 'PUT':
            _logger.info('PUT')
            respuesta = requests.put(url,headers=headers,json=data)
        if method == 'POST':
            _logger.info('POST')
            respuesta = requests.post(url,headers=headers,json=data)
        if method == 'DEL':
            _logger.info('DEL')
            respuesta = requests.delete(url,headers=headers,json=data)     
        _logger.info(respuesta)                   
        return respuesta.json()

        # res = backend.api_esb_call("POST", esb_api_endpoint, payload)
        # if not res:
        #     msg = "ESB Synchornization Service Connection Error"
        #     raise RetryableJobError(msg)

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        for rec in self:
            rec.with_delay(channel='root.account').lvdet_sync_registry()
        return res

    def delete_registry(self):
        self._delete_registry_queue()


    def _delete_registry_queue(self):
        _logger.info('Encolado eliminacion registro')
        self.with_delay(channel='root.account')._delete_registry_process()

    def _delete_registry_process(self):
        _logger.info('Inicio eliminacion registro')
        respuesta = self._del_lvdet_monthly_registry_api(
            self.date.year,
            self.date.month,
            self.l10n_latam_document_type_id_code,
            self.l10n_latam_document_number
        )
        _logger.info('respuesta registro')
        _logger.info(respuesta)
        if respuesta['respuesta'] == 'Eliminacion Exitosa de Registros':
            self._delete_lvdet_registry_local()
        else:
            msg = "Error en api LibroVenta %s - detalle -> %s" % (respuesta['respuesta'], json.dumps(respuesta, indent=4))
            raise RetryableJobError(msg)
