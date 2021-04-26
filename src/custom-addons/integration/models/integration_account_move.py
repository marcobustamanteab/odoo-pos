from odoo import fields, models


class IntegrationAccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'integration account move'

    integration_line_ids = fields.One2many('integration.account.move.line', 'parent_id', string='Lines')


class IntegrationAccountMoveLine(models.Model):
    _name = 'integration.account.move.line'
    _description = 'integration account move'

    parent_id = fields.Many2one('account.move')
    response_status = fields.Boolean('status')
    response_description = fields.Char('resultado_sap')
    response_payload = fields.Binary('json_payload')
    response_date_sync = fields.Date('fecha_trx')
    response_id_trx = fields.Char('id_sap_trx')

   # @api.model
   # def _get_account_configuration(self):
   #      self.env[]

    def get_account_move_line_custom(self, movement):
        result = {}
        result.header = self._get_account_move_line_header(movement)
        type_account = movement.account_id.type_account
        if type_account == 'D':
            result.debtor = self._get_account_move_line_debtor(movement)
        elif type_account == 'K':
            result.creditor = self._get_account_move_line_creditor(movement)
        else:
            result.mayor = self._get_account_move_line_mayor(movement)
        result.vendor = self._get_account_move_line_vendor(movement)
        result.currency_amount = self._get_account_move_line_currency_amount(movement)
        result.criteria = self._get_account_move_line_criteria(movement)
        return result

    def _get_account_move_line_header(self, movement):
        header = {
                "T_DOCUMENTOS": {
                    "CABECERA": {
                        "ID_DOCUMENTO": "%s" % movement.name,
                        "USERNAME": "KDCPEREZ",
                        "HEADER_TXT": "Asiento12221922",
                        "COMP_CODE": "A050",
                        "DOC_DATE": "%s" % movement.date.strftime("%Y%m%d"),
                        "PSTNG_DATE": "%s" % movement.date.strftime("%Y%m%d"),
                        "DOC_TYPE": "IA",
                        "REF_DOC_NO": "%s" % movement.payment_reference,
                        "TRANS_DATE": " "
                    }}}
        return header
