from datetime import date
import requests
import logging
import json
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class SaleBookOrigin(models.Model):
    _name = 'salebook.origin'
    _description = 'SaleBook Origin'

    razon_social_comercial = fields.Integer(
        string='razon_social')
    periodo_anio = fields.Integer(
        string='periodo año')
    periodo_mes = fields.Integer(
        string='periodo mes')
    tipo_operacion = fields.Char(
        string='tipo operacion')
    tipo_origen = fields.Char(
        string='tipo origen')
    origen_fecha = fields.Date(
        string='codigo estado')
    estado_origen = fields.Char(
        string='codigo estado')
    ruta_archivo = fields.Char(
        string='codigo estado')
    tipo_proceso = fields.Char(
        string='codigo estado')

    