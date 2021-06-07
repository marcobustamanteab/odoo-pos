from odoo import fields, api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    dte_send_status = fields.Selection(
        [
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('accepted', 'Accepted'),
            ('error', 'Error')
        ], string="DTE Status", default='pending'
    )

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        config = self.env["dte.client.config"]
        dte_to_send = {
            "CLIENT": {
                "client-vat-company": "CL%s" %(self.company_id.vat)
            },
            "INVOICE": {
                "company_id": "CL91041000-8",
                "invoice_date": "%s" %(self.date_invoice),
                "partner_id": "CL%s" %(self.partner_id.vat),
                "type": "out_invoice",
                "name": self.name,
                "journal_id": "INV"
            },
            "PARTNER": {
                "name": "Nombre del Contacto",
                "vat": "CL11111111-1",
                "street": "Simon Jara 112",
                "activity_description": "CONSUMIDOR",
                "phone": "986 608039",
                "email": "martinsalcedo.py@gmail.com",
                "country_id": "CL"
            },
            "DETAIL": [
                {
                    "product_id": "000001",
                    "quantity": "1",
                    "price_unit": 5000,
                    "name": "000001",
                    "account_id": "410201",
                    "display_type": "product",
                    "discount": "4.5",
                    "invoice_line_tax_ids": "14V,17V"
                }
            ],
            "PRODUCT": [
                {
                    "default_code": "000001",
                    "name": "Producto 000001",
                    "type": "product",
                    "description": "Internal Note"
                },
                {
                    "default_code": "000002",
                    "name": "Producto 000002",
                    "type": "product",
                    "description": "Internal Note"
                }
            ]
        }
        return res
