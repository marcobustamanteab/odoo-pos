# -*- coding: utf-8 -*-
import json
import sys
from base64 import b64encode
from urllib.parse import urlencode

import requests

from odoo import models, fields, api
from odoo.exceptions import UserError
import urllib3

class IntegrationRequest(models.Model):
    _name = 'integration.request'
    _description = 'Integration Endpoint Definition'

    CT_JSON = 'application/json'
    CT_XML = 'application/xml'
    PM_FIELDS = 'fields'
    PM_QUERY = 'query'
    AT_NONE = 'none'
    AT_BASIC = 'basic'

    name = fields.Char("Name", required=True)
    endpoint_id = fields.Many2one("integration.endpoint", "Endpoint")
    endpoint_host = fields.Char("Host", store=True, related="endpoint_id.host")
    endpoint_port = fields.Integer("Port", store=True, related="endpoint_id.port")
    resource = fields.Char("Resource")
    url = fields.Char("URL")
    method = fields.Selection(
        [
            ("GET", "GET"),
            ("POST", "POST"),
        ], string="Method", default="GET")
    payload = fields.Text("Body")
    params_mode = fields.Selection(
        [
            (PM_FIELDS,'Parameters as Fields'),
            (PM_QUERY,'Parameters as Query'),
        ],string="Parameter Mode", default=PM_FIELDS)
    content_type = fields.Selection(
        [
            (CT_JSON,'JSON'),
            (CT_XML,"XML")
        ], string="Content Type", default=CT_JSON)
    string_content = fields.Boolean("Content as String")
    auth_type = fields.Selection(
        [
            (AT_NONE,"No Auth"),
            (AT_BASIC, "Basic Auth"),
        ],string="Authentication Type")
    username = fields.Char("Username")
    password = fields.Char("Password")
    response = fields.Text("Response")
    test_mode = fields.Boolean("Test Mode")
    no_empty_objects = fields.Boolean("Do No Send Empty Objects")


    @api.onchange('endpoint_id','resource','endpoint_host','endpoint_port')
    def _calculate_url(self):
        self.url = "%s:%s/%s" %(self.endpoint_host, self.endpoint_port, self.resource.strip("/") if self.resource else "")

    def action_perform_request(self, **kwargs):
        """
        Esta acción ejecuta la consulta http con todos los parámetros pasadon argumentos 'kwargs'

        :param kwargs:  header:     diccionario, conteniendo los valores {key:value} de encabezado
                        urivalues:  recibe los parametros de la consulta GET y los pasa a nivel de la URL luego de un ?
                        params:     diccionario, Si el tipo de envio de parametros es 'fields' los envia como diccionario en la consulta,
                                    sino lo hace como argumentos de query luego de ? en la URL. Si el tipo de envio es como URL se agregan
                                    separados por / al final de la URL
                        body:       string, envia la carga (payload) de datos del request, si el tipo de contenido esta definido como json hace una
                                    conversion del diccionario recibido y lo manda como application/json
                        formdata:   diccionario, recibo los campos como un formulario de la forma {key:value}

        :return: HTTPResponse object
        """

        http = urllib3.PoolManager()
        finalurl = self.url

        # URI PARAM VALUES
        urivalues = kwargs.get("urivalues", [])
        if urivalues:
            finalurl = finalurl + "/" + "/".join(urivalues)
        # PREPARE HEADERS
        headers = kwargs.get("header", {})
        if self.content_type == self.CT_JSON:
            headers["Content-Type"] = self.CT_JSON
        # PREPARE QUERY PARAMS
        pre_params = kwargs.get("params", {})
        fields = {}
        if self.params_mode == self.PM_FIELDS:
            fields = pre_params
        elif self.params_mode == self.PM_QUERY:
            encoded_args = urlencode(pre_params)
            finalurl = finalurl + "?" + encoded_args
        # PREPARE BODY
        pre_payload = kwargs.get("body", "")
        payload = {}
        if pre_payload:
            if self.content_type == self.CT_JSON:
                if not self.string_content:
                    payload = json.dumps(pre_payload).encode('utf-8')
                else:
                    payload = str(pre_payload)
            else:   #normaly XML
                payload = pre_payload
        # PREPARE FORM DATA
        formdata = kwargs.get("formdata", {})
        # PREPARE AUTH
        if self.auth_type == self.AT_BASIC:
            headers.update(urllib3.make_headers(basic_auth='%s:%s' % (self.username, self.password)))
        # PREPARE OTHERS
        response = None
        try:
            if not self.test_mode:
                print("#####")
                print(["URL REQUEST", finalurl])
                print(["METHOD", self.method])
                request_args = {}
                if self.no_empty_objects:
                    if headers:
                        print(["HEADERS", headers])
                        request_args["headers"] = headers
                    if payload:
                        print(["BODY", payload])
                        request_args["body"] = payload
                    if formdata:
                        print(["FIELDS", fields])
                        request_args["fields"] = formdata
                else:
                    print(["HEADERS", headers])
                    print(["BODY", payload])
                    print(["FIELDS", fields])
                    request_args["headers"] = headers
                    request_args["body"] = payload
                    request_args["fields"] = formdata
                print("#####")
                response = http.request(self.method,finalurl,**request_args)
                print(["RESPONSE", response, type(response)])
                print("#####")
            else:
                response = "Test Mode"
            if response:
                if not self.test_mode:
                    self.response = response
                else:
                    self.response = json.dumps({"Mode":"Test"})
                new_log = self.env['integration.request.log']
                if not self.test_mode:
                    log = new_log.create_log(self.id, response, response.data)
                else:
                    log = new_log.create_log(self.id, response, response)
        except Exception as exception:
            new_log = self.env['integration.request.log']
            vars = {}
            vars["request_id"] = self.id
            tb = sys.exc_info()[2]
            vars["result"] = str(exception.with_traceback(tb))
            log = new_log.create(vars)
            # raise exception
        print(["REQUEST_RESPONSE", type(response)])
        return response

class IntegrationRequestLog(models.Model):
    _name = "integration.request.log"
    _description = "Results of Requests"
    _order = "create_date DESC"

    request_id = fields.Many2one("integration.request", string="Request Id")
    http_response = fields.Char("Http Response")
    response = fields.Text("Response")
    result = fields.Text("Result")
    short_result = fields.Char("Short Result", compute="_compute_short_result")
    count = fields.Integer("Count", default=1)

    @api.model
    def create_log(self, request_id, response, result ):
        # print(["params", request_id, response, result])
        new_log = self.env[self._name]
        vars = {}
        vars["request_id"] = request_id
        if response:
            if hasattr(response, "status"):
                vars["http_response"] = response.status
            vars["response"] = response
        vars["result"] = result
        new_log.create(vars)

    def _compute_short_result(self):
        for record in self:
            record.short_result = "%s ..." %(record.result[:300])