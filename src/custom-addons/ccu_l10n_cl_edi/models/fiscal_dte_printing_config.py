#encoding: utf-8
from odoo import fields, models, api

class FiscalDTEPrintingConfig(models.Model):
    _name = "fiscal.dte.printing.config"
    _description = "Printing Format Tax Configuration"

    name = fields.Char("Name", compute="_compute_name")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    tax_1_id = fields.Many2one('account.tax.group', string="IABA 10%")
    tax_2_id = fields.Many2one('account.tax.group', string="IABA 18%")
    tax_3_id = fields.Many2one('account.tax.group', string="ILA VIN 20.5%")
    tax_4_id = fields.Many2one('account.tax.group', string="ILA CER 20.5%")
    tax_5_id = fields.Many2one('account.tax.group', string="ILA 31%")
    tax_6_id = fields.Many2one('account.tax.group', string="IVA 19%")
    voucher_document_type = fields.Many2one('l10n_latam.document.type', string="Tipo Documento Boleta")

    def _compute_name(self):
        for rec in self:
            rec.name = rec.company_id.name + " - Config. Impuestos"