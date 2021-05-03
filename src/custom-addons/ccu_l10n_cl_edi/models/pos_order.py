from odoo import models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def create(self, vals):
        print(["PRICELIST",vals.get('pricelist_id')])
        print(["TNC", self.pricelist_id.invoice_default_tnc])
        if vals.get('pricelist_id',None):
            pricelist = self.env['product.pricelist'].browse(vals['pricelist_id'])
            if pricelist and pricelist.invoice_default_tnc:
                tncs = []
                if vals.get('note',''):
                    tncs.append(vals.get('note',''))
                tncs.append(pricelist.invoice_default_tnc)
                vals['note'] = "\n".join(tncs)
        print(["VALS POS ORDER", vals])
        return super(PosOrder, self).create(vals)
