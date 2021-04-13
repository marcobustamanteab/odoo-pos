import models

from . import fields, models

class integration_accounting(models.Model):
    _inherit = 'account.account'

    CUENTA_PS = fields.Integer('Account PeopleSoft',
                    groups='base.group_user',
                    states={'lost': [('readonly', True)]},
                    help='Total book page count', company_dependent=False)
    CUENTA_SAP = fields.Integer('Account SAP',
                    groups='base.group_user',
                    states={'lost': [('readonly', True)]},
                    help='Total book page count', company_dependent=False)
    SAP_DESCR20 = fields.Char(string='Account Description', required=True, translate=True)
    CLASE_CTA = fields.Selection(
                    [('X', 'X'),
                    ('P', 'P')],
                    'State', default="draft")
    SAP_TP_CTA = fields.Selection(
                    [('A', 'A'),
                     ('D', 'D'),
                     ('K', 'K'),
                     ('P', 'P'),
                     ('S', 'S')],
                    'State', default="draft")
    IND_CECO = fields.Boolean(string="Bring Accounts Balance Forward", help="Used in")
    IND_CEBE = fields.Boolean(string="Bring Accounts Balance Forward", help="Used in")
    IND_REF = fields.Char(string="Bring Accounts Balance Forward", help="Used in")
    IND_REF2 = fields.Char(string="Bring Accounts Balance Forward", help="Used in")
    IND_REF3 = fields.Char(string="Bring Accounts Balance Forward", help="Used in")
    SAP_ASIG = fields.Boolean(string="Bring Accounts Balance Forward", help="Used in")
    IND_SOC_GLFIL = fields.Boolean(string="Bring Accounts Balance Forward", help="Used in")
    ELEMENTO_PEP = fields.Boolean(string="Bring Accounts Balance Forward", help="Used in")
    IND_ART_SKU = fields.Boolean(string="Bring Accounts Balance Forward", help="Used in")
    IND_FECHA_VALOR = fields.Boolean(string="Bring Accounts Balance Forward", help="Used in")

