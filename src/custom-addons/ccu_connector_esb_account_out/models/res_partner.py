from odoo import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cost_center_code = fields.Char(string='Cost Center Code', index=True)
    sap_code = fields.Char(string='SAP Client Code', index=True)
    use_generic_sap_client = fields.Boolean(string='Use generic SAP Client')
    generic_sap_code = fields.Char(string='Generic SAP Code')
    generic_RUT = fields.Char(string='Generic SAP RUT')
