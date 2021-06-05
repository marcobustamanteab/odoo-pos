# Copyright (C) 2020 Open Source Integrators
# Copyright (C) 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from simplejson.errors import JSONDecodeError
import json
import logging
import requests
from odoo import fields, models, _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class BackendAcp(models.Model):
    _inherit = "backend.acp"

    #connection_type = fields.Selection(selection_add=[("esb", "ESB")])
    connection_type = fields.Selection(
        [("nd", "Not defined"),("esb", "ESB")],

        default="nd",
        required="True",
        ondelete="set default",
    )
    client_id = fields.Char(string="Client ID")
    client_secret = fields.Char()
    esb_auth_endpoint = fields.Char('ESB Auth Endpoint')
    esb_auth_grant_type = fields.Char(
        'ESB Auth grant_type',
        default='client_credentials')

    def _build_url(self, endpoint):
        """
        Method build url for ESB.
        URL should not end with a '/'
        Endpoint should begin with an '/'
        """
        url = self.host
        if self.port:
            url = '%s:%d' % (url, self.port)
        if endpoint:
            url = url + endpoint
        return url

    def _generate_access_token(self):
        """To Generate access token."""
        self.ensure_one()
        url_path = self._build_url(self.esb_auth_endpoint)
        headers = {
            'Authorization': (
                self.client_secret and 'Basic ' + self.client_secret or ''),
        }
        data = {
            'grant_type': self.esb_auth_grant_type,
            'username': self.user or '',
            'password': self.password or '',
            'client_id': self.client_id or '',
        }
        response = requests.post(
            url_path,
            data=data,
            headers=headers)
        token = False
        if response.status_code == 200:
            response_data = json.loads(response.text)
            token = response_data.get('access_token')
        return token

    def action_confirm(self):
        if self.connection_type == "esb":
            # If TEST Dont Ask for Token 
            if self.prod_environment:
                token = self._generate_access_token()
                if self.esb_auth_endpoint and not token:
                    raise ValidationError(_(
                        "Connection failed. Could not get an authorization token."
                        " Please check your configuration settings."))
        return super().action_confirm()

    def api_esb_call(self, verb, esb_api_endpoint,
                     payload_dict=None,
                     headers_add=None,
                     token=None, error=True):
        """
        verb = GET or POST or PUT or PATCH or DELETE
        esb_api_endpoint = API endpoint
        payload_dict = Data
        token = Token value
        """
        url_path = self._build_url(esb_api_endpoint)

        if not token and self.prod_environment:
            token = self._generate_access_token() or ""
        headers = {
            # TODO
            # 'authorization': 'Bearer ' + token,
            # 'client_id': self.client_id or '',
            # 'LEGADO': 'ODOO',
            # 'ID_MENSAJE': str(uuid.uuid4()).replace('-', ''),
            'content-type': "application/json" if verb != "GET" else '',
            'Accept': "application/json",
        }
        if headers_add:
            headers.update(headers_add)
        payload = None
        if payload_dict:
            # Sanitize strings from single quotes
            for k, v in payload_dict.items():
                if type(v) is str and "'" in v:
                    payload_dict[k] = str(v).replace("'", "")
            payload = str(payload_dict).replace("'", '"')

        _logger.debug("Call %s %s: %s", url_path, verb, payload)
        response = requests.request(
            verb,
            url_path,
            data=payload or '',
            headers=headers)
        _logger.debug(
            "Response %s: %s",
            response.status_code, response.text)

        try:
            res = response.json()
        except JSONDecodeError:
            res = {}
        error_msg = None
        if (response.status_code in (404, 500) or
                res.get("Fault") or
                res.get("status") == "nook"):
            error_msg = _(
                "ESB call failed with Status %s.\n\n"
                "Request:\n%s %s\n%s\n\n"
                "Response:\n%s"
                ) % (
                response.status_code,
                verb, url_path, payload or payload_dict or '',
                response.text)
            _logger.error(error_msg)
            if error:
                raise ValidationError(error_msg)
        return res
