from odoo import models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def create(self, vals):
        if vals.get('pricelist_id',None):
            pricelist = self.env['product.pricelist'].browse(vals['pricelist_id'])
            if pricelist and pricelist.invoice_default_tnc:
                tncs = []
                if vals.get('note',''):
                    tncs.append(vals.get('note',''))
                tncs.append(pricelist.invoice_default_tnc)
                vals['note'] = "\n".join(tncs)
        return super(PosOrder, self).create(vals)

    def _prepare_invoice_vals(self):
        vals = super(PosOrder, self)._prepare_invoice_vals()
        config = self.env['fiscal.dte.printing.config'].search([('company_id', '=', self.company_id.id)])
        if config:
            if self.partner_id and self.partner_id.l10n_cl_sii_taxpayer_type == '3':
                vals['l10n_latam_document_type_id'] = config.voucher_document_type.id
        return vals