import base64
from html import unescape

from lxml import etree
from odoo import models, api, _, fields
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    departure_address = fields.Char("Departure Address")
    departure_city = fields.Char("Departure City")
    departure_state = fields.Char("Departure State")

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        config = self.env['fiscal.dte.printing.config'].search([('company_id', '=', self.company_id.id)])
        if not config:
            raise UserError(_("Configuration for DTE Printing Format Not Found, Company: %s " % self.company_id.name))
        if config and self.move_type in self.get_invoice_types() and self.journal_id.type == 'sale':
            if self.partner_id and self.partner_id.l10n_cl_sii_taxpayer_type == '3':
                self.l10n_latam_document_type_id = config.voucher_document_type.id

    def _is_doc_type_voucher(self):
        res = False
        if self.l10n_latam_document_type_id.code in ['35', '39', '906', '45', '46', '70', '71']:
            res = True
        for ref_rec in self.l10n_cl_reference_ids:
            found = False
            if ref_rec.l10n_cl_reference_doc_type_selection == '39' and not found:
                res = True
                found = True
            if ref_rec.l10n_cl_reference_doc_type_selection == '61' and not found:
                origin_doc = self.env['account.move'].search([]).filtered(
                    lambda inv: inv.l10n_latam_document_number == ref_rec.origin_doc_number)
                for ref_orig_rec in origin_doc:
                    if ref_orig_rec and ref_orig_rec.l10n_latam_document_type_id.code == '39' and not found:
                        res = True
                        found = True
        return res

    # CCU REDEFINED

    def _l10n_cl_create_dte(self):
        if self._is_doc_type_voucher():
            self._ccu_l10n_cl_create_dte()
        else:
            super(AccountMove, self)._l10n_cl_create_dte()

    def _l10n_cl_create_dte_envelope(self, receiver_rut='60803000-K'):
        if self._is_doc_type_voucher():
            dte_signed, file_name = self._ccu_l10n_cl_create_dte_envelope(receiver_rut)
        else:
            dte_signed, file_name = super(AccountMove, self)._l10n_cl_create_dte_envelope(receiver_rut)
        return dte_signed, file_name

    def l10n_cl_send_dte_to_sii(self, retry_send=True):
        if self._is_doc_type_voucher():
            self.ccu_l10n_cl_send_dte_to_sii(retry_send)
        else:
            super(AccountMove, self).l10n_cl_send_dte_to_sii(retry_send)

    # CCU METHODS
    def _ccu_l10n_cl_create_dte(self):
        folio = int(self.l10n_latam_document_number)
        doc_id_number = 'B{}T{}'.format(folio, self.l10n_latam_document_type_id.code)
        dte_barcode_xml = self._l10n_cl_get_dte_barcode_xml()
        self.l10n_cl_sii_barcode = dte_barcode_xml['barcode']
        dte = self.env.ref('l10n_cl_edi.dte_template')._render({
            'move': self,
            'format_vat': self._l10n_cl_format_vat,
            'get_cl_current_strftime': self._get_cl_current_strftime,
            'format_length': self._format_length,
            'doc_id': doc_id_number,
            'caf': self.l10n_latam_document_type_id._get_caf_file(self.company_id.id,
                                                                  int(self.l10n_latam_document_number)),
            'amounts': self._l10n_cl_get_amounts(),
            'withholdings': self._l10n_cl_get_withholdings(),
            'dte': dte_barcode_xml['ted'],
        })
        dte = unescape(dte.decode('utf-8')).replace(r'&', '&amp;')
        digital_signature = self.company_id._get_digital_signature(user_id=self.env.user.id)
        signed_dte = self._sign_full_xml(
            dte, digital_signature, doc_id_number, 'doc', self.l10n_latam_document_type_id._is_doc_type_voucher())
        dte_attachment = self.env['ir.attachment'].create({
            'name': 'DTE_{}.xml'.format(self.name),
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
            'datas': base64.b64encode(signed_dte.encode('ISO-8859-1'))
        })
        self.l10n_cl_dte_file = dte_attachment.id

    def _ccu_l10n_cl_create_dte_envelope(self, receiver_rut='60803000-K'):
        file_name = 'B{}T{}.xml'.format(self.l10n_latam_document_number, self.l10n_latam_document_type_id.code)
        digital_signature = self.company_id._get_digital_signature(user_id=self.env.user.id)
        template = self.l10n_latam_document_type_id._is_doc_type_voucher() and self.env.ref(
            'l10n_cl_edi.envio_boleta') or self.env.ref('l10n_cl_edi.envio_dte')
        dte_rendered = template._render({
            'move': self,
            'RutEmisor': self._l10n_cl_format_vat(self.company_id.vat),
            'RutEnvia': digital_signature.subject_serial_number,
            'RutReceptor': receiver_rut,
            'FchResol': self.company_id.l10n_cl_dte_resolution_date,
            'NroResol': self.company_id.l10n_cl_dte_resolution_number,
            'TmstFirmaEnv': self._get_cl_current_strftime(),
            'dte': base64.b64decode(self.l10n_cl_dte_file.datas).decode('ISO-8859-1')
        })
        dte_rendered = unescape(dte_rendered.decode('utf-8')).replace('<?xml version="1.0" encoding="ISO-8859-1" ?>',
                                                                      '')
        dte_signed = self._sign_full_xml(
            dte_rendered, digital_signature, 'SetDoc',
            self.l10n_latam_document_type_id._is_doc_type_voucher() and 'bol' or 'env',
            self.l10n_latam_document_type_id._is_doc_type_voucher()
        )
        return dte_signed, file_name

    def ccu_l10n_cl_send_dte_to_sii(self, retry_send=True):
        """
        Send the DTE to the SII. It will be
        """
        # INVOICE SERVER
        if self.company_id.l10n_cl_dte_voucher_service_provider == self.company_id.INVOICE_SERVER:
            digital_signature = self.company_id._get_digital_signature(user_id=self.env.user.id)
            response = self._send_xml_to_sii(
                self.company_id.l10n_cl_dte_service_provider,
                self.company_id.website,
                self.company_id.vat,
                self.l10n_cl_sii_send_file.name,
                base64.b64decode(self.l10n_cl_sii_send_file.datas),
                digital_signature
            )
            if not response:
                return None

            response_parsed = etree.fromstring(response)
            self.l10n_cl_sii_send_ident = response_parsed.findtext('TRACKID')
            sii_response_status = response_parsed.findtext('STATUS')
            if sii_response_status == '5':
                digital_signature.last_token = False
                _logger.error('The response status is %s. Clearing the token.' %
                              self._l10n_cl_get_sii_reception_status_message(sii_response_status))
                if retry_send:
                    _logger.info('Retrying send DTE to SII')
                    self.l10n_cl_send_dte_to_sii(retry_send=False)

                # cleans the token and keeps the l10n_cl_dte_status until new attempt to connect
                # would like to resend from here, because we cannot wait till tomorrow to attempt
                # a new send
            else:
                self.l10n_cl_dte_status = 'ask_for_status' if sii_response_status == '0' else 'rejected'
            self.message_post(
                body=_('DTE has been sent to SII with response: %s.') % self._l10n_cl_get_sii_reception_status_message(
                    sii_response_status))
        if self.company_id.l10n_cl_dte_voucher_service_provider == self.company_id.VOUCHER_SERVER:
            digital_signature = self.company_id._get_digital_signature(user_id=self.env.user.id)
            response = self._ccu_send_xml_to_sii(
                self.company_id.l10n_cl_dte_service_provider,
                self.company_id.website,
                self.company_id.vat,
                self.l10n_cl_sii_send_file.name,
                base64.b64decode(self.l10n_cl_sii_send_file.datas),
                digital_signature
            )
            if not response:
                return None

            response_parsed = etree.fromstring(response)
            self.l10n_cl_sii_send_ident = response_parsed.findtext('TRACKID')
            sii_response_status = response_parsed.findtext('STATUS')
            if sii_response_status == '5':
                digital_signature.last_token = False
                _logger.error('The response status is %s. Clearing the token.' %
                              self._l10n_cl_get_sii_reception_status_message(sii_response_status))
                if retry_send:
                    _logger.info('Retrying send DTE to SII')
                    self.l10n_cl_send_dte_to_sii(retry_send=False)

                # cleans the token and keeps the l10n_cl_dte_status until new attempt to connect
                # would like to resend from here, because we cannot wait till tomorrow to attempt
                # a new send
            else:
                self.l10n_cl_dte_status = 'ask_for_status' if sii_response_status == '0' else 'rejected'
            self.message_post(
                body=_('DTE has been sent to SII with response: %s.') % self._l10n_cl_get_sii_reception_status_message(
                    sii_response_status))

