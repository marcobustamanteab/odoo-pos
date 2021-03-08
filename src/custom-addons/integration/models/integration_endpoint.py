# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IntegrationEndPoint(models.Model):
    _name = 'integration.endpoint'
    _description = 'Integration Endpoint Definition'

    host = fields.Char("Host")
    port = fields.Integer("Port")
    name = fields.Char("Name")