# class_account = integration_accounting.class_account
# type_account = integration_accounting.type_account
# ind_ceco = integration_accounting.ind_ceco
# ind_cebe = integration_accounting.ind_cebe

    def _get_account_move_line_creditor(self, journal_line):
        creditor = {}
        for lines in journal_line:
            creditor += {
                "ACREEDOR": [
                    {
                        "ITEMNO_ACC": "%s" % lines.partner_id.id,
                        "VENDOR_NO": "%s" % lines.partner_id.vat,
                        "SP_GL_IND": "",
                        "SGTXT": "",
                        "REF_KEY_1": "",
                        "REF_KEY_2": "",
                        "REF_KEY_3": "",
                        "BUS_AREA": "",
                        "BP_GEBER": "",
                        "PMNTTRMS": "",
                        "BLINE_DATE": "",
                        "PMNT_BLOCK": "",
                        "ALLOC_NMBR": "%s" % lines.account_id.sap_asig if lines.partner_id.vat else '',
                        "ALT_PAYEE": "",
                        "PROFIT_CTR": "A50B899200",
                        "PYMT_CUR": "",
                        "PYMT_AMT": ""
                    }
                ]}
        return creditor

    def _get_account_move_line_vendor(self, journal_line):
        vendor = {}
        for lines in journal_line:
            vendor = {
            "CREACION_VENDOR": [
                {
                    "PAIS": "%s" % lines.partner_id.country,
                    "RUT": "%s" % lines.partner_id.vat,
                    "NOMBRE_1": "%s" % lines.partner_id.name,
                    "NOMBRE_2": "%s" % lines.partner_id.name,
                    "COD_BUSQUEDA": "%s" % lines.partner_id.vat,
                    "DIRECCION": "%s" % lines.partner_id.address,
                    "CALLE": "Arauco 1025, Santiago",
                    "NUMERO": "7700, 6",
                    "CIUDAD": "%s" % lines.partner_id.city,
                    "COMUNA": "LAS CONDES",
                    "REGION": "13",
                    "SOCIEDAD": "%s" % lines.partner_id.company_id.name,
                    "CTA_ASOCIADA": "2102030011",
                    "GRUPO_TESORERIA": "KPN",
                    "VIA_PAGO": "V",
                    "CONDICION_PAGO": "Z000",
                    "ID_CUENTA_BANCARIA": "",
                    "PAIS_BANCO": "",
                    "CLAVE_BANCO": "",
                    "CUENTA_BANCARIA": ""
                }
            ]}
        return vendor

    def _get_account_move_line_debtor(self, journal_line):
        debtor = {}
        for lines in journal_line:
            debtor += {
            "DEUDOR": [
                {
                    "ITEMNO_ACC": "0",
                    "CUSTOMER": " ",
                    "SP_GL_IND": " ",
                    "SGTXT": " ",
                    "PMNTTRMS": " ",
                    "PYMT_METH": " ",
                    "C_CTR_AREA": " ",
                    "TAX_CODE": " ",
                    "PROFIT_CTR": " ",
                    "BLINE_DATE": " ",
                    "PMNT_BLOCK": " ",
                    "REF_KEY_1": " ",
                    "REF_KEY_2": " ",
                    "REF_KEY_3": " ",
                    "ALT_PAYEE": " ",
                    "ALLOC_NMBR": "%s" % lines.account_id.sap_asig if lines.partner_id.vat else '',
                }
            ]}
        return debtor

    def _get_account_move_line_mayor(self, journal_line):
        mayor = {}
        for lines in journal_line:
            mayor += {
            "CUENTADEMAYOR": [
                {
                    "ITEMNO_ACC": "2",
                    "HKONT": "%s" % lines.account_id.name,
                    "SGTXT": "",
                    "VALUE_DATE": " ",
                    "ALLOC_NMBR": "%s" % lines.account_id.sap_asig if lines.partner_id.vat else '',
                    "COSTCENTER": "",
                    "TAX_CODE": "",
                    "BUS_AREA": "",
                    "PLANT": "",
                    "MATERIAL": "",
                    "FUNC_AREA": "",
                    "FIS_PERIOD": "0",
                    "FISC_YEAR": "0",
                    "ALLOC_NMBR_2": "%s" % lines.account_id.sap_asig if lines.partner_id.vat else '',
                    "PROFIT_CTR": "A50B899200",
                    "WBS_ELEMENT": "",
                    "ORDERID": "",
                    "ASSET_NO": "",
                    "SALES_ORD": "",
                    "S_ORD_ITEM": "0",
                    "DISTR_CHAN": "",
                    "DIVISION": "",
                    "SALESORG": "",
                    "SALES_GRP": "",
                    "SALES_OFF": "",
                    "SOLD_TO": "",
                    "SEGMENT": "",
                    "REF_KEY_1": "",
                    "REF_KEY_2": "",
                    "REF_KEY_3": "",
                    "TRADE_ID": ""
                }
            ]}
        return mayor

    def _get_account_move_line_currency_amount(self, journal_line):
        currency_amount = {}
        for lines in journal_line:
            currency_amount += {
                "CURRENCYAMOUNT": [
                    {
                        "ITEMNO_ACC": "1",
                        "CURR_TYPE": "0",
                        "CURRENCY": "%s" % lines.currency_id.name,
                        "CURRENCY_ISO": "0",
                        "AMT_DOCCUR": "%s" % lines.debit,
                        "AMT_BASE": "0",
                        "EXCH_RATE": ".00000"
                    },
                    {
                        "ITEMNO_ACC": "2",
                        "CURR_TYPE": "0",
                        "CURRENCY": "%s" % lines.currency_id.name,
                        "CURRENCY_ISO": "0",
                        "AMT_DOCCUR": "%s" % lines.amount_currency,
                        "AMT_BASE": "0",
                        "EXCH_RATE": ".00000"
                    }
                ]}
        return currency_amount

    def _get_account_move_line_criteria(self, journal_line):
        criteria = {}
        for lines in journal_line:
            criteria += {
                "CRITERIA": [
                    {
                        "ITEMNO_ACC": "0",
                        "FIELDNAME": " ",
                        "CHARACTER": " ",
                        "PROD_NO_LONG": " "
                    }
                ]}
        return criteria



