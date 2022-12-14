from datetime import date
import requests
import logging
import json
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = ['res.company']

    lvta_tipo_operacion = fields.Char(
        string='Tipo Operacion',
        default='Venta')
    lvta_tipo_origen = fields.Char(
        string='Tipo Origen')

