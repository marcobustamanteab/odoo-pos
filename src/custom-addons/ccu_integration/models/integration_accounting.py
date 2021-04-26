from odoo import fields, models, api


class IntegrationAccounting(models.Model):
    _inherit = 'account.account'
    _description = "Record for Online Stock Consult"

    external_account_1 = fields.Integer('Account PeopleSoft')
    external_account_2 = fields.Integer('Account SAP')
    int_description = fields.Char('Account Description')
    class_account = fields.Selection(
                    [('X', 'X'),
                    ('P', 'P')],
                    'State')
    type_account = fields.Selection(
                    [('A', 'A'),
                     ('D', 'D'),
                     ('K', 'K'),
                     ('P', 'P'),
                     ('S', 'S')],
                    'State')
    ind_ceco = fields.Boolean('ind_ceco')
    ind_cebe = fields.Boolean('ind_cebe')
    ind_ref = fields.Char('ind_ref')
    ind_ref2 = fields.Char('ind_ref_2')
    ind_ref3 = fields.Char('ind_ref_3')
    sap_asig = fields.Boolean('sap_asig')
    ind_soc_glfil = fields.Boolean('ind_soc_glfil')
    pep_element = fields.Boolean('elemento_pep')
    ind_art_sku = fields.Boolean('ind_art_sku')
    ind_date_value = fields.Boolean('ind_fecha_valor')


