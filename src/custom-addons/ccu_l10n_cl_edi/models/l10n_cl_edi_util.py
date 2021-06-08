# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import collections
import hashlib
import logging
import re
import textwrap
import urllib3

from functools import wraps
from html import unescape

from lxml import etree
from OpenSSL import crypto
from urllib3.exceptions import NewConnectionError
from requests.exceptions import ConnectionError, HTTPError

from zeep import Client, Settings
from zeep.exceptions import TransportError

from odoo import _, models, fields
from odoo.exceptions import UserError
from odoo.tools import xml_utils

_logger = logging.getLogger(__name__)

MAX_RETRIES = 20


def l10n_cl_edi_retry(max_retries=MAX_RETRIES, logger=None, custom_msg=None):
    """
    This custom decorator allows to manage retries during connection request to SII.
    This is needed because Zeep library cannot manage the parsing of HTML format responses
    that sometimes are delivered by SII instead of XML format.
    """

    def deco_retry(func):
        @wraps(func)
        def wrapper_retry(self, *args):
            retries = max_retries
            while retries > 0:
                try:
                    return func(self, *args)
                except (TransportError, NewConnectionError, HTTPError, ConnectionError) as error:
                    if custom_msg is not None:
                        logger.error(custom_msg)
                    if logger is not None:
                        logger.error(error)
                    retries -= 1
                except Exception as error:
                    self._report_connection_err(error)
                    logger.error(error)
                    break
            msg = _('- It was not possible to get a seed after %s retries.') % max_retries
            if custom_msg is not None:
                msg = custom_msg + msg
            self._report_connection_err(msg)

        return wrapper_retry

    return deco_retry


class L10nClEdiUtilMixin(models.AbstractModel):
    _name = 'l10n_cl.edi.util'
    _description = 'Utility Methods for Chilean Electronic Invoicing'

    config = None

    @l10n_cl_edi_retry(logger=_logger)
    def _ccu_get_seed_ws(self, mode):
        return self.config.l10n_cl_dte_voucher_service_provider.url + '/boleta.electronica.semilla'

    def _ccu_get_seed(self, mode):
        """
        Request the seed needed to authenticate to the SII with a Digital Certificate
        """
        response = self._ccu_get_seed_ws(mode)
        if response is None:
            self._report_connection_err(_('Token cannot be generated. Please try again'))
            return False
        print(["SEED", response.encode('utf-8')])
        response_parsed = etree.fromstring(response.encode('utf-8'))
        status = response_parsed.xpath('//ESTADO')[0].text
        if status == '-1':
            self._report_connection_err(_('Error Get Seed: (Message Exception)'))
            return False
        if status == '-2':
            self._report_connection_err(_('Error Get Seed: Retorno'))
            return False
        return response_parsed.xpath('//SEMILLA')[0].text

    def _ccu_get_token(self, mode, digital_signature):
        if self.config.l10n_cl_use_last_token:
            if digital_signature.last_token:
                return digital_signature.last_token
        seed = self._ccu_get_seed(mode)
        if not seed:
            return self._connection_exception('exception', _('No possible to get a seed'))
        signed_token = self._get_signed_token(digital_signature, seed)
        response = self._get_token_ws(mode, etree.tostring(
            etree.fromstring(signed_token), pretty_print=True, encoding='ISO-8859-1').decode())
        try:
            response_parsed = etree.fromstring(response.encode('utf-8'))
        except (ValueError, AttributeError) as error:
            return self._connection_exception('exception', error)
        status = response_parsed.findtext('{http://www.sii.cl/XMLSchema}RESP_HDR/ESTADO')
        if status is None or status in ['-07', '12', '11']:
            error = (_('No response trying to get a token') if status is None else
                     response_parsed.findtext('{http://www.sii.cl/XMLSchema}RESP_HDR/GLOSA'))
            return self._connection_exception(status, error)
        digital_signature.last_token = response_parsed[0][0].text
        return response_parsed[0][0].text

    def _ccu_send_xml_to_sii(self, mode, company_website, company_vat, file_name, xml_message, digital_signature,
                             post='/cgi_dte/UPL/DTEUpload'):
        """
        The header used here is explicitly stated as is, in SII documentation. See
        http://www.sii.cl/factura_electronica/factura_mercado/envio.pdf
        it says: as mentioned previously, the client program must include in the request header the following.....
        """
        config = self.env['fiscal.dte.config.settings'].search([('company_id', '=', self.company_id.id)])
        self.config = config
        if not config:
            raise UserError('Fiscal DTE Config. Settings not found, Company: %s' % (self.company_id.name))
        token = self._ccu_get_token(mode, digital_signature)
        if token is None:
            self._report_connection_err(_('No response trying to get a token'))
            return False
        return None

    #     url = SERVER_VOUCHER_URL[mode].replace('/DTEWS/', '')
    #     headers = {
    #         'Accept': 'image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, application/vnd.ms-powerpoint, \
    # application/ms-excel, application/msword, */*',
    #         'Accept-Language': 'es-cl',
    #         'Accept-Encoding': 'gzip, deflate',
    #         'User-Agent': 'Mozilla/4.0 (compatible; PROG 1.0; Windows NT 5.0; YComp 5.0.2.4)',
    #         'Referer': '{}'.format(company_website),
    #         'Connection': 'Keep-Alive',
    #         'Cache-Control': 'no-cache',
    #         'Cookie': 'TOKEN={}'.format(token),
    #     }
    #     params = collections.OrderedDict({
    #         'rutSender': digital_signature.subject_serial_number[:8],
    #         'dvSender': digital_signature.subject_serial_number[-1],
    #         'rutCompany': self._l10n_cl_format_vat(company_vat)[:8],
    #         'dvCompany': self._l10n_cl_format_vat(company_vat)[-1],
    #         'archivo': (file_name, xml_message, 'text/xml'),
    #     })
    #     multi = urllib3.filepost.encode_multipart_formdata(params)
    #     headers.update({'Content-Length': '{}'.format(len(multi[0]))})
    #     try:
    #         response = pool.request_encode_body('POST', url + post, params, headers)
    #     except Exception as error:
    #         self._report_connection_err(_('Sending DTE to SII failed due to:') + '<br /> %s' % error)
    #         digital_signature.last_token = False
    #         return False
    #     return response.data


        # we tried to use requests. The problem is that we need the Content-Lenght and seems that requests
        # had the ability to send this provided the file is in binary mode, but did not work.
        # response = requests._post(url + post, headers=headers, files=params)
        # if response.status_code != 200:
        #     response.raise_for_status()
        # else:
        #     return response.text
