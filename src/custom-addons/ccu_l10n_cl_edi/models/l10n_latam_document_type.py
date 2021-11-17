from odoo import api, models, fields

class L10nLatamDocumentType(models.Model):
    _inherit = 'l10n_latam.document.type'

    print_pdf417 = fields.Boolean("Print PDF417")