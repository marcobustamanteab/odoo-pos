from odoo import fields, models, api


class IntegrationAccounting(models.Model):
    _inherit = 'account.account'
    _name = "integration.account.account"
    _description = "Record for Online Stock Consult"

    external_account_1 = fields.Integer('Account PeopleSoft', groups='base.group_user', help='Cuenta PeopleSoft',
                                     required=True, translate=True)
    external_account_2 = fields.Integer('Account SAP', groups='base.group_user', help='Cuenta SAP', required=True,
                                     translate=True)
    int_description = fields.Char(string='Account Description', required=True, translate=True)
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
    ind_ceco = fields.Boolean(string="ind_ceco", help="Used in")
    ind_cebe = fields.Boolean(string="ind_cebe", help="Used in")
    ind_ref = fields.Char(string="ind_ref", help="Used in")
    ind_ref2 = fields.Char(string="ind_ref 2", help="Used in")
    ind_ref3 = fields.Char(string="ind_ref 3", help="Used in")
    sap_asig = fields.Boolean(string="sap_asig", help="Used in")
    ind_soc_glfil = fields.Boolean(string="ind_soc_glfil", help="Used in")
    pep_element = fields.Boolean(string="elemento_pep", help="Used in")
    ind_art_sku = fields.Boolean(string="ind_art_sku", help="Used in")
    ind_date_value = fields.Boolean(string="ind_fecha_valor", help="Used in")

