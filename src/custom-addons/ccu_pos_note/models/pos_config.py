# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import base64
import json
import logging

_logger = logging.getLogger(__name__)


class pos_config(models.Model):
    _inherit = "pos.config"

    order_note = fields.Boolean(string='Nota en Orden', default=1)
    orderline_note = fields.Boolean(string='Nota en linea de Boleta', default=False)
    print_notes = fields.Boolean(string='Imprimir Nota de Boleta', default=1)
