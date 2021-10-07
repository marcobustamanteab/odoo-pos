from odoo import api, fields, models
from odoo.exceptions import UserError
import os

class AccountInvoiceExportAttachment(models.TransientModel):
    _name = 'account.invoice.export.attachment'
    _description = 'Account Invoice Export Attachment'

    def action_export_attachment(self):
        invoices = self.env['account.invoice'].search(
            [
                ('type','=','out_invoice')
            ], order='name'
        )
        for record in invoices:
            print(["INVOICE", record.number, record.company_id.id, record.amount_total])
            attachment = self.env['ir.attachment'].search(
                [
                    ('type','=','binary'),
                    ('res_model','=','account.invoice'),
                    ('res_id','=',record.id),
                ]
            )
            if attachment:
                export_path = '/var/lib/odoo/xerox/%s' % (record.number)
                if not os.path.exists(export_path):
                    print(["CREATING FOLDER", export_path])
                    ff = os.makedirs(export_path)
                    print(ff)
            for file in attachment:
                filename = file.datas_fname.split('/')[-1] if len(file.datas_fname.split('/')) > 1 else file.datas_fname
                filename_path = '%s/%s' %(export_path, filename)
                print(["FILENAME", filename])
                if file.datas:
                    exp_file = open(filename_path, 'wb')
                    exp_file.write(file.datas)
                    exp_file.flush()
                    exp_file.close()