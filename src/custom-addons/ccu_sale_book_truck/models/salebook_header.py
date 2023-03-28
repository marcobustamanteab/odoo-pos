from datetime import date
import requests
import logging
import json
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class SaleBookHeader(models.Model):
    _name = 'salebook.header'
    _description = 'SaleBook Header'

    razon_social_comercial = fields.Integer(
        string='razon_social')
    periodo_anio = fields.Integer(
        string='periodo año')
    periodo_mes = fields.Integer(
        string='periodo mes')
    tipo_operacion = fields.Char(
        string='tipo operacion')
    flag_carga_truck = fields.Char(
        string='flag_carga_truck')
    flag_carga_peoplesoft = fields.Char(
        string='flag_carga_peoplesoft')
    flag_carga_vyd = fields.Char(
        string='flag_carga_vyd')
    codigo_de_estado = fields.Char(
        string='codigo estado')
    fecha_envio_sii = fields.Date(
        string='fecha envio sii')
    flag_carga_odoo = fields.Char(
        string='flag_carga_odoo')
    origen_5 = fields.Char(
        string='origen 5')
    origen_6 = fields.Char(
        string='origen 6')
    origen_7 = fields.Char(
        string='origen 7')
    origen_8 = fields.Char(
        string='origen 8')


