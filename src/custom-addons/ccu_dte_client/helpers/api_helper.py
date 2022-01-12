import json
import requests
from requests.auth import HTTPBasicAuth
from odoo import http

class ApiHelper(object):
    def __init__(self, company_id):
        self.config = http.request.env["dte.client.config"].search(
            [
                ('company_id', "=", company_id)
            ]
        )

    def _get_oauth2_token(self):
        oauth2_token_url = self.config.oauth2_url
        oauth2_user = self.config.oauth2_user
        oauth2_pass = self.config.oauth2_pass
        basic_auth_user = self.config.oauth2_basic_user
        basic_auth_pass = self.config.oauth2_basic_pass
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
        'grant_type': 'password',
        'username': oauth2_user,
        'password': oauth2_pass
        }

        response = requests.post(oauth2_token_url, auth=HTTPBasicAuth(basic_auth_user, basic_auth_pass), headers=headers, data=data, verify=False)
        return json.loads(response.content)['access_token']
    
    def get(self, url, headers, data, oauth2_required=False):
        if oauth2_required:
            oauth2_token = self._get_oauth2_token()
            headers["Authorization"] = f'Bearer {oauth2_token}'
        return requests.request("GET", url, headers=headers, data=data, verify=False)

    def post(self, url, headers, data, oauth2_required=False):
        if oauth2_required:
            oauth2_token = self._get_oauth2_token()
            headers["Authorization"] = f'Bearer {oauth2_token}'
        return requests.request("POST", url, headers=headers, data=data, verify=False)